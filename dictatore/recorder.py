from __future__ import annotations

import subprocess
import threading
from abc import ABC, abstractmethod
from typing import Callable


AudioCallback = Callable[[bytes], None]


class Recorder(ABC):
    @abstractmethod
    def start(self, callback: AudioCallback) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...


class _SubprocessRecorder(Recorder):
    def __init__(self) -> None:
        self._process: subprocess.Popen[bytes] | None = None
        self._thread: threading.Thread | None = None
        self._stopped = False

    def _build_cmd(self) -> list[str]:
        raise NotImplementedError

    def start(self, callback: AudioCallback) -> None:
        self._stopped = False
        self._process = subprocess.Popen(
            self._build_cmd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        def _read() -> None:
            assert self._process is not None and self._process.stdout is not None
            while not self._stopped:
                chunk = self._process.stdout.read(4096)
                if not chunk:
                    break
                callback(chunk)

        self._thread = threading.Thread(target=_read, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopped = True
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            self._process = None

    def wait(self) -> None:
        if self._thread is not None:
            self._thread.join()


class PwcatRecorder(_SubprocessRecorder):
    def _build_cmd(self) -> list[str]:
        return ["pw-cat", "--record", "--format=s16", "--rate=16000", "--channels=1", "-"]


class ParecRecorder(_SubprocessRecorder):
    def _build_cmd(self) -> list[str]:
        return ["parec", "--format=s16le", "--rate=16000", "--channels=1", "--raw"]


class ArecordRecorder(_SubprocessRecorder):
    def _build_cmd(self) -> list[str]:
        return ["arecord", "-t", "raw", "-f", "S16_LE", "-r", "16000", "-c", "1"]


_RECORDER_MAP: dict[str, type[Recorder]] = {
    "pw-cat": PwcatRecorder,
    "parec": ParecRecorder,
    "arecord": ArecordRecorder,
}


def get_recorder(name: str) -> Recorder:
    cls = _RECORDER_MAP.get(name)
    if cls is None:
        raise ValueError(f"Unknown recorder backend: {name}")
    return cls()
