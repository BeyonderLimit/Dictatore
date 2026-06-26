from __future__ import annotations

import math
import struct
import sys
import threading
import time
from typing import Callable

from dictatore.cli import dispatch
from dictatore.config import get_model_path, load_config
from dictatore.normalize import normalize
from dictatore.numbers import convert_numbers
from dictatore.output import get_output
from dictatore.overlay import Overlay
from dictatore.plugins import load_plugins, run_plugins
from dictatore.recorder import get_recorder
from dictatore.recognizer import Recognizer


def _rms(chunk: bytes) -> float:
    if len(chunk) < 2:
        return 0.0
    count = len(chunk) // 2
    samples = struct.unpack(f"<{count}h", chunk[: count * 2])
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def _process_and_emit(
    raw: str,
    cfg: dict,
    transform_fn: Callable[[str], str] | None,
    output: object,
) -> None:
    text = normalize(raw, cfg.get("AUTO_CAPITALIZE", True))
    if cfg.get("ENABLE_DIGITS"):
        text = convert_numbers(text)
    if transform_fn:
        text = transform_fn(text)
    text = run_plugins(text, load_plugins())
    output.emit(text)


def _run_recording() -> None:
    cfg, transform_fn = load_config()
    model_path = get_model_path(cfg["MODEL"])

    if not model_path.is_dir():
        print(f"Error: model not found at {model_path}", file=sys.stderr)
        sys.exit(1)

    recognizer = Recognizer(str(model_path))
    recorder = get_recorder(cfg["RECORDER"])
    output = get_output(cfg["OUTPUT"])
    timeout = cfg.get("TIMEOUT", 2.5)
    threshold = cfg.get("SILENCE_RMS_THRESHOLD", 3000)
    show_overlay = cfg.get("SHOW_OVERLAY", True)

    overlay = Overlay(None, cfg)
    partial_text = ""
    finals: list[str] = []
    silence_start: float | None = None
    cooldown_until: float = 0.0
    overlay_text = ""

    def on_partial(text: str) -> None:
        nonlocal partial_text, overlay_text
        partial_text = text
        overlay_text = text
        print(f"\r\x1b[K{text}", file=sys.stderr, end="", flush=True)

    def on_final(text: str) -> None:
        nonlocal partial_text
        finals.append(text)
        partial_text = ""

    recognizer.start(partial_callback=on_partial, final_callback=on_final)

    def audio_callback(chunk: bytes) -> None:
        nonlocal partial_text, finals, silence_start, cooldown_until
        recognizer.feed(chunk)
        now = time.monotonic()
        if now < cooldown_until:
            return
        if _rms(chunk) < threshold:
            if silence_start is None:
                silence_start = now
            elif now - silence_start >= timeout:
                to_emit = " ".join(finals)
                remaining = recognizer.reset()
                if remaining:
                    to_emit = to_emit + " " + remaining if to_emit else remaining
                elif not to_emit:
                    to_emit = partial_text
                if to_emit:
                    finals.clear()
                    partial_text = ""
                    _process_and_emit(to_emit, cfg, transform_fn, output)
                    print(f"\r\x1b[K\u2192 {to_emit}", file=sys.stderr)
                    print("Listening...", file=sys.stderr, end="", flush=True)
                    overlay_text = ""
                    cooldown_until = now + 0.5
                silence_start = None
        else:
            silence_start = None

    print("Listening... (speak; pause to emit; Ctrl+C to quit)", file=sys.stderr)

    if show_overlay:
        overlay.show()

    recorder.start(callback=audio_callback)

    stop_event = threading.Event()
    try:
        while True:
            if stop_event.wait(timeout=0.1):
                break
            if show_overlay and overlay_text:
                overlay.update_text(overlay_text)
    except KeyboardInterrupt:
        recorder.stop()

    if show_overlay:
        overlay.hide()

    if partial_text and not finals:
        _process_and_emit(partial_text, cfg, transform_fn, output)

    remaining = recognizer.stop()
    if remaining and (not finals or remaining not in finals):
        _process_and_emit(remaining, cfg, transform_fn, output)


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            _print_usage()
            return
        dispatch()
        return
    _run_recording()


def _print_usage() -> None:
    print("Dictatore 2.0", file=sys.stderr)
    print(file=sys.stderr)
    print("Usage: dictatore [command]", file=sys.stderr)
    print("  (no args)   Continuous dictation — pause to emit, Ctrl+C to quit", file=sys.stderr)
    print("  doctor      Verify dependencies and installation", file=sys.stderr)
    print("  models      List installed language models", file=sys.stderr)
    print("  config      Open configuration file", file=sys.stderr)
    print("  install     Interactive setup", file=sys.stderr)
    print("  daemon      Start background daemon (Fast mode)", file=sys.stderr)
    print(file=sys.stderr)
    print("Tip: set OUTPUT=\"stdout\" in config for terminal testing", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
