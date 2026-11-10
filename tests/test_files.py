from typing import Callable
from unittest.mock import ANY, AsyncMock, MagicMock, mock_open, patch

import pytest

from love_bot.core import config
from love_bot.core.exceptions import EmptyFileError
from love_bot.files import (
    RETRYABLE_EXEPTIONS, safe_read_file, safe_write_in_file,
)

READING = 'чтени'
WRITING = 'запис'
EMPTY = 'пуст'


@pytest.mark.asyncio
@pytest.mark.parametrize('exception', (FileNotFoundError(), OSError()))
@pytest.mark.parametrize(
    ('tested_func', 'args', 'phrase_is_contained'),
    (
        (safe_read_file, (ANY,), READING),
        (safe_write_in_file, 3 * (ANY,), WRITING)
    ),
)
@patch('love_bot.files.telegram_logging')
@patch.object(config.logger, 'exception')
async def test_safe_open_file_with_not_retryable_os_error(
    mock_logger: MagicMock,
    mock_telegram_logging: MagicMock,
    exception: Exception,
    tested_func: Callable,
    args: tuple,
    phrase_is_contained: str,
) -> None:
    with (
        patch('builtins.open', side_effect=exception),
        pytest.raises(OSError),
    ):
        await tested_func(*args)
    if not isinstance(exception, FileNotFoundError):
        mock_logger.assert_called_once()
    mock_telegram_logging.assert_called_once()
    error_message = mock_telegram_logging.call_args.args[0]
    assert phrase_is_contained in error_message.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'exception',
    [OSError(error_number, '') for error_number in RETRYABLE_EXEPTIONS],
)
@pytest.mark.parametrize(
    ('tested_func', 'args', 'phrase_is_contained'),
    (
        (safe_read_file, (ANY,), READING),
        (safe_write_in_file, 3 * (ANY,), WRITING)
    ),
)
@patch('love_bot.files.telegram_logging', autospec=True)
@patch('love_bot.files.asyncio.sleep', autospec=True)
@patch('love_bot.files.config.logger')
async def test_safe_open_file_with_retryable_os_error(
    mock_logger: MagicMock,
    mock_sleep: AsyncMock,
    mock_telegram_logging: MagicMock,
    exception: Exception,
    tested_func: Callable,
    args: tuple,
    phrase_is_contained: str,
) -> None:
    with (
        patch('builtins.open', side_effect=exception),
        pytest.raises(OSError),
    ):
        await tested_func(*args)
    assert len(mock_logger.method_calls) == config.OPENING_ATTEMPTS_LIMIT
    assert mock_sleep.await_count == config.OPENING_ATTEMPTS_LIMIT - 1
    mock_telegram_logging.assert_called_once()
    error_message = mock_telegram_logging.call_args.args[0]
    assert phrase_is_contained in error_message.lower()


@pytest.mark.asyncio
@patch('love_bot.files.telegram_logging')
@patch('builtins.open', new_callable=mock_open)
async def test_safe_read_empty_file(
    mock_open_file: MagicMock, mock_telegram_logging: MagicMock, filepath: str,
) -> None:
    with pytest.raises(EmptyFileError):
        await safe_read_file(filepath)
    mock_open_file.assert_called_once_with(filepath, encoding='utf-8')
    mock_open_file().readlines.assert_called_once()
    mock_telegram_logging.assert_called_once()
    error_message = mock_telegram_logging.call_args.args[0]
    assert EMPTY in error_message.lower()


@pytest.mark.asyncio
@patch('builtins.open', new_callable=mock_open)
async def test_safe_write_file_one_time(
    mock_open_file: MagicMock,
    filepath: str,
    file_open_mode: str,
    file_content: str,
) -> None:
    await safe_write_in_file(filepath, file_open_mode, file_content)
    mock_open_file.assert_called_once_with(
        filepath, file_open_mode, encoding='utf-8',
    )
    mock_open_file().writelines.assert_called_once_with(file_content)
