import pytest

from love_bot import config
from love_bot.handlers.starting_operations import start_dream_writing


@pytest.mark.asyncio
async def test_start_dream_writing(message_mock, state_mock, mocker):
    message_mock.chat.id = config.ARINA_ID
    mock_send = mocker.patch(
        "love_bot.handlers.starting_operations.safe_send_message",
    )
    await start_dream_writing(message_mock, state_mock)
    mock_send.assert_called_once()
    state_mock.set_state.assert_called_once()
