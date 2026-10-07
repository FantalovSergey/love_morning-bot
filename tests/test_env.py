import pytest

from love_bot.env import get_env_vars


def test_absent_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('BOT_TOKEN', '')
    monkeypatch.setenv('MY_ID', '0')
    with pytest.raises(ValueError, match='BOT_TOKEN, MY_ID'):
        get_env_vars()


def test_Arina_and_my_ids_are_the_same(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv('ARINA_ID', '1')
    monkeypatch.setenv('MY_ID', '1')
    with pytest.raises(ValueError):
        get_env_vars()
