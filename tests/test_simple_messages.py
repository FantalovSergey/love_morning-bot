from unittest.mock import AsyncMock, patch

import pytest

from love_bot.handlers.simple_messages import (
    handle_message,
    send_cuteness_immediately,
    show_all_dreams,
    show_all_love_messages,
)
from love_bot import config


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.simple_messages.send_love_message",
    new_callable=AsyncMock,
)
async def test_send_cuteness(mock_send, message):
    await send_cuteness_immediately(message)

    mock_send.assert_awaited_once_with(message.message_id)


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.simple_messages.safe_send_message",
    new_callable=AsyncMock,
)
async def test_show_all_messages_for_Arina(mock_send, message):
    message.chat.id = config.ARINA_ID

    await show_all_love_messages(message)

    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.simple_messages.delete_messages_after_showing_content",
    new_callable=AsyncMock,
)
@patch(
    "love_bot.handlers.simple_messages.show_content",
    new_callable=AsyncMock,
)
async def test_show_all_dreams(mock_show, mock_delete, message):
    mock_show.return_value = []

    await show_all_dreams(message)

    mock_show.assert_awaited_once()
    mock_delete.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.simple_messages.write_content",
    new_callable=AsyncMock,
)
async def test_handle_message_owner(mock_write, message):
    message.chat.id = config.MY_ID

    await handle_message(message)

    mock_write.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.simple_messages.safe_send_message",
    new_callable=AsyncMock,
)
async def test_handle_message_Arina(mock_send, message):
    message.chat.id = config.ARINA_ID

    await handle_message(message)

    mock_send.assert_awaited_once()
