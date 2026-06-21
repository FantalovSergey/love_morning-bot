from unittest.mock import AsyncMock, patch

import pytest

from love_bot.handlers.fsm import (
    delete_dreams, delete_love_messages, write_dream, write_note_for_Arina,
)
from love_bot import config


@pytest.mark.asyncio
@patch('love_bot.handlers.fsm.write_content', new_callable=AsyncMock)
async def test_write_dream_success(mock_write, message, state):
    message.text = 'short dream'
    await write_dream(message, state)
    state.clear.assert_awaited_once()
    mock_write.assert_awaited_once()


@pytest.mark.asyncio
@patch('love_bot.handlers.fsm.safe_send_message', new_callable=AsyncMock)
async def test_write_dream_too_long(mock_send, message, state):
    message.text = 'a' * (config.TO_BOT_MESSAGE_SYMBOL_LIMIT + 1)
    await write_dream(message, state)
    mock_send.assert_awaited_once()
    state.clear.assert_not_awaited()


@pytest.mark.asyncio
@patch('love_bot.handlers.fsm.delete_content', new_callable=AsyncMock)
async def test_delete_love_messages(mock_delete, message, state):
    await delete_love_messages(message, state)
    mock_delete.assert_awaited_once()


@pytest.mark.asyncio
@patch('love_bot.handlers.fsm.delete_content', new_callable=AsyncMock)
async def test_delete_dreams(mock_delete, message, state):
    await delete_dreams(message, state)
    mock_delete.assert_awaited_once()


@pytest.mark.asyncio
@patch('love_bot.handlers.fsm.config.bot.copy_message', new_callable=AsyncMock)
async def test_write_note_for_Arina(mock_send, message, state):
    await write_note_for_Arina(message, state)
    state.clear.assert_awaited_once()
    mock_send.assert_awaited_once()
    message.answer.assert_awaited_once()
