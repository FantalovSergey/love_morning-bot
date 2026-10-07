from unittest.mock import AsyncMock, call, MagicMock, patch

import pytest
from aiogram import Bot

from love_bot.core import config, templates
from love_bot.core.keyboards import my_keyboard
from love_bot.core.states import LoveMessagesDeleting
from tests.types import DispatcherFactory, UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch('love_bot.handlers.love_messages.fsm.safe_send_message', autospec=True)
async def test_delete_love_messages_unsuccessfully(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.MY_ID, state=LoveMessagesDeleting.indexes_waiting,
    )
    with (
        patch(
            'love_bot.handlers.love_messages.fsm.delete_content',
            side_effect=Exception(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.MY_ID))
    await assert_state(
        dispatcher,
        bot,
        config.MY_ID,
        expected_state=LoveMessagesDeleting.indexes_waiting,
    )
    mock_safe_send.assert_not_awaited()


@pytest.mark.asyncio
@patch('love_bot.handlers.love_messages.fsm.delete_content')
@patch('love_bot.handlers.love_messages.fsm.safe_send_message', autospec=True)
async def test_delete_love_messages_successfully(
    mock_safe_send: AsyncMock,
    mock_delete_content: MagicMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
    repr_content: list[str],
) -> None:
    mock_delete_content.return_value = repr_content.copy()
    dispatcher = await get_dispatcher_with_state(
        config.MY_ID, state=LoveMessagesDeleting.indexes_waiting,
    )
    await dispatcher.feed_update(bot, make_update(config.MY_ID))
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_delete_content.assert_called_once_with(
        config.LOVE_MESSAGES_FILEPATH, text_message,
    )
    mock_safe_send.assert_has_awaits(
        [call(config.MY_ID, message) for message in repr_content],
    )
    mock_safe_send.assert_has_awaits(
        (
            call(
                config.MY_ID,
                templates.CONTENT_IS_DELETED,
                keyboard=my_keyboard,
            ),
        ),
    )
