from aiogram.types import KeyboardButton as Button, ReplyKeyboardMarkup

# В VS Code ширина пробела и знаков препинания = ширине строчной буквы;
# в Telegram – половине ширины строчной буквы,
# а ширина прописной буквы = 1,5 * ширина строчной.
# Исходя из этого вторую строку в надписи следует выравнивать по правому краю
# и добавлять/убирать пробелы в соответствии с вышеизложенными особенностями.
GET_CUTENESS = (
    'Получить милоту\n'
    '       райт нау!!'
)
WRITE_DREAM = 'Записать сон📝'
SHOW_MESSAGES = 'Посмотреть сообщения'
SHOW_DREAMS = 'Посмотреть все сны😴'
DELETE_MESSAGES = 'Удалить сообщения'
DELETE_DREAMES = (
    'Удалить нехорошие\n'
    '            сны🗑️'
)
WRITE_AS_BOT = (
    'Написать от лица\n'
    '            бота'
)
CANCEL = 'Отмена❌'

Arina_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [Button(text=GET_CUTENESS), Button(text=SHOW_DREAMS)],
        [Button(text=WRITE_DREAM), Button(text=DELETE_DREAMES)],
    ],
    resize_keyboard=True,
)

my_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [Button(text=SHOW_MESSAGES), Button(text=SHOW_DREAMS)],
        [Button(text=DELETE_MESSAGES), Button(text=WRITE_AS_BOT)],
    ],
    resize_keyboard=True,
)

cancel = ReplyKeyboardMarkup(
    keyboard=[[Button(text=CANCEL)]], resize_keyboard=True,
)
