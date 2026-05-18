from unittest.mock import AsyncMock, patch

import pytest

from love_bot.handlers.starting_operations import (
    start_dream_writing,
    start_dreams_deleting,
    start_love_messages_deleting,
    start_writing_as_bot,
)
from love_bot import config


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.starting_operations.safe_send_message",
    new_callable=AsyncMock,
)
async def test_start_dream_writing(mock_send, message, state):
    message.chat.id = config.ARINA_ID

    await start_dream_writing(message, state)

    state.set_state.assert_awaited_once()
    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.starting_operations.safe_send_message",
    new_callable=AsyncMock,
)
async def test_start_delete_messages_for_Arina(
    mock_send,
    message,
    state,
):
    message.chat.id = config.ARINA_ID

    await start_love_messages_deleting(message, state)

    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.starting_operations.show_content",
    new_callable=AsyncMock,
)
@patch(
    (
        "love_bot.handlers.starting_operations."
        "delete_messages_after_showing_content"
    ),
    new_callable=AsyncMock,
)
async def test_start_delete_messages(
    mock_delete,
    mock_show,
    message,
    state,
):
    message.chat.id = config.MY_ID

    mock_show.return_value = []

    await start_love_messages_deleting(message, state)

    state.set_state.assert_awaited_once()
    mock_show.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "love_bot.handlers.starting_operations.show_content",
    new_callable=AsyncMock,
)
@patch(
    "love_bot.handlers.starting_operations.safe_send_message",
    new_callable=AsyncMock,
)
@patch(
    (
        "love_bot.handlers.starting_operations."
        "delete_messages_after_showing_content"
    ),
    new_callable=AsyncMock,
)
async def test_start_dreams_deleting(
    mock_delete,
    mock_send,
    mock_show,
    message,
    state,
):
    message.chat.id = config.ARINA_ID

    mock_show.return_value = []

    await start_dreams_deleting(message, state)

    state.set_state.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_writing_as_bot(message, state):
    message.chat.id = config.MY_ID

    await start_writing_as_bot(message, state)

    state.set_state.assert_awaited_once()
    message.answer.assert_awaited_once()
