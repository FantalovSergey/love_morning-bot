from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from love_bot.core import config
from love_bot.core.exceptions import (
    EmptyRequestError, TooLongContentMessageError,
)
from love_bot.validators import (
    validate_request_text_is_not_none, validate_writing_request,
)


@pytest.mark.asyncio
@patch('love_bot.validators.safe_send_message', autospec=True)
async def test_validate_request_text_is_not_none(
    mock_safe_send: AsyncMock,
) -> None:
    with pytest.raises(EmptyRequestError):
        validate_request_text_is_not_none(request_text=None)
    mock_safe_send.assert_called_once_with(config.MY_ID, ANY)


@pytest.mark.asyncio
@patch('love_bot.validators.safe_send_message', autospec=True)
async def test_validate_writing_request(
    mock_safe_send: AsyncMock, too_long_message: str, symbol_exceeding: int,
) -> None:
    with pytest.raises(TooLongContentMessageError) as exception_info:
        validate_writing_request(too_long_message)
    assert exception_info.value.symbol_limit_exceeding == symbol_exceeding
    mock_safe_send.assert_called_once_with(config.MY_ID, ANY)


@pytest.mark.asyncio
@patch('love_bot.validators.safe_send_message', autospec=True)
async def test_validate_writing_request_text_is_not_none(
    mock_validate_is_not_none: MagicMock,
) -> None:
    with pytest.raises(EmptyRequestError):
        validate_writing_request(request_text=None)
    mock_validate_is_not_none.assert_called_once()
