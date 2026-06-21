from unittest.mock import AsyncMock

import pytest

from love_bot.middlewares import AccessMiddleware


@pytest.mark.asyncio
async def test_access_middleware_denies_unknown_user(message):
    middleware = AccessMiddleware(1, 2, 3)
    handler = AsyncMock()
    message.chat_id = 999
    result = await middleware(handler, event=message, data={})
    assert result is None
    handler.assert_not_called()
    message.answer.assert_awaited_once()
