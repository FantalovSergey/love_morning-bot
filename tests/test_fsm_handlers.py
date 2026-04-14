import pytest

from love_bot import config
from love_bot.handlers.fsm import write_dream


@pytest.mark.asyncio
async def test_write_dream_too_long(message_mock, state_mock, mocker):
    message_mock.text = "x" * (config.TO_BOT_MESSAGE_SYMBOL_LIMIT + 10)
    mock_send = mocker.patch("love_bot.handlers.fsm.safe_send_message")
    await write_dream(message_mock, state_mock)
    mock_send.assert_called_once()
    state_mock.clear.assert_not_called()


@pytest.mark.asyncio
async def test_write_dream_success(message_mock, state_mock, mocker):
    mock_write = mocker.patch("love_bot.handlers.fsm.write_content")
    await write_dream(message_mock, state_mock)
    mock_write.assert_called_once()
    state_mock.clear.assert_called_once()
