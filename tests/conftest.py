from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message


@pytest.fixture
def message():
    msg = MagicMock(spec=Message)
    msg.text = "test text"
    msg.message_id = 111
    msg.chat = SimpleNamespace(id=123)
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def state():
    st = AsyncMock()
    st.clear = AsyncMock()
    st.set_state = AsyncMock()
    return st
