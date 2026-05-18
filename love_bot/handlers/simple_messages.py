from aiogram import F, Router
from aiogram.types import Message

from .. import config, keyboards
from ..content import (
    get_content_from_file, send_love_message, show_content, write_content,
)
from ..utils import delete_messages_after_showing_content, safe_send_message

simple_messages_router = Router()


@simple_messages_router.message(
    F.text == keyboards.GET_CUTENESS, F.chat.id == config.ARINA_ID,
)
async def send_cuteness_immediately(request: Message):
    """Ответ на нажатие Ариной кнопки 'Получить милоту райт нау!!'"""
    await send_love_message(request.message_id)


@simple_messages_router.message(F.text == keyboards.SHOW_MESSAGES)
async def show_all_love_messages(request: Message):
    """
    Ответ на нажатие кнопки 'Посмотреть сообщения'.\n
    Мне – все любовные сообщения из файла, Арине – предупреждение.
    """
    if request.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Вы делаете что-то незаконное🤔',
            request.message_id,
        )
        return
    await delete_messages_after_showing_content(
        config.MY_ID,
        await show_content(
            request, get_content_from_file(config.LOVE_MESSAGES_FILEPATH),
        )
    )


@simple_messages_router.message(F.text == keyboards.SHOW_DREAMS)
async def show_all_dreams(request: Message):
    """Ответ на нажатие кнопки 'Посмотреть все сны😴'."""
    await delete_messages_after_showing_content(
        request.chat.id,
        await show_content(
            request, get_content_from_file(config.DREAMS_FILEPATH),
        ),
    )


@simple_messages_router.message()
async def handle_message(request: Message):
    """Обработка прочих сообщений.\n
    Моё сообщение сохраняется в файл как любовное.
    Сообщение Арины пересылается мне.
    """
    if request.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID, 'Сообщение отправлено☺️', request.message_id,
        )
        return
    await write_content(request, config.LOVE_MESSAGES_FILEPATH)
