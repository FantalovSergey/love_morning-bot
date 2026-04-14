import pytest
from unittest.mock import AsyncMock, MagicMock

from love_bot.middlewares import AccessMiddleware


@pytest.mark.asyncio
async def test_access_denied():
    middleware = AccessMiddleware((1,))
    handler = AsyncMock()
    event = MagicMock()
    event.message.chat.id = 2
    event.message.answer = AsyncMock()
    await middleware(handler, event, {})
    handler.assert_not_called()
    event.message.answer.assert_called_once()
