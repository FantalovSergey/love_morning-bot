from collections.abc import AsyncIterator
from datetime import datetime

import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State
from aiogram.types import Chat, Message, Update, User

from love_bot.core import config
from love_bot.dispatcher import dispatcher as dp
from tests.types import DispatcherFactory, UpdateFactory


@pytest_asyncio.fixture
async def dispatcher(bot: Bot) -> Dispatcher:
    for chat_id in (config.ARINA_ID, config.MY_ID):
        context = dp.fsm.get_context(bot, chat_id, user_id=chat_id)
        await context.clear()
    return dp


@pytest.fixture
def get_dispatcher_with_state(
    dispatcher: Dispatcher, bot: Bot,
) -> DispatcherFactory:
    """Диспетчер с состоянием для определённого пользователя."""
    async def factory(
        chat_id: int, state: State = State('test'),
    ) -> Dispatcher:
        context = dispatcher.fsm.get_context(bot, chat_id, user_id=chat_id)
        await context.set_state(state)
        return dispatcher
    return factory


@pytest_asyncio.fixture
async def bot() -> AsyncIterator[Bot]:
    bot = Bot('1:TEST_TOKEN')
    yield bot
    await bot.session.close()


@pytest.fixture
def make_update(
    chat_id: int, text_message: str, received_message_id: int,
) -> UpdateFactory:
    """Апдейт в виде текстового сообщения в чате с пользователем."""
    def factory(
        chat_id: int = chat_id, text_message: str = text_message,
    ) -> Update:
        return Update(
            update_id=1,
            message=Message(
                message_id=received_message_id,
                date=datetime.now(),
                text=text_message,
                from_user=User(id=chat_id, is_bot=False, first_name='Test'),
                chat=Chat(id=chat_id, type='private'),
            ),
        )
    return factory


@pytest.fixture
def message(sent_message_id: int, chat_id: int) -> Message:
    return Message(
        message_id=sent_message_id,
        date=datetime.now(),
        chat=Chat(id=chat_id, type='private'),
    )


@pytest.fixture
def received_message_id() -> int:
    return 1


@pytest.fixture
def chat_id() -> int:
    return 1


@pytest.fixture
def text_message() -> str:
    return 'test'


@pytest.fixture
def sent_message_id() -> int:
    return 10


@pytest.fixture
def sent_message_ids() -> list[int]:
    return [10, 20]


@pytest.fixture
def repr_content(sent_message_ids: list[int]) -> list[str]:
    """
    Возвращает список отправляемых сообщений,
    количество которых соответствует количеству message_ids.
    """
    return [
        f'{index}. test{index}\n'
        for index in range(1, len(sent_message_ids) + 1)
    ]


@pytest.fixture
def too_long_message(symbol_exceeding: int) -> str:
    return 'a' * (config.WRITING_CONTENT_SYMBOL_LIMIT + symbol_exceeding)


@pytest.fixture
def symbol_exceeding() -> int:
    return 1
