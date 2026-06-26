from __future__ import annotations

import re
import unicodedata


def insert_punctuation(words: list[dict]) -> str:
    if not words:
        return ""
    parts: list[str] = []
    for i, w in enumerate(words):
        word = w["word"]
        if i > 0:
            gap = w["start"] - words[i - 1]["end"]
            if gap > 0.7:
                parts.append(".")
            elif gap > 0.3:
                parts.append(",")
        parts.append(word)
    result = " ".join(parts)
    result = re.sub(r"\s+([.,])", r"\1", result)
    return result


def normalize(text: str, auto_capitalize: bool = True) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()

    if auto_capitalize and text:
        text = text[0].upper() + text[1:]

    return text
