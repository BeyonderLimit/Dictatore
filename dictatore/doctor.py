from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

from dictatore.config import CONFIG_DIR, MODELS_DIR, load_config


def _check_python() -> list[str]:
    issues: list[str] = []
    if sys.version_info < (3, 11):
        issues.append(f"Python >= 3.11 required, found {sys.version_info.major}.{sys.version_info.minor}")
    return issues


def _check_vosk() -> list[str]:
    issues: list[str] = []
    try:
        import vosk
        version = getattr(vosk, "__version__", None)
        if version:
            issues.append(f"VOSK: {version}")
        else:
            issues.append("VOSK: import ok")
    except ImportError:
        issues.append("VOSK not installed (pip install vosk)")
    return issues


def _check_model() -> list[str]:
    issues: list[str] = []
    cfg, _ = load_config()
    model_name = cfg.get("MODEL", "en-us")
    model_path = MODELS_DIR / model_name

    if not model_path.is_dir():
        issues.append(
            f"Language model not found at {model_path}\n"
            f"  Download from https://alphacephei.com/vosk/models"
        )
    else:
        issues.append(f"Model: {model_path}")
    return issues


def _check_recorder(name: str) -> list[str]:
    issues: list[str] = []
    path = shutil.which(name)
    if path is None:
        issues.append(f"Recording backend '{name}' not found")
        return issues
    issues.append(f"Recorder: {path}")
    return issues


def _check_output(name: str) -> list[str]:
    issues: list[str] = []
    if name in ("stdout", "clipboard"):
        issues.append(f"Output: {name}")
        return issues
    path = shutil.which(name)
    if path is None:
        issues.append(f"Output driver '{name}' not found (install {name})")
    else:
        issues.append(f"Output: {path}")
    return issues


def _check_pipewire() -> list[str]:
    issues: list[str] = []
    result = subprocess.run(
        ["pactl", "info"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0 and "PipeWire" in result.stdout:
        issues.append("Audio server: PipeWire")
    else:
        issues.append("Audio server: not PipeWire (check PulseAudio)")
    return issues


def run() -> list[str]:
    issues: list[str] = []

    issues.extend(_check_python())
    issues.extend(_check_vosk())
    issues.extend(_check_model())
    issues.extend(_check_pipewire())

    cfg, _ = load_config()
    issues.append(f"Hotkey: {cfg.get('HOTKEY', 'Super+D')}")
    issues.extend(_check_recorder(cfg.get("RECORDER", "pw-cat")))
    issues.extend(_check_output(cfg.get("OUTPUT", "xdotool")))

    config_dir_ok = CONFIG_DIR.is_dir()
    issues.append(f"Config dir: {CONFIG_DIR} {'exists' if config_dir_ok else 'not found'}")

    return issues
