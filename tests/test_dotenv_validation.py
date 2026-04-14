import pytest

from love_bot.dotenv_validation import get_env_vars


def test_env_ok(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("ARINA_ID", "1")
    monkeypatch.setenv("MY_ID", "2")
    assert get_env_vars() == ("token", 1, 2)


def test_env_missing(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "")
    with pytest.raises(ValueError):
        get_env_vars()
