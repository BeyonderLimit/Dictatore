import subprocess

import pytest

from dictatore.output import ClipboardOutput, StdoutOutput, get_output


def test_get_output_returns_correct_driver():
    from dictatore.output import WtypeOutput, XdotoolOutput

    assert isinstance(get_output("stdout"), StdoutOutput)
    assert isinstance(get_output("xdotool"), XdotoolOutput)
    assert isinstance(get_output("wtype"), WtypeOutput)
    assert isinstance(get_output("clipboard"), ClipboardOutput)


def test_get_output_unknown_raises():
    with pytest.raises(ValueError):
        get_output("nonexistent")


def test_stdout_output_prints_without_newline(capsys):
    StdoutOutput().emit("Hello ")
    StdoutOutput().emit("world")
    captured = capsys.readouterr()
    assert captured.out == "Hello world"


def test_clipboard_falls_back_past_missing_tools(monkeypatch, tmp_path):
    # Fake $PATH containing a real wl-copy replacement; xclip absent.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "wl-copy").write_text("#!/bin/sh\ncat > /dev/null\n")
    (fake_bin / "wl-copy").chmod(0o755)

    calls = []
    real_run = subprocess.run

    def fake_run(cmd, **kwargs):
        calls.append(cmd[0])
        if cmd[0] == "xclip":
            raise FileNotFoundError("xclip")
        return real_run(cmd, **kwargs)

    monkeypatch.setattr("dictatore.output.subprocess.run", fake_run)
    ClipboardOutput().emit("hi")
    assert calls == ["xclip", "wl-copy"]
