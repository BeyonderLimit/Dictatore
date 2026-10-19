"""Voice activity detection.

VOSK hallucinates filler words ("the", "a") when breath and background
noise are fed to it, so recognition is gated: audio only reaches the
recognizer while speech is detected (plus a small pre-roll and tail so
word onsets and endings are not clipped).

Backends:
    webrtc — Google's WebRTC VAD (via the optional webrtcvad package)
    rms    — energy-based fallback, pure Python, no dependencies
    off    — no gating; every chunk is fed to VOSK
"""
from __future__ import annotations

import math
import struct
from abc import ABC, abstractmethod
from collections import deque

SAMPLE_RATE = 16000


def rms(chunk: bytes) -> float:
    if len(chunk) < 2:
        return 0.0
    count = len(chunk) // 2
    samples = struct.unpack(f"<{count}h", chunk[: count * 2])
    return math.sqrt(sum(s * s for s in samples) / len(samples))


class VAD(ABC):
    @abstractmethod
    def is_speech(self, chunk: bytes) -> bool:
        ...


class RmsVad(VAD):
    """Energy gate: speech if the chunk's RMS exceeds a fixed threshold."""

    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def is_speech(self, chunk: bytes) -> bool:
        return rms(chunk) >= self._threshold


class WebrtcVad(VAD):
    """WebRTC VAD: majority vote over exact 30 ms frames.

    Accepts arbitrary chunk sizes and internally splits them into the
    10/20/30 ms frames the model requires (30 ms = 960 bytes @16 kHz s16
    mono). Trailing bytes that do not fill a frame are ignored — at 30 ms
    granularity they never carry decision-relevant energy.
    """

    _FRAME_BYTES = 2 * (SAMPLE_RATE // 1000) * 30  # s16 mono, 30 ms

    def __init__(self, aggressiveness: int = 2) -> None:
        import webrtcvad

        self._vad = webrtcvad.Vad(aggressiveness)

    def is_speech(self, chunk: bytes) -> bool:
        step = self._FRAME_BYTES
        frames = [chunk[i : i + step] for i in range(0, len(chunk) - step + 1, step)]
        if not frames:
            return False
        voiced = sum(
            self._vad.is_speech(frame, SAMPLE_RATE) for frame in frames
        )
        return voiced * 2 > len(frames)


def get_vad(
    name: str,
    rms_threshold: float = 3000,
    aggressiveness: int = 2,
) -> VAD:
    """Create a VAD backend. `webrtc` falls back to `rms` with a warning
    when the webrtcvad package is not installed."""
    if name == "off":
        raise ValueError("VAD backend must not be 'off'; call sites handle that")
    if name == "webrtc":
        try:
            return WebrtcVad(aggressiveness)
        except ImportError:
            import sys

            print(
                "VAD: webrtcvad not installed, using RMS fallback "
                "(pip install webrtcvad-wheels to enable webrtc VAD)",
                file=sys.stderr,
            )
            name = "rms"
    if name == "rms":
        return RmsVad(rms_threshold)
    raise ValueError(f"Unknown VAD backend: {name}")


class SpeechGate:
    """Passes speech audio (with pre-roll and a hangover tail) through a VAD.

    process() consumes one recorder chunk and returns the byte chunks that
    should be sent to the recognizer:
      - before speech: chunks are buffered as pre-roll; on the first voiced
        chunk the buffer is flushed so the start of the word is intact,
      - after speech stops: a hangover tail keeps feeding briefly so word
        endings are not clipped,
      - after the hangover expires: chunks are dropped (breath, room noise)
        and the VOSK never sees them.
    """

    def __init__(
        self,
        vad: VAD,
        preroll_ms: int = 200,
        hangover_ms: int = 400,
        sample_rate: int = SAMPLE_RATE,
    ) -> None:
        self._vad = vad
        preroll_bytes = sample_rate * 2 * preroll_ms // 1000  # s16 mono
        self._preroll: deque[bytes] = deque(maxlen=max(preroll_bytes, 1))
        hangover_bytes = sample_rate * 2 * hangover_ms // 1000
        self._hangover_bytes = max(hangover_bytes, 1)
        self._remaining_hangover = 0
        self._in_speech = False

    def process(self, chunk: bytes) -> tuple[list[bytes], bool]:
        """Return (chunks_to_feed, was_speech) for this chunk."""
        if self._vad.is_speech(chunk):
            out = [chunk]
            if not self._in_speech:
                out = [*self._preroll, chunk]
                self._preroll.clear()
                self._in_speech = True
            self._remaining_hangover = self._hangover_bytes
            return out, True

        if not self._in_speech:
            self._preroll.append(chunk)
            return [], False

        if self._remaining_hangover > 0:
            self._remaining_hangover -= len(chunk)
            return [chunk], False

        # Hangover expired without any new voiced chunk.
        self._in_speech = False
        self._preroll.append(chunk)
        return [], False

    def reset(self) -> None:
        self._preroll.clear()
        self._remaining_hangover = 0
        self._in_speech = False
