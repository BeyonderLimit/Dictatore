import textwrap

from dictatore import config


def test_defaults_applied_when_no_config_file(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "missing.py")
    cfg, transform = config.load_config()
    assert cfg["TIMEOUT"] == 2.5
    assert cfg["OUTPUT"] == "xdotool"
    assert cfg["MODEL"] == "en-us"
    assert transform is None


def test_user_config_overrides_defaults(tmp_path, monkeypatch):
    config_file = tmp_path / "config.py"
    config_file.write_text(
        textwrap.dedent(
            """
            TIMEOUT = 5.0
            OUTPUT = "stdout"
            ENABLE_DIGITS = False
            """
        )
    )
    monkeypatch.setattr(config, "CONFIG_PATH", config_file)
    cfg, _ = config.load_config()
    assert cfg["TIMEOUT"] == 5.0
    assert cfg["OUTPUT"] == "stdout"
    assert cfg["ENABLE_DIGITS"] is False
    # untouched defaults
    assert cfg["SHOW_OVERLAY"] is True


def test_transform_hook_is_loaded(tmp_path, monkeypatch):
    config_file = tmp_path / "config.py"
    config_file.write_text("def transform(text):\n    return text.upper()\n")
    monkeypatch.setattr(config, "CONFIG_PATH", config_file)
    cfg, transform = config.load_config()
    assert callable(transform)
    assert transform("hello") == "HELLO"


def test_dunder_names_not_copied_into_config(tmp_path, monkeypatch):
    config_file = tmp_path / "config.py"
    config_file.write_text('TIMEOUT = 1.0\n')
    monkeypatch.setattr(config, "CONFIG_PATH", config_file)
    cfg, _ = config.load_config()
    assert not any(k.startswith("__") for k in cfg)


def test_get_model_path_joins_models_dir():
    assert config.get_model_path("en-us") == config.MODELS_DIR / "en-us"
