from aiogram import Dispatcher

from love_bot.core import config
from love_bot.core.middlewares import AccessMiddleware
from love_bot.handlers.routers import (
    basic_router,
    fsm_router,
    operations_launching_router,
    simple_messages_router,
)


def build_dispatcher() -> Dispatcher:
    """
    Создаёт объект Dispatcher с middleware
    для ограничения доступа посторонних пользователей
    и подключает к нему роутеры.
    """
    dispatcher = Dispatcher()
    dispatcher.message.outer_middleware(
        AccessMiddleware(config.ARINA_ID, config.MY_ID),
    )
    dispatcher.include_routers(
        basic_router,
        fsm_router,
        operations_launching_router,
        simple_messages_router,
    )
    return dispatcher


dispatcher = build_dispatcher()
