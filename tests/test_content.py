from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from love_bot.content import delete_content, write_content
from love_bot.core.exceptions import NoContentForDeletingError


@pytest.mark.asyncio
@patch('love_bot.content.safe_write_in_file', autospec=True)
async def test_write_content(
    mock_write_in_file: AsyncMock, filepath: str,
) -> None:
    await write_content(filepath, text='hello\n\nworld')
    mock_write_in_file.assert_awaited_once_with(
        filepath, mode='a', content=('hello  world\n',),
    )


@pytest.mark.asyncio
@patch('love_bot.content.telegram_logging')
@patch('love_bot.content.safe_write_in_file', autospec=True)
async def test_delete_content_with_out_of_range_indexes(
    mock_write_in_file: AsyncMock, mock_logging: MagicMock, filepath: str,
) -> None:
    with (
        patch('love_bot.content.safe_read_file', return_value=['test1']),
        pytest.raises(NoContentForDeletingError),
    ):
        await delete_content(filepath, index_ranges='2')
    mock_write_in_file.assert_not_awaited()
    mock_logging.assert_called_once()


@pytest.mark.asyncio
@patch('love_bot.content.safe_write_in_file', autospec=True)
@patch(
    'love_bot.content.safe_read_file',
    autospec=True,
    return_value=['test1', 'test2'],
)
async def test_delete_content(
    mock_read_file: AsyncMock,
    mock_write_in_file: AsyncMock,
    filepath: str,
) -> None:
    deleted_content = await delete_content(filepath, index_ranges='2')
    mock_read_file.assert_awaited_once_with(filepath)
    mock_write_in_file.assert_awaited_once_with(
        filepath, mode='w', content=['test1'],
    )
    assert deleted_content == ['1. `test2`']
