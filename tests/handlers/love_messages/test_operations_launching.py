from unittest.mock import AsyncMock, call, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State

from love_bot.core import config, keyboards, templates
from love_bot.core.states import LoveMessagesDeleting
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.love_messages.operations_launching.safe_send_message',
    autospec=True,
)
@patch(
    (
        'love_bot.handlers.love_messages.operations_launching.'
        'get_message_with_right_greeting'
    ),
    autospec=True,
)
@patch(
    'love_bot.handlers.love_messages.operations_launching.retrieve_content',
    autospec=True,
)
async def test_send_cuteness_immediately(
    mock_retrieve_content: AsyncMock,
    mock_get_message: MagicMock,
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    await dispatcher.feed_update(
        bot,
        make_update(config.ARINA_ID, text_message=keyboards.GET_CUTENESS),
    )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_retrieve_content.assert_awaited_once_with(
        config.LOVE_MESSAGES_FILEPATH,
    )
    mock_get_message.assert_called_once_with(
        mock_retrieve_content.return_value,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, mock_get_message.return_value, received_message_id,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('text_message', 'expected_response'),
    (
        (
            keyboards.SHOW_MESSAGES,
            templates.SHOWING_ARINA_ALL_LOVE_MESSAGE_RESPONSE,
        ),
        (
            keyboards.DELETE_MESSAGES,
            templates.DELETING_LOVE_MESSAGES_BY_ARINA_RESPONSE,
        ),
    ),
)
@patch(
    'love_bot.handlers.love_messages.operations_launching.safe_send_message',
    autospec=True,
)
async def test_make_illegal_Arina_requests(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
    received_message_id: int,
    expected_response: str,
) -> None:
    await dispatcher.feed_update(
        bot, make_update(config.ARINA_ID, text_message),
    )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, expected_response, received_message_id,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'text_message', (keyboards.SHOW_MESSAGES, keyboards.DELETE_MESSAGES),
)
@patch(
    'love_bot.handlers.love_messages.operations_launching.safe_send_message',
    autospec=True,
)
async def test_show_all_love_messages_unsuccessfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.love_messages.operations_launching.'
                'list_content'
            ),
            side_effect=Exception(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(
            bot, make_update(config.MY_ID, text_message),
        )
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_safe_send.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('text_message', 'expected_state'),
    (
        (keyboards.SHOW_MESSAGES, None),
        (keyboards.DELETE_MESSAGES, LoveMessagesDeleting.indexes_waiting),
    ),
)
@patch(
    (
        'love_bot.handlers.love_messages.operations_launching.'
        'delete_messages_after_content_showing'
    ),
    autospec=True,
)
@patch(
    'love_bot.handlers.love_messages.operations_launching.safe_send_message',
    autospec=True,
)
@patch(
    'love_bot.handlers.love_messages.operations_launching.list_content',
    autospec=True,
)
async def test_show_all_love_messages_successfully(
    mock_list_content: AsyncMock,
    mock_safe_send: AsyncMock,
    mock_delete_messages: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
    expected_state: State | None,
    repr_content: list[str],
    sent_message_ids: list[int],
) -> None:
    mock_list_content.return_value = repr_content.copy()
    mock_safe_send.side_effect = sent_message_ids + [None]
    await dispatcher.feed_update(bot, make_update(config.MY_ID, text_message))
    mock_list_content.assert_awaited_once_with(config.LOVE_MESSAGES_FILEPATH)
    mock_safe_send.assert_has_awaits(
        [call(config.MY_ID, message) for message in repr_content],
    )
    await assert_state(dispatcher, bot, config.MY_ID, expected_state)
    mock_delete_messages.assert_awaited_once_with(
        config.MY_ID, sent_message_ids,
    )


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.love_messages.operations_launching.safe_send_message',
    autospec=True,
)
async def test_start_love_messages_deleting(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.love_messages.operations_launching.'
                'list_content'
            ),
        ),
        patch(
            (
                'love_bot.handlers.love_messages.operations_launching.'
                'delete_messages_after_content_showing'
            ),
        ),
    ):
        await dispatcher.feed_update(
            bot, make_update(
                config.MY_ID, text_message=keyboards.DELETE_MESSAGES,
            ),
        )
    mock_safe_send.assert_has_awaits(
        (
            call(
                config.MY_ID,
                templates.LOVE_MESSAGES_DELETING_INVITE,
                keyboard=keyboards.cancel,
            ),
        ),
    )
