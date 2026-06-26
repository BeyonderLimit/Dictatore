from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

CONFIG_DIR = Path.home() / ".config" / "dictatore"
CONFIG_PATH = CONFIG_DIR / "config.py"
PLUGINS_DIR = CONFIG_DIR / "plugins"
MODELS_DIR = Path.home() / ".local" / "share" / "dictatore" / "models"

DEFAULT_CONFIG: dict[str, Any] = {
    "HOTKEY": "Super+D",
    "TIMEOUT": 2.5,
    "SILENCE_RMS_THRESHOLD": 3000,
    "MAX_RECORDING_SECONDS": 60,
    "ENABLE_DIGITS": True,
    "OUTPUT": "xdotool",
    "MODEL": "en-us",
    "RECORDER": "pw-cat",
    "SHOW_OVERLAY": True,
    "OVERLAY_POSITION": "top-center",
    "OVERLAY_FONT_SIZE": 14,
    "OVERLAY_OPACITY": 0.9,
    "OVERLAY_WIDTH": 60,
}


_SKIP_KEYS = frozenset({"__name__", "__doc__", "__file__", "__builtins__", "transform"})


def load_config() -> tuple[dict[str, Any], Callable[[str], str] | None]:
    cfg = dict(DEFAULT_CONFIG)
    transform: Callable[[str], str] | None = None

    if CONFIG_PATH.exists():
        spec = importlib.util.spec_from_file_location("user_config", CONFIG_PATH)
        if spec is None or spec.loader is None:
            return cfg, transform
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for key in dir(mod):
            if key in _SKIP_KEYS or key.startswith("_"):
                continue
            cfg[key] = getattr(mod, key)

        if hasattr(mod, "transform"):
            transform = getattr(mod, "transform")

    return cfg, transform


def get_model_path(model_name: str) -> Path:
    return MODELS_DIR / model_name
