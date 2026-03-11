import asyncio
from datetime import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot import config, keyboards, love_messages
from love_bot.fsms import DeleteMessages
from love_bot.utils import get_indexes, safe_send_message


async def wish_good_morning():
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(config.TZ)
        delta = now.replace(**config.SENDING_TIME) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        await love_messages.send_love_message()
        await asyncio.sleep(1)


@config.dispatcher.message(Command("start"))
async def start(message: Message):
    """
    Ответ на команду /start.\n
    Неизвестным пользователям отправляется соответствующее сообщение.
    """
    if message.chat.id == config.ARINA_ID:
        first_message = (
            'Приветище! Каждое утро я буду присылать тебе что-нибудь милое😊. '
            'Если хочешь этого прямо сейчас, жми на кнопочку. Я глупенький, '
            'поэтому не смогу понимать твои сообщения и буду пересылать их '
            'моему создателю. Там, конечно, тоже не гений сидит, '
            'но у него больше шансов разобраться✨'
        )
        await message.answer(
            first_message, reply_markup=keyboards.get_cuteness,
        )
    elif message.chat.id == config.MY_ID:
        await message.answer('🖐️', reply_markup=keyboards.show_messages)
    else:
        await message.answer(config.FOR_UNKNOWN_USERS)


@config.dispatcher.message(F.text == keyboards.GET_CUTENESS_TEXT)
async def send_cuteness_immediately(message: Message):
    """Ответ на нажатие Ариной кнопки 'Получить милоту райт нау!!'"""
    if message.chat.id == config.ARINA_ID:
        await love_messages.send_love_message()


@config.dispatcher.message(F.text == keyboards.SHOW_MESSAGES_TEXT)
async def show_all_love_messages(message: Message):
    """
    Ответ на нажатие кнопки 'Посмотреть сообщения'.\n
    Мне – все сообщения из файла, Арине – предупреждение.
    """
    if message.chat.id == config.MY_ID:
        messages = await love_messages.get_messages_from_file()
        if messages:
            await love_messages.show_messages(
                messages, keyboards.delete_messages,
            )
    elif message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID, 'Вы делаете что-то незаконное🤔',
        )


@config.dispatcher.message(F.text == keyboards.DELETE_MESSAGES_TEXT)
async def start_love_messages_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов либо отмены удаления нажатием кнопки,
    Арине – предупреждение.
    """
    if message.chat.id == config.MY_ID:
        await state.clear()
        await message.answer(
            (
                'Введите диапазоны сообщений через запятую\n'
                'Пример: 1, 17-19, 23-24'
            ),
            reply_markup=keyboards.cancel,
        )
        await state.set_state(DeleteMessages.indexes)
    elif message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID, 'Вы делаете что-то очень незаконное🤔🤔🤔',
        )


@config.dispatcher.message(DeleteMessages.indexes)
async def delete_love_messages(message: Message, state: FSMContext):
    """
    Удаление сообщений из файла по указанным индексам или отмена удаления.
    """
    if message.text == keyboards.CANCEL_TEXT:
        await state.clear()
        await message.answer(
            'Удаление отменено', reply_markup=keyboards.show_messages,
        )
    else:
        try:
            indexes_for_deleting = get_indexes(message.text)
        except ValueError:
            await message.answer('Проверьте правильность ввода')
        else:
            messages_from_file = await love_messages.get_messages_from_file()
            if messages_from_file:
                undeleted_messages = []
                deleted_messages = []
                for index, message_from_file in enumerate(messages_from_file):
                    (
                        deleted_messages.append(message_from_file)
                        if index in indexes_for_deleting
                        else undeleted_messages.append(message_from_file)
                    )
                with open(config.FILEPATH, 'w', encoding='utf-8') as file:
                    file.writelines(undeleted_messages)
                await message.answer('Удалены следующие сообщения:')
                await love_messages.show_messages(
                    deleted_messages, keyboards.show_messages,
                )
            await state.clear()


@config.dispatcher.message()
async def receive_message(message: Message):
    """Обработка прочих сообщений.\n
    Моё сообщение сохраняется в файл как любовное.
    Сообщение Арины пересылается мне.
    """
    if message.chat.id == config.MY_ID:
        try:
            with open(config.FILEPATH, 'a', encoding='utf-8') as file:
                file.write(f'{message.text}\n')
        except FileNotFoundError:
            await message.answer(
                'Файл с сообщениями не найден',
                reply_markup=keyboards.show_messages,
            )
        else:
            await message.answer(
                'Сохранено', reply_markup=keyboards.show_messages,
            )
    elif message.chat.id == config.ARINA_ID:
        await config.bot.forward_message(
            chat_id=config.MY_ID,
            from_chat_id=config.ARINA_ID,
            message_id=message.message_id,
        )
        await message.answer('Сообщение отправлено☺️')


async def main():
    await asyncio.gather(
        wish_good_morning(), config.dispatcher.start_polling(config.bot),
    )


if __name__ == '__main__':
    asyncio.run(main())
