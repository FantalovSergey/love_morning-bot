import asyncio

from love_bot.core import config
from love_bot.core.utils import safe_send_message
from love_bot.dispatcher import dispatcher
from love_bot.tasks import wish_good_morning


async def main() -> None:
    """
    Запускает отправку утренних сообщений, поллинг бота
    и уведомляет меня об успешном запуске в Telegram.
    """
    await asyncio.gather(
        wish_good_morning(),
        dispatcher.start_polling(config.bot),
        safe_send_message(config.MY_ID, 'Бот запущен'),
    )


if __name__ == '__main__':
    asyncio.run(main())
