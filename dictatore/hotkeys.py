from __future__ import annotations

import sys
from typing import Callable

KeyCallback = Callable[[], None]


def listen(
    *,
    on_down: KeyCallback | None = None,
    on_up: KeyCallback | None = None,
) -> None:
    hotkey = sys.argv[1] if len(sys.argv) > 1 else ""
    if not hotkey:
        import re
        import subprocess

        result = subprocess.run(
            ["xdotool", "getactivewindow"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            return
    if on_down:
        on_down()
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    if on_up:
        on_up()
