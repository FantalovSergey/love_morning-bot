import pytest

from love_bot.utils import get_indexes, safe_send_message


def test_single_indexes():
    assert get_indexes("1, 2, 3") == [1, 2, 3]


def test_ranges():
    assert get_indexes("1-3") == [1, 2, 3]


def test_mixed():
    assert get_indexes("1, 3-5") == [1, 3, 4, 5]


def test_invalid():
    with pytest.raises(ValueError):
        get_indexes("abc")


@pytest.mark.asyncio
async def test_send_success(mock_bot):
    mock_bot.send_message.return_value.message_id = 10
    await safe_send_message(1, "hello")
    mock_bot.send_message.assert_called_once()
