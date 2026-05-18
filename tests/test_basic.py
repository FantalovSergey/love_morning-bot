from unittest.mock import AsyncMock, patch

import pytest

from love_bot.handlers.basic import cancel, start
from love_bot import config, keyboards


@pytest.mark.asyncio
async def test_start_for_owner(message, state):
    message.chat.id = config.MY_ID

    await start(message, state)

    state.clear.assert_awaited_once()

    message.answer.assert_awaited_once_with(
        "🖐️",
        reply_markup=keyboards.my_keyboard,
    )


@pytest.mark.asyncio
@patch("love_bot.handlers.basic.safe_send_message", new_callable=AsyncMock)
async def test_start_for_Arina(mock_send, message, state):
    message.chat.id = config.ARINA_ID

    await start(message, state)

    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch("love_bot.handlers.basic.safe_send_message", new_callable=AsyncMock)
async def test_cancel(mock_send, message, state):
    message.chat.id = config.MY_ID

    await cancel(message, state)

    state.clear.assert_awaited_once()

    mock_send.assert_awaited_once()
