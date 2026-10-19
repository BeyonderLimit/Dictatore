import sys
import types

import pytest

from dictatore.vad import RmsVad, SpeechGate, VAD, WebrtcVad, get_vad, rms

SILENCE = b"\x00\x00" * 1024
LOUD = (b"\xd3\x30" + b"\x2d\xcf") * 512  # ±12499 alternating -> RMS ~9500


def test_rms_zero_for_silence():
    assert rms(SILENCE) == 0.0


def test_rms_positive_for_tone():
    assert rms(LOUD) > 8000


def test_rms_vad_threshold():
    low = RmsVad(threshold=3000)
    assert low.is_speech(SILENCE) is False
    assert low.is_speech(LOUD) is True


def test_get_vad_unknown_backend():
    with pytest.raises(ValueError):
        get_vad("sox")


def test_get_vad_webrtc_falls_back_to_rms(monkeypatch):
    monkeypatch.setitem(sys.modules, "webrtcvad", None)  # simulates being absent
    vad = get_vad("webrtc", rms_threshold=3000)
    assert isinstance(vad, RmsVad)


def test_get_vad_webrtc_uses_package(monkeypatch):
    calls = []

    class FakeVad:
        def __init__(self, aggressiveness):
            calls.append(aggressiveness)

        def is_speech(self, frame, rate):
            assert len(frame) == 960  # 30 ms @16 kHz, s16 mono
            assert rate == 16000
            return int.from_bytes(frame[:2], "little", signed=True) != 0

    fake = types.ModuleType("webrtcvad")
    fake.Vad = FakeVad
    monkeypatch.setitem(sys.modules, "webrtcvad", fake)

    vad = get_vad("webrtc", aggressiveness=2)
    assert isinstance(vad, WebrtcVad)
    # 3 frames: voiced, silent, voiced -> majority voiced
    chunk = (b"\xff\x7f" * 480) + (b"\x00\x00" * 480) + (b"\xff\x7f" * 480)
    assert vad.is_speech(chunk) is True
    # 2 of 3 silent -> not speech
    chunk = (b"\x00\x00" * 480) + (b"\x00\x00" * 480) + (b"\xff\x7f" * 480)
    assert vad.is_speech(chunk) is False
    assert calls == [2]


class _ScriptedVAD(VAD):
    """VAD that yields scripted per-chunk decisions."""

    def __init__(self, decisions):
        self._decisions = list(decisions)

    def is_speech(self, chunk):
        if not self._decisions:
            return False
        return self._decisions.pop(0)


def test_gate_drops_silence_before_speech():
    gate = SpeechGate(_ScriptedVAD([False, False, True]), preroll_ms=1, hangover_ms=1)
    assert gate.process(SILENCE) == ([], False)
    assert gate.process(SILENCE) == ([], False)


def test_gate_flushes_preroll_on_speech_onset():
    gate = SpeechGate(_ScriptedVAD([False, True]), preroll_ms=256, hangover_ms=1)
    quieter = b"\x01\x00" * 1024
    assert gate.process(quieter) == ([], False)  # buffered as pre-roll
    chunks, is_speech = gate.process(SILENCE)
    # flushes the buffered chunk then the voiced chunk
    assert chunks == [quieter, SILENCE]
    assert is_speech is True


def test_gate_hangover_feeds_tail_then_drops():
    gate = SpeechGate(
        _ScriptedVAD([True, False, False, False]), preroll_ms=1, hangover_ms=8
    )  # 8 ms = 512 bytes hangover budget
    chunks, is_speech = gate.process(SILENCE)
    assert (chunks, is_speech) == ([SILENCE], True)
    # one 2048-byte chunk exhausts the 512-byte hangover budget
    assert gate.process(SILENCE) == ([SILENCE], False)
    # after hangover expires, silence is dropped again
    assert gate.process(SILENCE) == ([], False)


def test_gate_hangover_survives_incomplete_chunks():
    gate = SpeechGate(
        _ScriptedVAD([True, False, False, False, False]), preroll_ms=1, hangover_ms=8
    )  # 8 ms = 512 bytes hangover budget
    gate.process(SILENCE)
    # small 128-byte chunks: budget of 256 covers exactly two of them
    small = b"\x00\x00" * 64  # 128 bytes
    assert gate.process(small) == ([small], False)
    assert gate.process(small) == ([small], False)
    # budget exhausted
    assert gate.process(small) == ([], False)


def test_gate_reset_after_speech():
    gate = SpeechGate(_ScriptedVAD([True, False]), preroll_ms=1, hangover_ms=1)
    gate.process(SILENCE)
    gate.reset()
    assert gate.process(SILENCE) == ([], False)
