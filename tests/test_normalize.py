from dictatore.normalize import insert_punctuation, normalize


def _words(*spans):
    # spans: list of (word, start, end) tuples
    return [{"word": w, "start": s, "end": e} for w, s, e in spans]


def test_insert_punctuation_empty():
    assert insert_punctuation([]) == ""


def test_no_gap_no_punctuation():
    words = _words(("hello", 0.0, 1.0), ("world", 1.0, 2.0))
    assert insert_punctuation(words) == "hello world"


def test_medium_gap_inserts_comma():
    words = _words(("hello", 0.0, 1.0), ("world", 1.4, 2.4))  # gap 0.4
    assert insert_punctuation(words) == "hello, world"


def test_long_gap_inserts_period():
    words = _words(("hello", 0.0, 1.0), ("world", 2.0, 3.0))  # gap 1.0
    assert insert_punctuation(words) == "hello. world"


def test_normalize_collapses_whitespace_and_capitalizes():
    assert normalize("  hello   world ") == "Hello world"


def test_normalize_nfkc_and_capitalization():
    assert normalize("café") == "Café"


def test_normalize_empty_string():
    assert normalize("") == ""


def test_normalize_no_capitalize():
    assert normalize("hello world", auto_capitalize=False) == "hello world"
