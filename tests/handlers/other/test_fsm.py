from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot

from love_bot.core import config, keyboards, templates
from love_bot.core.states import NoteForArinaSending
from tests.types import DispatcherFactory, UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch('love_bot.handlers.other.fsm.config.bot.copy_message', autospec=True)
@patch('love_bot.handlers.other.fsm.safe_send_message', autospec=True)
async def test_write_note_for_Arina(
    mock_safe_send: AsyncMock,
    mock_copy_message: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.MY_ID, state=NoteForArinaSending.note_waiting,
    )
    await dispatcher.feed_update(bot, make_update(config.MY_ID))
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_copy_message.assert_awaited_once_with(
        chat_id=config.ARINA_ID,
        from_chat_id=config.MY_ID,
        message_id=received_message_id,
    )
    mock_safe_send.assert_awaited_once_with(
        config.MY_ID, templates.SUCCESS, keyboard=keyboards.my_keyboard,
    )
