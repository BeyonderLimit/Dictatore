from __future__ import annotations

import re

_SINGLE_DIGITS: dict[str, int] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
}

_TENS: dict[str, int] = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}

_SCALES: dict[str, int] = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
}

_ORDINAL_MAP: dict[str, tuple[str, str]] = {
    "first": ("one", "st"), "second": ("two", "nd"), "third": ("three", "rd"),
    "fourth": ("four", "th"), "fifth": ("five", "th"), "sixth": ("six", "th"),
    "seventh": ("seven", "th"), "eighth": ("eight", "th"), "ninth": ("nine", "th"),
    "tenth": ("ten", "th"), "eleventh": ("eleven", "th"), "twelfth": ("twelve", "th"),
    "thirteenth": ("thirteen", "th"), "fourteenth": ("fourteen", "th"),
    "fifteenth": ("fifteen", "th"), "sixteenth": ("sixteen", "th"),
    "seventeenth": ("seventeen", "th"), "eighteenth": ("eighteen", "th"),
    "nineteenth": ("nineteen", "th"), "twentieth": ("twenty", "th"),
    "thirtieth": ("thirty", "th"), "fortieth": ("forty", "th"),
    "fiftieth": ("fifty", "th"), "sixtieth": ("sixty", "th"),
    "seventieth": ("seventy", "th"), "eightieth": ("eighty", "th"),
    "ninetieth": ("ninety", "th"),
    "hundredth": ("hundred", "th"), "thousandth": ("thousand", "th"),
    "millionth": ("million", "th"), "billionth": ("billion", "th"),
}

_NUMBER_WORDS: set[str] = (
    set(_SINGLE_DIGITS)
    | set(_TENS)
    | set(_SCALES)
    | set(_ORDINAL_MAP)
    | {"and"}
)


def _is_digit_series(words: list[str]) -> bool:
    return (
        len(words) >= 2
        and all(w.lower().rstrip(".,;:!?") in _SINGLE_DIGITS for w in words)
    )


def _strip_punct(w: str) -> str:
    return w.lower().rstrip(".,;:!?")


def _parse_number(words: list[str]) -> tuple[int, str] | None:
    total = 0
    current = 0
    ordinal_suffix = ""

    for raw in words:
        w = _strip_punct(raw)
        if w == "and":
            continue

        if w in _ORDINAL_MAP:
            base, suffix = _ORDINAL_MAP[w]
            ordinal_suffix = suffix
            w = base

        if w in _SINGLE_DIGITS:
            current += _SINGLE_DIGITS[w]
        elif w in _TENS:
            current += _TENS[w]
        elif w == "hundred":
            current *= 100
        elif w in _SCALES:
            scale = _SCALES[w]
            current = max(current, 1)
            total += current * scale
            current = 0
        else:
            return None

    value = total + current
    if ordinal_suffix:
        return value, f"{value:,}{ordinal_suffix}"
    return value, f"{value:,}"


def _digit_series_to_str(words: list[str]) -> str:
    return "".join(str(_SINGLE_DIGITS[_strip_punct(w)]) for w in words)


def convert_numbers(text: str) -> str:
    source_words = text.split()
    i = 0
    result_parts: list[str] = []

    while i < len(source_words):
        cluster: list[str] = []
        while i < len(source_words):
            w = _strip_punct(source_words[i])
            if w in _NUMBER_WORDS:
                cluster.append(source_words[i])
                i += 1
            else:
                break

        if not cluster:
            result_parts.append(source_words[i])
            i += 1
            continue

        if _is_digit_series(cluster):
            result_parts.append(_digit_series_to_str(cluster))
        elif len(cluster) >= 2:
            parsed = _parse_number(cluster)
            if parsed is not None:
                result_parts.append(parsed[1])
            else:
                result_parts.extend(cluster)
        else:
            w = _strip_punct(cluster[0])
            if w in _SINGLE_DIGITS:
                result_parts.append(str(_SINGLE_DIGITS[w]))
            elif w in _ORDINAL_MAP:
                base, suffix = _ORDINAL_MAP[w]
                base_val = _SINGLE_DIGITS.get(base) or _TENS.get(base) or _SCALES.get(base, 0)
                result_parts.append(f"{base_val:,}{suffix}" if suffix == "th" else f"{base_val}{suffix}")
            elif w in _TENS:
                result_parts.append(cluster[0])
            else:
                result_parts.append(cluster[0])

    return " ".join(result_parts)
