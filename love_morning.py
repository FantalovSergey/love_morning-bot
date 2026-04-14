import asyncio

from love_bot import config
from love_bot.content import wish_good_morning
from love_bot.handlers.basic import basic_router
from love_bot.handlers.fsm import fsm_router
from love_bot.handlers.simple_messages import simple_messages_router
from love_bot.handlers.starting_operations import starting_operations_router
from love_bot.utils import safe_send_message


async def main():
    config.dispatcher.include_routers(
        basic_router, fsm_router, starting_operations_router,
        simple_messages_router,
    )
    await asyncio.gather(
        wish_good_morning(),
        config.dispatcher.start_polling(config.bot),
        safe_send_message(config.MY_ID, 'Бот запущен'),
    )


if __name__ == '__main__':
    asyncio.run(main())
