import pytest

from love_bot import config, content


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
    mock_send = mocker.patch("love_bot.content.safe_send_message")
    await content.send_love_message()
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_write_content(tmp_path, message_mock, mocker):
    file = tmp_path / "file.txt"
    mock_send = mocker.patch("love_bot.content.safe_send_message")
    await content.write_content(message_mock, str(file))
    assert file.read_text() == "test\n"
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_show_content_empty(message_mock, mocker):
    message_mock.chat.id = 123
    sent_message_id = 777
    mock_send = mocker.patch(
        "love_bot.content.safe_send_message",
        new_callable=mocker.AsyncMock,
        side_effect=[sent_message_id, None],
    )
    mocker.patch(
        "love_bot.content.asyncio.sleep", new_callable=mocker.AsyncMock,
    )
    mock_delete = mocker.patch.object(
        config.bot, "delete_messages", new_callable=mocker.AsyncMock,
    )
    await content.show_content(message_mock, [])
    assert mock_send.call_args_list[0].args == (123, 'Пуфто, ничего нет🙃')
    mock_delete.assert_awaited_once_with(123, [sent_message_id])
    assert mock_send.call_args_list[1].args == (
        123,
        'Я показал, а потом удалив, штобы никто не подсмотрел🐻',
    )


@pytest.mark.asyncio
async def test_show_content_forward_request_from_Arina(message_mock, mocker):
    message_mock.chat.id = config.ARINA_ID
    message_mock.message_id = 555
    mocker.patch(
        "love_bot.content.safe_send_message",
        new_callable=mocker.AsyncMock,
        return_value=1,
    )
    mocker.patch(
        "love_bot.content.asyncio.sleep", new_callable=mocker.AsyncMock,
    )
    mock_forward = mocker.patch.object(
        config.bot, "forward_message", new_callable=mocker.AsyncMock,
    )
    mocker.patch.object(
        config.bot, "delete_messages", new_callable=mocker.AsyncMock,
    )
    await content.show_content(message_mock, ["hello\n"])
    mock_forward.assert_awaited_once_with(
        chat_id=config.MY_ID, from_chat_id=config.ARINA_ID, message_id=555,
    )


@pytest.mark.asyncio
async def test_show_content_split_into_chunks(message_mock, mocker):
    message_mock.chat.id = 123
    mocker.patch.object(config, "FROM_BOT_MESSAGE_SYMBOL_LIMIT", 10)
    mock_send = mocker.patch(
        "love_bot.content.safe_send_message",
        new_callable=mocker.AsyncMock,
        side_effect=[1, 2, None],
    )
    mocker.patch(
        "love_bot.content.asyncio.sleep", new_callable=mocker.AsyncMock,
    )
    mock_delete = mocker.patch.object(
        config.bot, "delete_messages", new_callable=mocker.AsyncMock,
    )
    messages = ["12345\n", "67890\n"]
    await content.show_content(message_mock, messages)
    assert mock_send.await_count == 3
    mock_delete.assert_awaited_once_with(123, [1, 2])


@pytest.mark.asyncio
async def test_show_content_success(message_mock, mocker):
    message_mock.chat.id = 123
    mock_send = mocker.patch(
        "love_bot.content.safe_send_message",
        new_callable=mocker.AsyncMock,
        side_effect=[999, None],
    )
    mocker.patch(
        "love_bot.content.asyncio.sleep", new_callable=mocker.AsyncMock,
    )
    mock_delete = mocker.patch.object(
        config.bot, "delete_messages", new_callable=mocker.AsyncMock,
    )
    messages = ["hello\n", "world\n"]
    await content.show_content(message_mock, messages)
    assert mock_send.call_args_list[0].args == (123, "1. hello\n2. world\n")
    mock_delete.assert_awaited_once_with(123, [999])


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
