from unittest.mock import AsyncMock, mock_open, patch

import pytest

from love_bot.content import (
    delete_content,
    get_content_from_file,
)


@patch("builtins.open", new_callable=mock_open, read_data="a\nb\n")
def test_get_content_from_file(_):
    result = get_content_from_file("test.txt")

    assert result == ["a\n", "b\n"]


@patch("love_bot.content.get_indexes")
@patch("love_bot.content.get_content_from_file")
@patch("love_bot.content.show_content", new_callable=AsyncMock)
@patch("love_bot.content.safe_send_message", new_callable=AsyncMock)
@patch("builtins.open", new_callable=mock_open)
@pytest.mark.asyncio
async def test_delete_content(
    mocked_open,
    mock_send,
    mock_show,
    mock_get_content,
    mock_get_indexes,
    message,
    state,
):
    mock_get_indexes.return_value = [1]
    mock_get_content.return_value = ["a\n", "b\n"]

    await delete_content(
        message,
        state,
        "test.txt",
        keyboard=None,
    )

    state.clear.assert_awaited_once()

    mocked_open.assert_called_once_with(
        "test.txt",
        "w",
        encoding="utf-8",
    )
