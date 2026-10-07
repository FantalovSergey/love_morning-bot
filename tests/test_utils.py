from unittest.mock import AsyncMock, call, patch

import pytest
from aiogram.types import Message

from love_bot.core import config
from love_bot.core.utils import (
    get_content_for_repr,
    get_date_with_month_written_by_letters,
    get_indexes,
    safe_send_message,
)


@pytest.mark.asyncio
@patch('love_bot.core.utils.config.bot.forward_message', autospec=True)
async def test_safe_send_message_without_request_message_id(
    mock_forward: AsyncMock,
    chat_id: int,
    message: Message,
    text_message: str,
    sent_message_id: int,
) -> None:
    with patch(
        'love_bot.core.utils.config.bot.send_message', return_value=message,
    ):
        assert (
            await safe_send_message(chat_id, text_message) == sent_message_id
        )
    mock_forward.assert_awaited_once_with(
        chat_id=config.MY_ID, from_chat_id=chat_id, message_id=sent_message_id,
    )


@pytest.mark.asyncio
@patch('love_bot.core.utils.config.bot.forward_message', autospec=True)
async def test_safe_send_message_with_request_message_id(
    mock_forward: AsyncMock,
    chat_id: int,
    message: Message,
    text_message: str,
    received_message_id: int,
    sent_message_id: int,
) -> None:
    with patch(
        'love_bot.core.utils.config.bot.send_message', return_value=message,
    ):
        assert (
            await safe_send_message(
                chat_id, text_message, received_message_id,
            ) == sent_message_id
        )
    mock_forward.assert_has_awaits(
        [
            call(
                chat_id=config.MY_ID,
                from_chat_id=chat_id,
                message_id=forwarded_message_id,
            )
            for forwarded_message_id in (received_message_id, sent_message_id)
        ]
    )


def test_get_indexes_single() -> None:
    assert get_indexes('1, 3') == [1, 3]


def test_get_indexes_ranges() -> None:
    assert get_indexes('1-3') == [1, 2, 3]


def test_get_indexes_mixed() -> None:
    assert get_indexes('1, 3-5, 7') == [1, 3, 4, 5, 7]


def test_get_content_for_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        'love_bot.core.utils.config.TELEGRAM_MESSAGE_SYMBOL_LIMIT', 20,
    )
    assert (
        get_content_for_repr(
            ['hello\n', 'world\n', '!\n', '!\n'],
        ) == ['1. hello\n2. world\n', '3. !\n4. !\n']
    )


@pytest.mark.parametrize(
    ('source', 'expected'),
    (
        ('01.01', '1 января '),
        ('15.10.2025', '15 октября 2025'),
    ),
)
def test_get_date_with_month_written_by_letters(
    source: str, expected: str,
) -> None:
    assert get_date_with_month_written_by_letters(source) == expected
