from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot, Dispatcher

from love_bot.core import config, keyboards, templates
from love_bot.core.states import NoteForArinaSending
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
async def test_Arina_starts_writing_as_bot(
    dispatcher: Dispatcher, bot: Bot, make_update: UpdateFactory,
) -> None:
    with patch('love_bot.handlers.other.simple_messages.safe_send_message'):
        await dispatcher.feed_update(
            bot,
            make_update(config.ARINA_ID, text_message=keyboards.WRITE_AS_BOT),
        )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.other.operations_launching.safe_send_message',
    autospec=True,
)
async def test_start_writing_as_bot(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    await dispatcher.feed_update(
        bot, make_update(config.MY_ID, text_message=keyboards.WRITE_AS_BOT),
    )
    await assert_state(
        dispatcher,
        bot,
        config.MY_ID,
        expected_state=NoteForArinaSending.note_waiting,
    )
    mock_safe_send.assert_awaited_once_with(
        config.MY_ID,
        templates.WRITING_AS_BOT_INVITE,
        keyboard=keyboards.cancel,
    )
