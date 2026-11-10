from unittest.mock import MagicMock, patch

import pytest

from love_bot.core.exceptions import (
    EmptyRequestError, TooLongContentMessageError,
)
from love_bot.validators import (
    validate_request_text_is_not_none, validate_writing_request,
)


@patch('love_bot.validators.telegram_logging')
def test_validate_request_text_is_not_none(
    mock_logging: MagicMock,
) -> None:
    with pytest.raises(EmptyRequestError):
        validate_request_text_is_not_none(request_text=None)
    mock_logging.assert_called_once()


@patch('love_bot.validators.telegram_logging')
def test_validate_writing_request(
    mock_logging: MagicMock, too_long_message: str, symbol_exceeding: int,
) -> None:
    with pytest.raises(TooLongContentMessageError) as exception_info:
        validate_writing_request(too_long_message)
    assert exception_info.value.symbol_limit_exceeding == symbol_exceeding
    mock_logging.assert_called_once()


@patch('love_bot.validators.telegram_logging')
def test_validate_writing_request_text_is_not_none(
    mock_logging: MagicMock,
) -> None:
    with pytest.raises(EmptyRequestError):
        validate_writing_request(request_text=None)
    mock_logging.assert_called_once()
