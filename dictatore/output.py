from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod


class OutputDriver(ABC):
    @abstractmethod
    def emit(self, text: str) -> None:
        ...


class XdotoolOutput(OutputDriver):
    def emit(self, text: str) -> None:
        subprocess.run(
            ["xdotool", "type", "--clearmodifiers", text],
            check=False,
        )


class WtypeOutput(OutputDriver):
    def emit(self, text: str) -> None:
        subprocess.run(
            ["wtype", text],
            check=False,
        )


class StdoutOutput(OutputDriver):
    def emit(self, text: str) -> None:
        print(text, end="", flush=True)


class ClipboardOutput(OutputDriver):
    def emit(self, text: str) -> None:
        for cmd in [
            ["xclip", "-selection", "clipboard"],
            ["wl-copy"],
        ]:
            try:
                subprocess.run(cmd, input=text.encode(), check=False)
                return
            except FileNotFoundError:
                continue


_OUTPUT_MAP: dict[str, type[OutputDriver]] = {
    "xdotool": XdotoolOutput,
    "wtype": WtypeOutput,
    "stdout": StdoutOutput,
    "clipboard": ClipboardOutput,
}


def get_output(name: str) -> OutputDriver:
    cls = _OUTPUT_MAP.get(name)
    if cls is None:
        raise ValueError(f"Unknown output driver: {name}")
    return cls()
