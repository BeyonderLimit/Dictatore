from datetime import datetime

from dictatore import transcript
from dictatore.transcript import append, resolve_path


def test_resolve_path_expands_user():
    path = resolve_path("~/.foo/transcript.txt")
    assert path.startswith("/home/") or path.startswith("/tmp/")


def test_resolve_path_disabled_values():
    assert resolve_path("") is None
    assert resolve_path(None) is None
    assert resolve_path(True) is None  # non-string truthy ignored


def test_append_creates_file_and_parents(tmp_path):
    path = tmp_path / "sub" / "dir" / "transcript.txt"
    append(str(path), "hello world", now=datetime(2026, 1, 2, 3, 4, 5))
    content = path.read_text(encoding="utf-8")
    assert content == "2026-01-02 03:04:05\thello world\n"


def test_append_accumulates_lines(tmp_path):
    path = tmp_path / "transcript.txt"
    append(str(path), "first", now=datetime(2026, 1, 1))
    append(str(path), "second", now=datetime(2026, 1, 2))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0].endswith("\tfirst")
    assert lines[1].endswith("\tsecond")


def test_append_strips_internal_newlines(tmp_path):
    # plugins could inject newlines; transcript must stay one line per emit
    path = tmp_path / "transcript.txt"
    append(str(path), "line one\nline two", now=datetime(2026, 1, 1))
    assert path.read_text(encoding="utf-8").count("\n") == 1


def test_append_skips_blank_text(tmp_path):
    path = tmp_path / "transcript.txt"
    append(str(path), "   \n ", now=datetime(2026, 1, 1))
    assert not path.exists()


def test_append_survives_os_error(tmp_path, monkeypatch, capsys):
    # unwritable parent: logging must warn, not crash dictation
    target_dir = tmp_path / "adir"
    target_dir.write_text("")  # file, not dir -> mkdir(parents=True) will fail
    bogus = target_dir / "x" / "transcript.txt"
    append(str(bogus), "text")
    assert capsys.readouterr().err  # warning printed to stderr
    assert not bogus.exists()


def test_default_config_enables_transcript():
    from dictatore.config import DEFAULT_CONFIG

    assert DEFAULT_CONFIG["TRANSCRIPT_FILE"] == transcript.TRANSCRIPT_FILE_DEFAULT
    assert resolve_path(DEFAULT_CONFIG["TRANSCRIPT_FILE"]) is not None
