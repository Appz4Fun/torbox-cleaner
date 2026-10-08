import os
import stat

import pytest

from torbox_cleaner import cli, config
from torbox_cleaner.config import (
    SETTINGS_URL,
    is_valid_api_key,
    read_masked,
    run_setup,
    write_env_key,
)

GOOD = "3f2c8a1e-9b7d-4c5e-a1f0-6d2b9e8c7a41"
GOOD2 = "0b8e5c2d-1a4f-4e6b-9c3d-7f2a1e0d5b98"


@pytest.mark.parametrize("key", [GOOD, GOOD.upper(), "00000000-0000-4000-8000-000000000000", GOOD2])
def test_valid_keys(key):
    assert is_valid_api_key(key)


@pytest.mark.parametrize(
    "key",
    [
        "",
        "not-a-key",
        "3f2c8a1e9b7d4c5ea1f06d2b9e8c7a41",  # no hyphens
        "{3f2c8a1e-9b7d-4c5e-a1f0-6d2b9e8c7a41}",  # braces
        "3f2c8a1e-9b7d-1c5e-a1f0-6d2b9e8c7a41",  # version 1
        "3f2c8a1e-9b7d-4c5e-c1f0-6d2b9e8c7a41",  # variant 2 (Microsoft)
        "3f2c8a1e-9b7d-4c5e-71f0-6d2b9e8c7a41",  # variant 0 (NCS)
        "3f2c8a1e-9b7d-4c5e-a1f0-6d2b9e8c7a4",  # too short
        "3f2c8a1e-9b7d-4c5e-a1f0-6d2b9e8c7a41x",  # too long
        "3f2c8a1g-9b7d-4c5e-a1f0-6d2b9e8c7a41",  # non-hex
        " " + GOOD,
    ],
)
def test_invalid_keys(key):
    assert not is_valid_api_key(key)


def test_write_env_creates_file_0600(tmp_path):
    env = tmp_path / "sub" / ".env"
    write_env_key(env, GOOD)
    assert env.read_text() == f"TORBOX_API_KEY={GOOD}\n"
    assert stat.S_IMODE(env.stat().st_mode) == 0o600


def test_write_env_replaces_existing_and_keeps_other_lines(tmp_path):
    env = tmp_path / ".env"
    env.write_text(f"# mine\nFOO=bar\nexport TORBOX_API_KEY={GOOD}\nBAZ=1\nTORBOX_API_KEY=dupe\n")
    write_env_key(env, GOOD2)
    assert env.read_text() == f"# mine\nFOO=bar\nTORBOX_API_KEY={GOOD2}\nBAZ=1\n"


def test_write_env_appends_when_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("FOO=bar")
    write_env_key(env, GOOD)
    assert env.read_text() == f"FOO=bar\nTORBOX_API_KEY={GOOD}\n"


def test_write_env_does_not_touch_similar_keys(tmp_path):
    env = tmp_path / ".env"
    env.write_text("TORBOX_API_KEY_OLD=x\n")
    write_env_key(env, GOOD)
    assert env.read_text() == f"TORBOX_API_KEY_OLD=x\nTORBOX_API_KEY={GOOD}\n"


def _feed(chars):
    it = iter(chars)
    out = []
    return (lambda: next(it, "")), out.append, out


def test_read_masked_echoes_stars():
    getch, write, out = _feed("abc\r")
    assert read_masked(getch, write) == "abc"
    assert "".join(out) == "***\r\n"


def test_read_masked_backspace_ctrl_u_and_escapes():
    getch, write, _ = _feed("ab\x7fc\x15xy\x1b[Az\n")
    assert read_masked(getch, write) == "xyz"


def test_read_masked_ctrl_c():
    getch, write, _ = _feed("ab\x03")
    with pytest.raises(KeyboardInterrupt):
        read_masked(getch, write)


def test_read_masked_ctrl_d_on_empty():
    getch, write, _ = _feed("\x04")
    with pytest.raises(EOFError):
        read_masked(getch, write)


def test_run_setup_reprompts_until_valid(tmp_path, monkeypatch, capsys):
    opened = []
    monkeypatch.setattr(config.webbrowser, "open", lambda url, new=0: opened.append(url) or True)
    answers = iter(["nope", "3f2c8a1e-9b7d-1c5e-a1f0-6d2b9e8c7a41", f"  '{GOOD}'  "])
    env = tmp_path / ".env"

    assert run_setup(env, prompt=lambda _: next(answers)) == GOOD

    assert opened == [SETTINGS_URL]
    assert env.read_text() == f"TORBOX_API_KEY={GOOD}\n"
    out = capsys.readouterr().out
    assert out.count("That is not a valid TorBox API key") == 2
    assert SETTINGS_URL in out


def test_run_setup_prints_link_when_browser_unavailable(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(config.webbrowser, "open", lambda url, new=0: False)
    run_setup(tmp_path / ".env", prompt=lambda _: GOOD)
    out = capsys.readouterr().out
    assert SETTINGS_URL in out
    assert "couldn't open a browser" in out


def test_run_setup_no_browser(tmp_path, monkeypatch):
    monkeypatch.setattr(config.webbrowser, "open", lambda *a, **k: pytest.fail("browser opened"))
    run_setup(tmp_path / ".env", open_browser=False, prompt=lambda _: GOOD)


def test_project_root_detected_from_clone():
    root = config.project_root()
    assert root is not None and (root / "pyproject.toml").is_file()
    assert config.default_env_file() == root / ".env"


def test_installed_mode_uses_user_config(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "project_root", lambda: None)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert config.default_env_file() == tmp_path / "torbox-cleaner" / ".env"
    monkeypatch.delenv("XDG_CONFIG_HOME")
    assert config.default_env_file() == config.Path.home() / ".config" / "torbox-cleaner" / ".env"


def test_cli_setup_only(monkeypatch, tmp_path):
    monkeypatch.delenv("TORBOX_API_KEY", raising=False)
    monkeypatch.setattr(config, "masked_input", lambda _: GOOD)
    monkeypatch.setattr(cli, "run_setup", lambda env, open_browser: run_setup(env, open_browser=False, prompt=lambda _: GOOD))
    env = tmp_path / ".env"
    assert cli.main(["--setup", "--env-file", str(env)]) == 0
    assert env.read_text() == f"TORBOX_API_KEY={GOOD}\n"


def test_cli_missing_key_non_interactive_errors(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("TORBOX_API_KEY", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(SystemExit) as e:
        cli.main(["--delete-all", "--dry-run", "--env-file", str(tmp_path / ".env")])
    assert e.value.code == 2
    assert "--setup" in capsys.readouterr().err


def test_cli_rejects_malformed_key(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("TORBOX_API_KEY", "garbage")
    with pytest.raises(SystemExit):
        cli.main(["--delete-all", "--dry-run", "--env-file", str(tmp_path / ".env")])
    assert "not a valid TorBox API key" in capsys.readouterr().err


def test_env_var_wins_over_file(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text(f"TORBOX_API_KEY={GOOD2}\n")
    monkeypatch.setenv("TORBOX_API_KEY", GOOD)
    config.load_dotenv(env)
    assert os.environ["TORBOX_API_KEY"] == GOOD
