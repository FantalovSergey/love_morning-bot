import asyncio
from datetime import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot import config, keyboards
from love_bot.content import (
    delete_content, get_content_from_file, send_love_message, show_content,
    write_content,
)
from love_bot.fsms import (
    DeleteDreams, DeleteLoveMessages, SendNoteForArina, WriteDream,
)
from love_bot.utils import safe_send_message


async def wish_good_morning():
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(config.TZ)
        delta = now.replace(**config.SENDING_TIME) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        await send_love_message()
        await asyncio.sleep(1)


@config.dispatcher.message(Command("start"))
async def start(message: Message, state: FSMContext):
    """
    Ответ на команду /start.\n
    Можно использовать для сброса FSM.
    """
    await state.clear()
    if message.chat.id == config.MY_ID:
        await message.answer('🖐️', reply_markup=keyboards.my_keyboard)
        return
    await safe_send_message(
        config.ARINA_ID,
        config.START_MESSAGE,
        keyboards.Arina_keyboard,
        request_message_id=message.message_id,
    )


@config.dispatcher.message(F.text == keyboards.CANCEL)
async def cancel(message: Message, state: FSMContext):
    """Отмена ранее выбранного действия."""
    await safe_send_message(
        message.chat.id,
        'Есть "Отмена"🫡',
        (
            keyboards.Arina_keyboard if message.chat.id == config.ARINA_ID else
            keyboards.my_keyboard
        ),
        request_message_id=message.message_id,
    )
    await state.clear()


@config.dispatcher.message(WriteDream.dream)
async def write_dream(message: Message, state: FSMContext):
    """
    Получение сна из сообщения и запись в файл.\n
    Присутствует ограничение количества символов.
    """
    symbol_exceeding = len(message.text) - config.TO_BOT_MESSAGE_SYMBOL_LIMIT
    if symbol_exceeding > 0:
        symbol_limit_warning = (
            'Как тут много всего🤯🤯🤯\nЯ могу запомнить сон, в котором максимум '
            f'{config.TO_BOT_MESSAGE_SYMBOL_LIMIT} символов🥺\n'
            f'Сократи, пожалуйста, свой сон на {symbol_exceeding} символов🙏'
        )
        await safe_send_message(
            config.ARINA_ID,
            symbol_limit_warning,
            request_message_id=message.message_id,
        )
        return
    await write_content(
        message, config.DREAMS_FILEPATH, keyboards.Arina_keyboard,
    )
    await state.clear()


@config.dispatcher.message(DeleteLoveMessages.indexes)
async def delete_love_messages(message: Message, state: FSMContext):
    """
    Удаление любовных сообщений из файла по указанным индексам.
    """
    await delete_content(
        message, state, config.LOVE_MESSAGES_FILEPATH, keyboards.my_keyboard,
    )


@config.dispatcher.message(DeleteDreams.indexes)
async def delete_dreams(message: Message, state: FSMContext):
    """
    Удаление снов из файла по указанным индексам.
    """
    await delete_content(
        message, state, config.DREAMS_FILEPATH, keyboards.Arina_keyboard,
    )


@config.dispatcher.message(SendNoteForArina.note)
async def write_note_for_Arina(message: Message, state: FSMContext):
    """Отправка кастомного уведомления из сообщения Арине."""
    await safe_send_message(config.ARINA_ID, message.text)
    await message.answer('✅', reply_markup=keyboards.my_keyboard)
    await state.clear()


@config.dispatcher.message(
    F.text == keyboards.GET_CUTENESS, F.chat.id == config.ARINA_ID,
)
async def send_cuteness_immediately(message: Message):
    """Ответ на нажатие Ариной кнопки 'Получить милоту райт нау!!'"""
    await send_love_message(request_message_id=message.message_id)


@config.dispatcher.message(
    F.text == keyboards.WRITE_DREAM, F.chat.id == config.ARINA_ID,
)
async def start_dream_writing(message: Message, state: FSMContext):
    """Ответ на нажатие Ариной кнопки 'Записать сон📝'."""
    await safe_send_message(
        config.ARINA_ID,
        'Напишите, каким сладеньким сном Вы хотите поделиться😋',
        keyboards.cancel,
        request_message_id=message.message_id,
    )
    await state.set_state(WriteDream.dream)


@config.dispatcher.message(F.text == keyboards.SHOW_MESSAGES)
async def show_all_love_messages(message: Message):
    """
    Ответ на нажатие кнопки 'Посмотреть сообщения'.\n
    Мне – все любовные сообщения из файла, Арине – предупреждение.
    """
    if message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Вы делаете что-то незаконное🤔',
            request_message_id=message.message_id,
        )
        return
    await show_content(
        message, get_content_from_file(config.LOVE_MESSAGES_FILEPATH),
    )


@config.dispatcher.message(F.text == keyboards.SHOW_DREAMS)
async def show_all_dreams(message: Message):
    """Ответ на нажатие кнопки 'Посмотреть все сны📝'."""
    await show_content(message, get_content_from_file(config.DREAMS_FILEPATH))


@config.dispatcher.message(F.text == keyboards.DELETE_MESSAGES)
async def start_love_messages_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов, Арине – предупреждение.
    """
    if message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Вы делаете что-то очень незаконное🤔🤔🤔',
            request_message_id=message.message_id,
        )
        return
    await show_content(
        message, get_content_from_file(config.LOVE_MESSAGES_FILEPATH),
    )
    await message.answer(
        (
            'Введите диапазоны сообщений через запятую\n'
            'Пример: 1, 17-19, 23-24'
        ),
        reply_markup=keyboards.cancel,
    )
    await state.set_state(DeleteLoveMessages.indexes)


@config.dispatcher.message(
    F.text == keyboards.DELETE_DREAMES, F.chat.id == config.ARINA_ID,
)
async def start_dreams_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие Ариной кнопки 'Удалить нехорошие сны🗑️'.\n
    Появляется возможность ввода индексов.
    """
    await show_content(
        message, get_content_from_file(config.DREAMS_FILEPATH),
    )
    await safe_send_message(
        config.ARINA_ID,
        (
            'Фто тут нувно удалить? Мне нувны номера\n'
            'Например: 1, 17-19, 23-24 кнопочка "Отправить"⏎'
        ),
        keyboards.cancel,
    )
    await state.set_state(DeleteDreams.indexes)


@config.dispatcher.message(
    F.text == keyboards.WRITE_AS_BOT, F.chat.id == config.MY_ID,
)
async def start_writing_as_bot(message: Message, state: FSMContext):
    """Ответ на нажатие мною кнопки 'Написать от лица бота'."""
    await message.answer('Можно вещать', reply_markup=keyboards.cancel)
    await state.set_state(SendNoteForArina.note)


@config.dispatcher.message()
async def handle_message(message: Message):
    """Обработка прочих сообщений.\n
    Моё сообщение сохраняется в файл как любовное.
    Сообщение Арины пересылается мне.
    """
    if message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Сообщение отправлено☺️',
            request_message_id=message.message_id,
        )
        return
    await write_content(message, config.LOVE_MESSAGES_FILEPATH)


async def main():
    await asyncio.gather(
        wish_good_morning(),
        config.dispatcher.start_polling(config.bot),
        safe_send_message(config.MY_ID, 'Бот запущен'),
    )


if __name__ == '__main__':
    asyncio.run(main())
