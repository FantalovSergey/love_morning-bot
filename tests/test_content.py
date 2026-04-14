import pytest

from love_bot import content


def test_read_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello\nworld\n")
    assert content.get_content_from_file(str(file)) == ["hello\n", "world\n"]


def test_get_content_file_not_found(tmp_path):
    path = tmp_path / "missing.txt"
    assert content.get_content_from_file(str(path)) == []


@pytest.mark.asyncio
async def test_no_messages(mocker):
    mocker.patch("love_bot.content.get_content_from_file", return_value=[])
    send_mock = mocker.patch("love_bot.content.safe_send_message")
    await content.send_love_message()
    send_mock.assert_called_once()


@pytest.mark.asyncio
async def test_write_content(tmp_path, message_mock, mocker):
    file = tmp_path / "file.txt"
    send_mock = mocker.patch("love_bot.content.safe_send_message")
    await content.write_content(message_mock, str(file))
    assert file.read_text() == "test\n"
    send_mock.assert_called_once()


@pytest.mark.asyncio
async def test_delete_content(tmp_path, message_mock, state_mock, mocker):
    file = tmp_path / "file.txt"
    file.write_text("a\nb\nc\n")
    message_mock.text = "2"
    mocker.patch("love_bot.content.get_indexes", return_value=[2])
    mocker.patch("love_bot.content.safe_send_message")
    mocker.patch("love_bot.content.show_content")
    await content.delete_content(message_mock, state_mock, str(file), None)
    assert file.read_text() == "a\nc\n"
