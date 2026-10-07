class EmptyFileError(ValueError):
    """Исключение при отсутствии содержимого файла."""


class EmptyRequestError(ValueError):
    """Исключение при отсутствии содержимого для записи в файл."""


class NoContentForDeletingError(ValueError):
    """
    Исключение при попытке удалить контент по индексам,
    выходящим за фактический диапазон.
    """


class TooLongContentMessageError(ValueError):
    """
    Исключение при получении сообщения для записи контента,
    длина которого превышает установленную в настройках бота.
    """
    def __init__(self, *args: object, symbol_limit_exceeding: int) -> None:
        """
        Принимает в качестве обязательного именнованного аргумента
        разницу между фактической длиной и предельной
        и указывает это число в сообщении об ошибке.
        """
        self.symbol_limit_exceeding = symbol_limit_exceeding
        super().__init__(*args)

    def __str__(self) -> str:
        details = (
            f'Лимит превышен на {self.symbol_limit_exceeding} символов'
        )
        return f'{super().__str__()}. {details}' if self.args else details
