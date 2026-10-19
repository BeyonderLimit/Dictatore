"""Local transcript log for dictated emissions.

Every emitted utterance appends one line to a plain text file under
~/.local/share/dictatore/. Format: "<local timestamp>\t<text>\n".
Purely local: no network, no audio retention. Set TRANSCRIPT_FILE to
None or "" in the config to disable logging entirely.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from dictatore.config import TRANSCRIPT_FILE_DEFAULT


def resolve_path(value: object) -> str | None:
    """Return the expanded transcript path, or None when disabled."""
    if not value or not isinstance(value, str):
        return None
    return str(Path(value).expanduser())


def append(path: str, text: str, now: datetime | None = None) -> None:
    """Append one emission to the transcript. Never raises on OSError —
    logging must not break dictation (e.g. disk full, bad path)."""
    stamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    line = text.replace("\n", " ").strip()
    if not line:
        return
    try:
        file_path = Path(path).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(f"{stamp}\t{line}\n")
    except OSError as exc:
        import sys

        print(f"Transcript logging failed: {exc}", file=sys.stderr)
