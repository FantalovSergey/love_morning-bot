from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot, Dispatcher

from love_bot.core import config, templates
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.other.simple_messages.safe_send_message', autospec=True,
)
async def test_handle_Arina_message(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, templates.SUCCESSFULL_SENDING, received_message_id,
    )
