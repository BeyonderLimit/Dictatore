import pytest

from dictatore.recorder import (
    ArecordRecorder,
    ParecRecorder,
    PwcatRecorder,
    get_recorder,
)


def test_get_recorder_known_backends():
    assert isinstance(get_recorder("pw-cat"), PwcatRecorder)
    assert isinstance(get_recorder("parec"), ParecRecorder)
    assert isinstance(get_recorder("arecord"), ArecordRecorder)


def test_get_recorder_unknown_raises():
    with pytest.raises(ValueError, match="Unknown recorder backend"):
        get_recorder("sox")


def test_pwcat_build_cmd():
    cmd = PwcatRecorder()._build_cmd()
    assert cmd[0] == "pw-cat"
    assert "--record" in cmd
    assert "--rate=16000" in cmd


def test_parec_build_cmd():
    cmd = ParecRecorder()._build_cmd()
    assert cmd[0] == "parec"
    assert "--rate=16000" in cmd
    assert "--raw" in cmd


def test_arecord_build_cmd():
    cmd = ArecordRecorder()._build_cmd()
    assert cmd[0] == "arecord"
    assert "16000" in cmd
    assert "-t" in cmd
