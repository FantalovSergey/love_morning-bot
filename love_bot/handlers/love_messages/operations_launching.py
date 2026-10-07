from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.content import list_content, retrieve_content
from love_bot.core import config, keyboards, templates
from love_bot.core.states import LoveMessagesDeleting
from love_bot.core.utils import (
    get_message_with_right_greeting, safe_send_message,
)
from love_bot.handlers.routers import operations_launching_router
from love_bot.tasks import delete_messages_after_content_showing


@operations_launching_router.message(
    F.text == keyboards.GET_CUTENESS, F.chat.id == config.ARINA_ID,
)
async def send_cuteness_immediately(request: Message) -> None:
    """Ответ на нажатие Ариной кнопки 'Получить милоту ...'."""
    await safe_send_message(
        config.ARINA_ID,
        get_message_with_right_greeting(
            retrieve_content(config.LOVE_MESSAGES_FILEPATH),
        ),
        request.message_id,
    )


@operations_launching_router.message(F.text == keyboards.SHOW_MESSAGES)
async def show_all_love_messages(request: Message) -> None:
    """
    Ответ на нажатие кнопки 'Посмотреть сообщения'.\n
    Мне – все любовные сообщения из файла, Арине – предупреждение.
    По прошествии определённого времени отправленные сообщения исчезают.
    """
    if request.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            templates.SHOW_ARINA_ALL_LOVE_MESSAGE_RESPONSE,
            request.message_id,
        )
        return
    message_ids: list[int] = []
    for message in list_content(config.LOVE_MESSAGES_FILEPATH):
        message_id = await safe_send_message(config.MY_ID, message)
        if message_id is None:
            break
        message_ids.append(message_id)
    await delete_messages_after_content_showing(config.MY_ID, message_ids)


@operations_launching_router.message(F.text == keyboards.DELETE_MESSAGES)
async def start_love_messages_deleting(
    request: Message, state: FSMContext,
) -> None:
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов, Арине – предупреждение.
    Показываются все любовные сообщения с индексами,
    которые по прошествии определённого времени исчезают.
    """
    if request.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            templates.DELETE_LOVE_MESSAGES_BY_ARINA_RESPONSE,
            request.message_id,
        )
        return
    message_ids: list[int] = []
    for message in list_content(config.LOVE_MESSAGES_FILEPATH):
        message_id = await safe_send_message(config.MY_ID, message)
        if message_id is None:
            break
        message_ids.append(message_id)
    else:
        await state.set_state(LoveMessagesDeleting.indexes_waiting)
        await safe_send_message(
            config.MY_ID,
            templates.LOVE_MESSAGES_DELETING_INVITE,
            keyboard=keyboards.cancel,
        )
    await delete_messages_after_content_showing(config.MY_ID, message_ids)
