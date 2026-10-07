from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from love_bot.core import config, templates
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.love_messages.simple_messages.safe_send_message',
    autospec=True,
)
async def test_write_love_message_unsuccessfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    with (
        patch(
            'love_bot.handlers.love_messages.simple_messages.write_content',
            side_effect=Exception(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.MY_ID))
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_safe_send.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.love_messages.simple_messages.write_content',
    autospec=True,
)
@patch(
    'love_bot.handlers.love_messages.simple_messages.safe_send_message',
    autospec=True,
)
async def test_write_love_message_successfully(
    mock_safe_send: AsyncMock,
    mock_write_content: MagicMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
) -> None:
    await dispatcher.feed_update(bot, make_update(config.MY_ID))
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_write_content.assert_called_once_with(
        config.LOVE_MESSAGES_FILEPATH, text_message,
    )
    mock_safe_send.assert_awaited_once_with(
        config.MY_ID, templates.CONTENT_IS_SAVED,
    )
