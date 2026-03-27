# Описание
Бот для отправки по расписанию ежедневных сообщений любимому человеку 
(и только ему) и получения от него снов, которые записываются и могут быть им 
удалены. Другие пользователи получают уведомление об эксклюзивности
использования бота. Присутствует функционал администрирования. Логирование в
сообщениях админу (DEBUG-ERROR) и в лог-файлы (ERROR-CRITICAL). Бот работает 
на серверах [Amvera](https://cloud.amvera.ru/).

# Установка
Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/FantalovSergey/love_morning-bot.git
```

```
cd love_morning-bot
```

Cоздайте и активируйте виртуальное окружение:

```
python3 -m venv venv
```

* Для Linux/macOS

    ```
    source venv/bin/activate
    ```

* Для Windows

    ```
    venv\Scripts\activate
    ```

Установите зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

# Стек
- Python 3.12.7
- aiogram 3.26.0
