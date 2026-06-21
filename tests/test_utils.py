from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from love_bot import config
from love_bot.utils import (
    get_date_with_month_written_by_letters, get_indexes, safe_send_message,
)


@pytest.mark.asyncio
async def test_safe_send_message_success():
    sent_message = SimpleNamespace(message_id=777)
    config.bot.send_message = AsyncMock(return_value=sent_message)
    config.bot.forward_message = AsyncMock()
    result = await safe_send_message(config.MY_ID, 'hello')
    assert result == 777
    config.bot.send_message.assert_awaited_once_with(
        config.MY_ID, 'hello', reply_markup=None,
    )
    config.bot.forward_message.assert_not_called()


@pytest.mark.asyncio
async def test_safe_send_message_to_Arina():
    sent_message = SimpleNamespace(message_id=777)
    config.bot.send_message = AsyncMock(return_value=sent_message)
    config.bot.forward_message = AsyncMock()
    await safe_send_message(config.ARINA_ID, 'hello')
    config.bot.forward_message.assert_awaited_once_with(
        chat_id=config.MY_ID, from_chat_id=config.ARINA_ID, message_id=777,
    )


@pytest.mark.asyncio
async def test_safe_send_message_with_request_message():
    sent_message = SimpleNamespace(message_id=777)
    config.bot.send_message = AsyncMock(return_value=sent_message)
    config.bot.forward_message = AsyncMock()
    await safe_send_message(config.ARINA_ID, 'hello', request_message_id=123)
    assert config.bot.forward_message.await_count == 2
    config.bot.forward_message.assert_any_await(
        chat_id=config.MY_ID, from_chat_id=config.ARINA_ID, message_id=123,
    )
    config.bot.forward_message.assert_any_await(
        chat_id=config.MY_ID, from_chat_id=config.ARINA_ID, message_id=777,
    )


@pytest.mark.asyncio
@patch.object(config.logger, 'exception')
async def test_safe_send_message_logs_unknown_error(mock_logger):
    config.bot.send_message = AsyncMock(side_effect=Exception('boom'))
    result = await safe_send_message(config.MY_ID, 'hello')
    assert result is None
    mock_logger.assert_called_once()


@pytest.mark.asyncio
@patch.object(config.logger, 'exception')
async def test_safe_send_message_ignores_chat_not_found(mock_logger):
    config.bot.send_message = AsyncMock(
        side_effect=Exception('chat not found'),
    )
    await safe_send_message(config.MY_ID, 'hello')
    mock_logger.assert_not_called()


def test_get_indexes_single():
    assert get_indexes('1, 2, 3') == [1, 2, 3]


def test_get_indexes_ranges():
    assert get_indexes('1-3') == [1, 2, 3]


def test_get_indexes_mixed():
    assert get_indexes('1, 3-5, 7') == [1, 3, 4, 5, 7]


@pytest.mark.parametrize(
    ('source', 'expected'),
    (
        ('01.01', '1 января '),
        ('15.10.2025', '15 октября 2025'),
    ),
)
def test_get_date_with_month_written_by_letters(source, expected):
    assert (get_date_with_month_written_by_letters(source) == expected)
