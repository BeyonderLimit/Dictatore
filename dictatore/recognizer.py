from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from vosk import Model, KaldiRecognizer

from dictatore.normalize import insert_punctuation


PartialCallback = Callable[[str], None]
FinalCallback = Callable[[str], None]


class Recognizer:
    def __init__(self, model_path: str | Path) -> None:
        self._model = Model(str(model_path))
        self._recognizer: KaldiRecognizer | None = None
        self._partial_cb: PartialCallback | None = None
        self._final_cb: FinalCallback | None = None

    def start(
        self,
        *,
        partial_callback: PartialCallback | None = None,
        final_callback: FinalCallback | None = None,
    ) -> None:
        self._recognizer = KaldiRecognizer(self._model, 16000)
        self._recognizer.SetWords(True)
        self._partial_cb = partial_callback
        self._final_cb = final_callback

    def feed(self, audio: bytes) -> None:
        if self._recognizer is None:
            raise RuntimeError("Recognizer not started")

        if self._recognizer.AcceptWaveform(audio):
            if self._final_cb is not None:
                result = self._recognizer.Result()
                data = json.loads(result)
                words = data.get("result", [])
                text = insert_punctuation(words) if words else data.get("text", "").strip()
                if text:
                    self._final_cb(text)
        else:
            if self._partial_cb is not None:
                partial = self._recognizer.PartialResult()
                data = json.loads(partial)
                text = data.get("partial", "").strip()
                if text:
                    self._partial_cb(text)

    def reset(self) -> str:
        if self._recognizer is None:
            return ""
        final = self._recognizer.FinalResult()
        data = json.loads(final)
        text = data.get("text", "").strip()
        self._recognizer = KaldiRecognizer(self._model, 16000)
        self._recognizer.SetWords(True)
        return text

    def stop(self) -> str:
        if self._recognizer is None:
            return ""

        final = self._recognizer.FinalResult()
        data = json.loads(final)
        text = data.get("text", "").strip()

        self._recognizer = None
        self._partial_cb = None
        self._final_cb = None

        return text
