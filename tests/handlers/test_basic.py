from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup

from love_bot.core import config, keyboards, templates
from tests.types import DispatcherFactory, UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch('love_bot.handlers.basic.safe_send_message', autospec=True)
async def test_Arina_start(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(config.ARINA_ID)
    await dispatcher.feed_update(
        bot, make_update(config.ARINA_ID, text_message='/start'),
    )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID,
        templates.START_MESSAGE_FOR_ARINA,
        received_message_id,
        keyboards.Arina_keyboard,
    )


@pytest.mark.asyncio
@patch('love_bot.handlers.basic.safe_send_message', autospec=True)
async def test_my_start(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    dispatcher = await get_dispatcher_with_state(config.MY_ID)
    await dispatcher.feed_update(
        bot, make_update(config.MY_ID, text_message='/start'),
    )
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        config.MY_ID, templates.START_FOR_ME, keyboard=keyboards.my_keyboard,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('chat_id', 'keyboard'),
    (
        (config.ARINA_ID, keyboards.Arina_keyboard),
        (config.MY_ID, keyboards.my_keyboard),
    ),
)
@patch('love_bot.handlers.basic.safe_send_message', autospec=True)
async def test_cancel(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    chat_id: int,
    keyboard: ReplyKeyboardMarkup,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(chat_id)
    await dispatcher.feed_update(
        bot, make_update(chat_id, text_message=keyboards.CANCEL),
    )
    await assert_state(dispatcher, bot, chat_id, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        chat_id, templates.CANCEL_RESPONSE, received_message_id, keyboard,
    )
