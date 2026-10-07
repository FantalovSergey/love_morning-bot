import asyncio
from datetime import datetime
from typing import NoReturn

from love_bot.content import retrieve_content
from love_bot.core import config, templates
from love_bot.core.utils import safe_send_message


async def wish_good_morning() -> NoReturn:
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(config.TZ)
        delta = now.replace(**config.SENDING_TIME, tzinfo=config.TZ) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        await safe_send_message(
            config.ARINA_ID, retrieve_content(config.LOVE_MESSAGES_FILEPATH),
        )
        await asyncio.sleep(1)


async def delete_messages_after_content_showing(
    chat_id: int, message_ids: list[int],
) -> None:
    """Удаление сообщений с контентом через некоторое время."""
    await asyncio.sleep(config.CONTENT_SHOWING_PERIOD)
    while len(message_ids) > 1:
        await config.bot.delete_messages(
            chat_id, message_ids[1:config.DELETING_MESSAGE_COUNT_LIMIT + 1],
        )
        del message_ids[1:config.DELETING_MESSAGE_COUNT_LIMIT + 1]
    await config.bot.edit_message_text(
        templates.AFTER_DELETING_NOTIFICATION,
        chat_id=chat_id,
        message_id=message_ids[0],
    )
