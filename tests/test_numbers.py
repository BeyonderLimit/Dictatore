from dictatore.numbers import convert_numbers


def test_digit_series_becomes_digit_string():
    assert convert_numbers("four five six") == "456"


def test_digit_series_with_punctuation():
    assert convert_numbers("two, three") == "23"


def test_compound_tens():
    assert convert_numbers("twenty five dollars") == "25 dollars"


def test_hundred_requires_scale_word():
    assert convert_numbers("one hundred five") == "105"


def test_thousand_scale():
    assert convert_numbers("two thousand ten") == "2,010"


def test_and_is_ignored():
    assert convert_numbers("one and twenty") == "21"


def test_single_digit_word():
    assert convert_numbers("one") == "1"


def test_single_ordinal():
    assert convert_numbers("first day") == "1st day"
    assert convert_numbers("third place") == "3rd place"


def test_no_numbers_unchanged():
    assert convert_numbers("hello world") == "hello world"


def test_sentence_with_mixed_numbers():
    assert convert_numbers("call me at four five six seven") == "call me at 4567"
