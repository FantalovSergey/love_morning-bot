from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from love_bot.content import delete_content, write_content
from love_bot.core import config
from love_bot.core.exceptions import NoContentForDeletingError


@patch('love_bot.content.safe_write_in_file', autospec=True)
def test_write_content(mock_write_in_file: MagicMock) -> None:
    write_content(filepath=ANY, text='hello\n\nworld')
    mock_write_in_file.assert_called_once_with(
        filepath=ANY, mode='a', content=('hello  world\n',),
    )


@pytest.mark.asyncio
@patch('love_bot.content.safe_send_message', autospec=True)
async def test_delete_content_with_out_of_range_indexes(
    mock_safe_send: AsyncMock,
) -> None:
    with (
        patch('love_bot.content.safe_read_file', return_value=['test1']),
        pytest.raises(NoContentForDeletingError),
    ):
        delete_content(filepath=ANY, index_ranges='2')
    mock_safe_send.assert_called_once_with(config.MY_ID, ANY)


@patch('love_bot.content.safe_write_in_file', autospec=True)
def test_delete_content(mock_write_in_file: MagicMock) -> None:
    with patch(
        'love_bot.content.safe_read_file', return_value=['test1', 'test2'],
    ):
        deleted_content = delete_content(filepath=ANY, index_ranges='2')
    mock_write_in_file.assert_called_once_with(
        filepath=ANY, mode='w', content=['test1'],
    )
    assert deleted_content == ['1. test2']
