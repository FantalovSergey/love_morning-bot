from unittest.mock import AsyncMock, call, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from love_bot.core import config, keyboards, templates
from love_bot.core.exceptions import EmptyFileError
from love_bot.core.states import DreamWriting, DreamsDeleting
from tests.types import UpdateFactory
from tests.utils import assert_state


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'text_message', (keyboards.SHOW_DREAMS, keyboards.DELETE_DREAMES),
)
@patch(
    'love_bot.handlers.dreams.operations_launching.config.bot.forward_message',
    autospec=True,
)
async def test_forward_message_when_Arina_requests_showing_or_deleting_dreams(
    mock_forward: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
    received_message_id: int,
) -> None:
    with (
        patch('love_bot.handlers.dreams.operations_launching.list_content'),
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'delete_messages_after_content_showing'
            ),
        ),
        patch(
            'love_bot.handlers.dreams.operations_launching.safe_send_message',
        ),
    ):
        await dispatcher.feed_update(
            bot, make_update(config.ARINA_ID, text_message),
        )
    mock_forward.assert_awaited_once_with(
        chat_id=config.MY_ID,
        from_chat_id=config.ARINA_ID,
        message_id=received_message_id,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('exception', 'expected_response'),
    (
        (EmptyFileError(), templates.FILE_IS_EMPTY),
        (OSError(), templates.DREAMS_FILE_ERROR),
    ),
)
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_show_Arina_all_dreams_unsuccessfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    exception: Exception,
    expected_response: str,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'config.bot.forward_message'
            ),
        ),
        patch(
            'love_bot.handlers.dreams.operations_launching.list_content',
            side_effect=exception,
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(
            bot,
            make_update(config.ARINA_ID, text_message=keyboards.SHOW_DREAMS),
        )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(config.ARINA_ID, expected_response)


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_show_me_all_dreams_unsuccessfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'config.bot.forward_message'
            ),
        ),
        patch(
            'love_bot.handlers.dreams.operations_launching.list_content',
            side_effect=Exception(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(
            bot, make_update(config.MY_ID, text_message=keyboards.SHOW_DREAMS),
        )
    await assert_state(dispatcher, bot, config.MY_ID, expected_state=None)
    mock_safe_send.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize('chat_id', (config.ARINA_ID, config.MY_ID))
@patch('love_bot.handlers.dreams.operations_launching.list_content')
@patch(
    (
        'love_bot.handlers.dreams.operations_launching.'
        'delete_messages_after_content_showing'
    ),
    autospec=True,
)
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_show_all_dreams_successfully(
    mock_safe_send: AsyncMock,
    mock_delete_messages: AsyncMock,
    mock_list_content: MagicMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    chat_id: int,
    repr_content: list[str],
    sent_message_ids: list[int],
) -> None:
    mock_list_content.return_value = repr_content.copy()
    mock_safe_send.side_effect = sent_message_ids.copy()
    with patch(
        (
            'love_bot.handlers.dreams.operations_launching.'
            'config.bot.forward_message'
        ),
    ):
        await dispatcher.feed_update(
            bot, make_update(chat_id, text_message=keyboards.SHOW_DREAMS),
        )
    await assert_state(dispatcher, bot, chat_id, expected_state=None)
    mock_safe_send.assert_has_awaits(
        [call(chat_id, message) for message in repr_content],
    )
    mock_delete_messages.assert_awaited_once_with(chat_id, sent_message_ids)


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_start_dream_writing(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    await dispatcher.feed_update(
        bot, make_update(config.ARINA_ID, text_message=keyboards.WRITE_DREAM),
    )
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamWriting.dream_waiting,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID,
        templates.DREAM_WRITING_INVITE,
        received_message_id,
        keyboards.cancel,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('exception', 'expected_response'),
    (
        (EmptyFileError(), templates.NOTHING_TO_DELETE),
        (OSError(), templates.DREAMS_FILE_ERROR),
    ),
)
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_start_dreams_deleting_unsuccessfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    exception: Exception,
    expected_response: str,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'config.bot.forward_message'
            ),
        ),
        patch(
            'love_bot.handlers.dreams.operations_launching.list_content',
            side_effect=exception,
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(
            bot,
            make_update(
                config.ARINA_ID, text_message=keyboards.DELETE_DREAMES,
            ),
        )
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_safe_send.assert_awaited_once_with(config.ARINA_ID, expected_response)


@pytest.mark.asyncio
@patch('love_bot.handlers.dreams.operations_launching.list_content')
@patch(
    (
        'love_bot.handlers.dreams.operations_launching.'
        'delete_messages_after_content_showing'
    ),
    autospec=True,
)
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_show_dreams_before_deleting(
    mock_safe_send: AsyncMock,
    mock_delete_messages: AsyncMock,
    mock_list_content: MagicMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
    repr_content: list[str],
    sent_message_ids: list[int],
) -> None:
    mock_list_content.return_value = repr_content.copy()
    mock_safe_send.side_effect = sent_message_ids + [None]
    with patch(
        (
            'love_bot.handlers.dreams.operations_launching.'
            'config.bot.forward_message'
        ),
    ):
        await dispatcher.feed_update(
            bot,
            make_update(
                config.ARINA_ID, text_message=keyboards.DELETE_DREAMES,
            ),
        )
    mock_safe_send.assert_has_awaits(
        [call(config.ARINA_ID, message) for message in repr_content],
    )
    mock_delete_messages.assert_awaited_once_with(
        config.ARINA_ID, sent_message_ids,
    )


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.dreams.operations_launching.safe_send_message',
    autospec=True,
)
async def test_start_dreams_deleting_successfully(
    mock_safe_send: AsyncMock,
    dispatcher: Dispatcher,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    with (
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'config.bot.forward_message'
            ),
        ),
        patch('love_bot.handlers.dreams.operations_launching.list_content'),
        patch(
            (
                'love_bot.handlers.dreams.operations_launching.'
                'delete_messages_after_content_showing'
            ),
        ),
    ):
        await dispatcher.feed_update(
            bot,
            make_update(
                config.ARINA_ID, text_message=keyboards.DELETE_DREAMES,
            ),
        )
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamsDeleting.indexes_waiting,
    )
    mock_safe_send.assert_has_awaits(
        (
            call(
                config.ARINA_ID,
                templates.DREAMS_DELETING_INVITE,
                keyboard=keyboards.cancel,
            ),
        ),
    )
