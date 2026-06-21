from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from love_bot import config
from love_bot.content import (
    delete_content, get_content_from_file, send_love_message, show_content,
    write_content,
)


@patch('builtins.open', new_callable=mock_open, read_data='hello\nworld\n')
def test_get_content_from_file_success(mocked_open):
    result = get_content_from_file('test.txt')
    assert result == ['hello\n', 'world\n']
    mocked_open.assert_called_once_with('test.txt', encoding='utf-8')


@patch('builtins.open', side_effect=FileNotFoundError)
def test_get_content_from_file_not_found(mocked_open):
    with patch.object(config.logger, 'error') as mock_logger:
        result = get_content_from_file('missing.txt')
    assert result == []
    mock_logger.assert_called_once()


@patch('builtins.open', new_callable=mock_open, read_data='')
def test_get_content_from_file_empty_love_messages(mocked_open):
    with patch.object(config.logger, 'error') as mock_logger:
        result = get_content_from_file(config.LOVE_MESSAGES_FILEPATH)
    assert result == []
    mock_logger.assert_called_once()


@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@patch('builtins.open', new_callable=mock_open)
@pytest.mark.asyncio
async def test_write_content(mocked_open, mock_send, message):
    message.text = 'hello\nworld'
    await write_content(message, 'test.txt')
    mocked_open.assert_called_once_with('test.txt', 'a', encoding='utf-8')
    handle = mocked_open()
    handle.writelines.assert_called_once_with(('hello world\n',))
    mock_send.assert_awaited_once()


@patch('love_bot.content.get_content_from_file', return_value=[])
@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_send_love_message_empty_file(mock_send, mock_get_content):
    await send_love_message()
    mock_send.assert_awaited_once()


@patch('love_bot.content.choice', return_value='Доброе утро ❤️')
@patch(
    'love_bot.content.get_content_from_file', return_value=['Доброе утро ❤️'],
)
@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_send_love_message_morning(
    mock_send, mock_get_content, mock_choice,
):
    fake_datetime = MagicMock()
    fake_datetime.now.return_value = datetime(2025, 1, 1, 8, 0)
    with patch('love_bot.content.datetime', fake_datetime):
        await send_love_message()
    mock_send.assert_awaited_once()
    sent_text = mock_send.await_args.args[1]
    assert 'Доброе утро' in sent_text


@patch('love_bot.content.choice', return_value='Доброе утро ❤️')
@patch(
    'love_bot.content.get_content_from_file', return_value=['Доброе утро ❤️'],
)
@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_send_love_message_evening_replace(
    mock_send, mock_get_content, mock_choice,
):
    fake_datetime = MagicMock()
    fake_datetime.now.return_value = datetime(2025, 1, 1, 18, 0)
    with patch('love_bot.content.datetime', fake_datetime):
        await send_love_message()
    sent_text = mock_send.await_args.args[1]
    assert 'Добрый вечер' in sent_text


@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_show_content_empty(mock_send, message):
    mock_send.return_value = 'msg'
    result = await show_content(message, [])
    assert result == ['msg']
    mock_send.assert_awaited_once()


@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_show_content_single_chunk(mock_send, message):
    mock_send.return_value = 'msg'
    content = ['hello\n', 'world\n']
    result = await show_content(message, content)
    assert result == ['msg']
    sent_text = mock_send.await_args.args[1]
    assert '1. hello' in sent_text
    assert '2. world' in sent_text


@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_show_content_multiple_chunks(mock_send, message):
    mock_send.side_effect = ['msg1', 'msg2']
    with patch.object(config, 'FROM_BOT_MESSAGE_SYMBOL_LIMIT', 10):
        content = ['123456\n', '123456\n']
        result = await show_content(message, content)
    assert result == ['msg1', 'msg2']
    assert mock_send.await_count == 2


@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_show_content_forwards_Arina_request(mock_send, message):
    message.chat.id = config.ARINA_ID
    config.bot.forward_message = AsyncMock()
    mock_send.return_value = 'msg'
    await show_content(message, ['hello\n'])
    config.bot.forward_message.assert_awaited_once()


@patch('love_bot.content.get_indexes', return_value=[1])
@patch('love_bot.content.get_content_from_file', return_value=['a\n', 'b\n'])
@patch('love_bot.content.show_content', new_callable=AsyncMock)
@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@patch('builtins.open', new_callable=mock_open)
@pytest.mark.asyncio
async def test_delete_content_success(
    mocked_open, mock_send, mock_show, mock_get_content, mock_get_indexes,
    message, state,
):
    await delete_content(message, state, 'test.txt', keyboard=None)
    state.clear.assert_awaited_once()
    handle = mocked_open()
    handle.writelines.assert_called_once_with(['b\n'])
    mock_show.assert_awaited_once()
    mock_send.assert_awaited_once()


@patch('love_bot.content.get_indexes', side_effect=ValueError)
@patch('love_bot.content.safe_send_message', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_delete_content_invalid_indexes(
    mock_send, mock_indexes, message, state,
):
    await delete_content(message, state, 'test.txt', keyboard=None)
    mock_send.assert_awaited_once()
    state.clear.assert_not_awaited()
