import errno
from datetime import datetime
from unittest.mock import AsyncMock, call, MagicMock, patch

import pytest
from aiogram.types import Message

from love_bot.core import config, templates
from love_bot.tasks import (
    delete_messages_after_content_showing, send_backups, wish_good_morning,
)
from tests.exeptions import StopTest


@pytest.mark.asyncio
@patch('love_bot.tasks.retrieve_content', autospec=True)
@patch('love_bot.tasks.safe_send_message', autospec=True)
async def test_WISH_good_morning(
    mock_safe_send: AsyncMock, mock_retrieve_content: MagicMock,
) -> None:
    with (
        patch('love_bot.tasks.asyncio.sleep', side_effect=[None, StopTest]),
        pytest.raises(StopTest),
    ):
        await wish_good_morning()
    mock_retrieve_content.assert_called_once_with(
        config.LOVE_MESSAGES_FILEPATH,
    )
    mock_safe_send.assert_awaited_once_with(
        config.ARINA_ID, mock_retrieve_content.return_value,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('now', 'expected_delay'),
    (
        (
            datetime(year=2026, month=2, day=17, hour=5, tzinfo=config.TZ),
            1 * config.HOUR,
        ),
        (
            datetime(year=2026, month=2, day=17, hour=7, tzinfo=config.TZ),
            23 * config.HOUR,
        ),
    )
)
@patch('love_bot.tasks.datetime', wraps=datetime)
@patch(
    'love_bot.tasks.asyncio.sleep',
    autospec=True,
    side_effect=[None, StopTest],
)
async def test_wish_good_MORNING(
    mock_sleep: AsyncMock,
    mock_datetime: MagicMock,
    now: datetime,
    expected_delay: int,
) -> None:
    mock_datetime.now.return_value = now
    with (
        patch('love_bot.tasks.retrieve_content'),
        patch('love_bot.tasks.safe_send_message'),
        pytest.raises(StopTest),
    ):
        await wish_good_morning()
    mock_sleep.assert_has_awaits((call(expected_delay), call(1)))


@pytest.mark.asyncio
@patch('love_bot.tasks.config.bot.delete_messages', autospec=True)
@patch('love_bot.tasks.config.bot.edit_message_text', autospec=True)
async def test_delete_one_message_after_content_showing(
    mock_edit_message: AsyncMock,
    mock_delete_messages: AsyncMock,
    chat_id: int,
    sent_message_id: int,
) -> None:
    with patch('love_bot.tasks.asyncio.sleep'):
        await delete_messages_after_content_showing(
            chat_id, [sent_message_id],
        )
    mock_delete_messages.assert_not_awaited()
    mock_edit_message.assert_awaited_once_with(
        templates.AFTER_DELETING_NOTIFICATION,
        chat_id=chat_id,
        message_id=sent_message_id,
    )


@pytest.mark.asyncio
@patch('love_bot.tasks.asyncio.sleep', autospec=True)
@patch('love_bot.tasks.config.bot.delete_messages', autospec=True)
@patch('love_bot.tasks.config.bot.edit_message_text', autospec=True)
async def test_delete_many_messages_after_content_showing(
    mock_edit_message: AsyncMock,
    mock_delete_messages: AsyncMock,
    mock_sleep: AsyncMock,
    chat_id: int,
    sent_message_ids: list[int],
) -> None:
    copied_message_ids = sent_message_ids.copy()
    await delete_messages_after_content_showing(chat_id, copied_message_ids)
    mock_sleep.assert_awaited_once_with(config.CONTENT_SHOWING_PERIOD)
    mock_delete_messages.assert_awaited_once_with(
        chat_id, sent_message_ids[1:],
    )
    mock_edit_message.assert_awaited_once_with(
        templates.AFTER_DELETING_NOTIFICATION,
        chat_id=chat_id,
        message_id=sent_message_ids[0],
    )


@pytest.mark.asyncio
@patch(
    'love_bot.tasks.asyncio.sleep', autospec=True, side_effect=StopTest,
)
@patch.object(config.logger, 'exception')
@patch('love_bot.tasks.safe_send_message', autospec=True)
@patch('love_bot.tasks.config.bot.send_document', autospec=True)
async def test_send_backups(
    mock_send_doc: AsyncMock,
    mock_send_message: AsyncMock,
    mock_logger: MagicMock,
    mock_sleep: AsyncMock,
    message: Message,
    text_message: str,
) -> None:
    mock_send_doc.side_effect = [
        Exception(f'[Errno {errno.ENOENT}]'), message, Exception(text_message),
    ]
    with pytest.raises(StopTest):
        await send_backups()
    mock_logger.assert_called_once()
    assert mock_send_message.await_count == 2
    chat_ids: list[int] = []
    text_messages: list[str] = []
    for call_args in mock_send_message.call_args_list:
        chat_ids.append(call_args.args[0])
        text_messages.append(call_args.args[1])
    assert chat_ids[0] == chat_ids[1] == config.MY_ID
    # Первый в очереди на отправку файл с сообщениями,
    # поэтому в первом сообщении об ошибке должен быть хотя бы путь к файлу
    assert config.LOVE_MESSAGES_FILEPATH in text_messages[0]
    assert text_messages[1] == text_message
    mock_sleep.assert_called_once_with(config.BACKUP_PERIOD)
