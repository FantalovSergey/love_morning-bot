import errno
from typing import Callable
from unittest.mock import ANY, AsyncMock, MagicMock, mock_open, patch

import pytest

from love_bot.core import config
from love_bot.core.exceptions import EmptyFileError
from love_bot.files import safe_read_file, safe_write_in_file

RETRYABLE_EXEPTIONS: tuple[int, ...] = (errno.ESTALE,)


@pytest.mark.asyncio
@pytest.mark.parametrize('exception', (FileNotFoundError(), OSError()))
@pytest.mark.parametrize(
    ('tested_func', 'args', 'phrase_is_contained'),
    (
        (safe_read_file, (ANY,), 'чтени'),
        (safe_write_in_file, (ANY, ANY, ANY), 'запис')
    ),
)
@patch('love_bot.files.safe_send_message', autospec=True)
@patch.object(config.logger, 'exception')
async def test_safe_open_file_with_not_retryable_os_error(
    mock_logger: MagicMock,
    mock_safe_send: AsyncMock,
    exception: Exception,
    tested_func: Callable,
    args: tuple,
    phrase_is_contained: str,
) -> None:
    with (
        patch('builtins.open', side_effect=exception),
        pytest.raises(OSError),
    ):
        tested_func(*args)
    if not isinstance(exception, FileNotFoundError):
        mock_logger.assert_called_once()
    mock_safe_send.assert_called_once()
    chat_id, error_message = mock_safe_send.call_args.args
    assert chat_id == config.MY_ID
    assert phrase_is_contained in error_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'exception',
    [OSError(error_number, '') for error_number in RETRYABLE_EXEPTIONS],
)
@pytest.mark.parametrize(
    ('tested_func', 'args', 'phrase_is_contained'),
    (
        (safe_read_file, (ANY,), 'чтени'),
        (safe_write_in_file, (ANY, ANY, ANY), 'запис')
    ),
)
@patch('love_bot.files.safe_send_message', autospec=True)
@patch('love_bot.files.config.logger')
async def test_safe_open_file_with_retryable_os_error(
    mock_logger: MagicMock,
    mock_safe_send: AsyncMock,
    exception: Exception,
    tested_func: Callable,
    args: tuple,
    phrase_is_contained: str,
) -> None:
    with (
        patch('builtins.open', side_effect=exception),
        pytest.raises(OSError),
    ):
        tested_func(*args)
    assert len(mock_logger.method_calls) == config.FILE_OPENING_ATTEMPTS_LIMIT
    mock_safe_send.assert_called_once()
    chat_id, error_message = mock_safe_send.call_args.args
    assert chat_id == config.MY_ID
    assert phrase_is_contained in error_message


@pytest.mark.asyncio
@patch('love_bot.files.safe_send_message', autospec=True)
async def test_safe_read_empty_file(mock_safe_send: AsyncMock) -> None:
    with (
        patch('builtins.open', new_callable=mock_open),
        pytest.raises(EmptyFileError)
    ):
        safe_read_file(ANY)
    mock_safe_send.assert_called_once_with(config.MY_ID, ANY)
