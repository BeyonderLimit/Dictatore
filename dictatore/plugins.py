from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Callable

from dictatore.config import PLUGINS_DIR


def load_plugins() -> list[Callable[[str], str]]:
    plugins: list[Callable[[str], str]] = []

    if not PLUGINS_DIR.is_dir():
        return plugins

    for fpath in sorted(PLUGINS_DIR.iterdir()):
        if not fpath.name.endswith(".py") or fpath.name.startswith("_"):
            continue

        spec = importlib.util.spec_from_file_location(fpath.stem, fpath)
        if spec is None or spec.loader is None:
            continue

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        if hasattr(mod, "transform"):
            plugins.append(getattr(mod, "transform"))

    return plugins


def run_plugins(text: str, plugins: list[Callable[[str], str]]) -> str:
    for plugin in plugins:
        text = plugin(text)
    return text
