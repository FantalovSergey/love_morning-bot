import pytest

from love_bot import content


def test_read_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello\nworld\n")
    result = content.get_content_from_file(str(file))
    assert result == ["hello\n", "world\n"]


@pytest.mark.asyncio
async def test_no_messages(mocker):
    mocker.patch("love_bot.content.get_content_from_file", return_value=[])
    send_mock = mocker.patch("love_bot.content.safe_send_message")
    await content.send_love_message()
    send_mock.assert_called_once()


@pytest.mark.asyncio
async def test_write_content(tmp_path, fake_message, mocker):
    file = tmp_path / "file.txt"
    send_mock = mocker.patch("love_bot.content.safe_send_message")
    await content.write_content(fake_message, str(file))
    assert file.read_text() == "test\n"
    send_mock.assert_called_once()


@pytest.mark.asyncio
async def test_delete_content(tmp_path, fake_message, fake_state, mocker):
    file = tmp_path / "file.txt"
    file.write_text("a\nb\nc\n")
    fake_message.text = "2"
    mocker.patch("love_bot.content.get_indexes", return_value=[2])
    mocker.patch("love_bot.content.safe_send_message")
    mocker.patch("love_bot.content.show_content")
    await content.delete_content(fake_message, fake_state, str(file), None)
    assert file.read_text() == "a\nc\n"
