from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot, Dispatcher

from love_bot.core import templates
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch('love_bot.core.middlewares.safe_send_message', autospec=True)
async def test_handle_message_from_unknown_user(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    chat_id: int,
    received_message_id: int,
) -> None:
    await dispatcher.feed_update(bot, make_update())
    await assert_state(dispatcher, bot, chat_id, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        chat_id, templates.MESSAGE_FOR_UNKNOWN_USERS, received_message_id,
    )
