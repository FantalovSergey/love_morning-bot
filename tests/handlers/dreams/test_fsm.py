from unittest.mock import AsyncMock, call, MagicMock, patch

import pytest
from aiogram import Bot

from love_bot.core import config, templates
from love_bot.core.exceptions import (
    EmptyFileError,
    EmptyRequestError,
    NoContentForDeletingError,
    TooLongContentMessageError,
)
from love_bot.core.keyboards import Arina_keyboard
from love_bot.core.states import DreamsDeleting, DreamWriting
from tests.types import DispatcherFactory, UpdateFactory
from tests.utils import assert_state

SYMBOL_EXCEEDING = 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('exception', 'expected_response'),
    (
        (EmptyRequestError, templates.WRITE_DREAM_REQUEST_IS_EMPTY),
        (
            TooLongContentMessageError(
                symbol_limit_exceeding=SYMBOL_EXCEEDING,
            ),
            templates.get_too_long_dream_warning(SYMBOL_EXCEEDING),
        ),
    ),
)
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_handle_invalid_dream_writing_requests(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
    exception: Exception,
    expected_response: str,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamWriting.dream_waiting,
    )
    with (
        patch(
            'love_bot.handlers.dreams.fsm.validate_writing_request',
            side_effect=exception,
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamWriting.dream_waiting,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, expected_response, received_message_id,
    )


@pytest.mark.asyncio
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_write_dream_unsuccessfully(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamWriting.dream_waiting,
    )
    with (
        patch(
            'love_bot.handlers.dreams.fsm.write_content',
            side_effect=OSError(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamWriting.dream_waiting,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, templates.DREAMS_FILE_ERROR, received_message_id,
    )


@pytest.mark.asyncio
@patch('love_bot.handlers.dreams.fsm.write_content', autospec=True)
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_write_dream_successfully(
    mock_safe_send: AsyncMock,
    mock_write_content: MagicMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    text_message: str,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamWriting.dream_waiting,
    )
    await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_write_content.assert_called_once_with(
        config.DREAMS_FILEPATH, text_message, timestamp=True,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID,
        templates.CONTENT_IS_SAVED,
        received_message_id,
        Arina_keyboard,
    )


@pytest.mark.asyncio
@patch(
    'love_bot.handlers.dreams.fsm.config.bot.forward_message', autospec=True,
)
async def test_forward_message_when_deleting_dreams(
    mock_forward: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    received_message_id: int,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamsDeleting.indexes_waiting,
    )
    with (
        patch('love_bot.handlers.dreams.fsm.delete_content'),
        patch('love_bot.handlers.dreams.fsm.safe_send_message'),
    ):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    mock_forward.assert_awaited_once_with(
        chat_id=config.MY_ID,
        from_chat_id=config.ARINA_ID,
        message_id=received_message_id,
    )


@pytest.mark.asyncio
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_handle_empty_dreams_deleting_request(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamsDeleting.indexes_waiting,
    )
    with (
        patch('love_bot.handlers.dreams.fsm.config.bot.forward_message'),
        patch(
            'love_bot.handlers.dreams.fsm.validate_request_text_is_not_none',
            side_effect=EmptyRequestError(),
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamsDeleting.indexes_waiting,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, templates.DELETE_DREAMS_REQUEST_IS_INVALID,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('exception', 'expected_response'),
    (
        (NoContentForDeletingError(), templates.OUT_OF_RANGE_INDEXES_ERROR),
        (ValueError(), templates.DELETE_DREAMS_REQUEST_IS_INVALID),
        (EmptyFileError(), templates.DREAMS_FILE_ERROR),
        (OSError(), templates.DREAMS_FILE_ERROR)
    ),
)
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_delete_dreams_unsuccessfully(
    mock_safe_send: AsyncMock,
    get_dispatcher_with_state: DispatcherFactory,
    bot: Bot,
    make_update: UpdateFactory,
    exception: Exception,
    expected_response: str,
) -> None:
    dispatcher = await get_dispatcher_with_state(
        config.ARINA_ID, state=DreamsDeleting.indexes_waiting,
    )
    with (
        patch('love_bot.handlers.dreams.fsm.config.bot.forward_message'),
        patch(
            'love_bot.handlers.dreams.fsm.delete_content',
            side_effect=exception,
        ),
        pytest.raises(Exception),
    ):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(
        dispatcher,
        bot,
        config.ARINA_ID,
        expected_state=DreamsDeleting.indexes_waiting,
    )
    mock_safe_send.assert_awaited_once_with(config.ARINA_ID, expected_response)


@pytest.mark.asyncio
@patch('love_bot.handlers.dreams.fsm.delete_content', autospec=True)
@patch('love_bot.handlers.dreams.fsm.safe_send_message', autospec=True)
async def test_delete_dreams_successfully(
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
        config.ARINA_ID, state=DreamsDeleting.indexes_waiting,
    )
    with patch('love_bot.handlers.dreams.fsm.config.bot.forward_message'):
        await dispatcher.feed_update(bot, make_update(config.ARINA_ID))
    await assert_state(dispatcher, bot, config.ARINA_ID, expected_state=None)
    mock_delete_content.assert_called_once_with(
        config.DREAMS_FILEPATH, text_message,
    )
    mock_safe_send.assert_has_awaits(
        [call(config.ARINA_ID, message) for message in repr_content],
    )
    mock_safe_send.assert_has_awaits(
        (
            call(
                config.ARINA_ID,
                templates.CONTENT_IS_DELETED,
                keyboard=Arina_keyboard,
            ),
        ),
    )
