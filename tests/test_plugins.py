from dictatore import plugins


def _write_plugin(path, marker):
    path.write_text(f"def transform(text):\n    return text + {marker!r}\n")


def test_plugins_loaded_and_run_in_filename_order(tmp_path, monkeypatch):
    _write_plugin(tmp_path / "01_first.py", "-first")
    _write_plugin(tmp_path / "02_second.py", "-second")
    _write_plugin(tmp_path / "not_python.txt", "-ignored")
    _write_plugin(tmp_path / "_private.py", "-private")
    monkeypatch.setattr(plugins, "PLUGINS_DIR", tmp_path)

    loaded = plugins.load_plugins()
    assert len(loaded) == 2

    result = plugins.run_plugins("text", loaded)
    assert result == "text-first-second"


def test_no_plugins_dir_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(plugins, "PLUGINS_DIR", tmp_path / "missing")
    assert plugins.load_plugins() == []


def test_plugin_without_transform_is_skipped(tmp_path, monkeypatch):
    (tmp_path / "notransform.py").write_text("value = 1\n")
    monkeypatch.setattr(plugins, "PLUGINS_DIR", tmp_path)
    assert plugins.load_plugins() == []
