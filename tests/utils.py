from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State


async def assert_state(
    dispatcher: Dispatcher,
    bot: Bot,
    chat_id: int,
    expected_state: State | None,
) -> None:
    """Проверяет, что fsm в чате с пользователем корректен."""
    context = dispatcher.fsm.get_context(bot, chat_id, user_id=chat_id)
    state = await context.get_state()
    assert state == expected_state, f'assert {state} == {expected_state}'
