import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_bot(mocker):
    bot = AsyncMock()
    mocker.patch("love_bot.config.bot", bot)
    return bot


@pytest.fixture
def message_mock():
    msg = MagicMock()
    msg.text = "test"
    msg.message_id = 1
    msg.chat.id = 123
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def state_mock():
    state = AsyncMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    return state
