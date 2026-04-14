import pytest

from love_bot import config, keyboards
from love_bot.handlers.basic import start, cancel


@pytest.mark.asyncio
async def test_start_for_me(message_mock, state_mock):
    message_mock.chat.id = config.MY_ID
    await start(message_mock, state_mock)
    message_mock.answer.assert_called_once_with(
        '🖐️', reply_markup=keyboards.my_keyboard
    )
    state_mock.clear.assert_called_once()


@pytest.mark.asyncio
async def test_start_for_Arina(message_mock, state_mock, mocker):
    mock_send = mocker.patch("love_bot.handlers.basic.safe_send_message")
    await start(message_mock, state_mock)
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_cancel(message_mock, state_mock, mocker):
    mock_send = mocker.patch("love_bot.handlers.basic.safe_send_message")
    await cancel(message_mock, state_mock)
    mock_send.assert_called_once()
    state_mock.clear.assert_called_once()
