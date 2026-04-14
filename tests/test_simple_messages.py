import pytest

from love_bot.handlers.simple_messages import handle_message
from love_bot import config


@pytest.mark.asyncio
async def test_handle_message_from_Arina(message_mock, mocker):
    message_mock.chat.id = config.ARINA_ID
    mock_send = mocker.patch(
        "love_bot.handlers.simple_messages.safe_send_message",
    )
    await handle_message(message_mock)
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_from_me(message_mock, mocker):
    mock_write = mocker.patch(
        "love_bot.handlers.simple_messages.write_content",
    )
    await handle_message(message_mock)
    mock_write.assert_called_once()
