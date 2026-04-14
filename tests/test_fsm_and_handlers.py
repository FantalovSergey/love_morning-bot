import pytest
from love_morning import cancel, start
from love_bot import config


@pytest.mark.asyncio
async def test_start_for_me(fake_message, fake_state, mocker):
    fake_message.chat.id = config.MY_ID
    await start(fake_message, fake_state)
    fake_message.answer.assert_called_once()
    fake_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_cancel(fake_message, fake_state, mocker):
    send_mock = mocker.patch("love_morning.safe_send_message")
    await cancel(fake_message, fake_state)
    send_mock.assert_called_once()
    fake_state.clear.assert_called_once()
