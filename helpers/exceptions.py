class BotException(Exception):
    """
    Base exception class
    """

    def __init__(self, message=None):
        self.message = f"Ошибка: {message}"
        super().__init__(self.message)

class OverwritingExistingCommand(BotException):
    def __init__(self, message="Нельзя перезаписывать чужие команды"):
        super().__init__(message)


class UserNotFoundError(BotException):
    """
    The following user doesn't exist.
    """

    def __init__(self, message="Пользователь не найден."):
        super().__init__(message)


class ScoreNotFoundError(BotException):
    """
    Couldn't find score on the map.
    """

    def __init__(self, message="Скор на карте не найден."):
        super().__init__(message)


class AccesDeniesError(BotException):
    """
    Access denied due to unmatching permissions.
    """

    def __init__(self, message="Нет доступа, ваша роль ниже необходимой."):
        super().__init__(message)


class ApiRequestError(BotException):
    """
    API request error.
    """

    def __init__(self, message="Ошибка при запросе к API."):
        super().__init__(message)


class CityNotFoundError(Exception):
    """
    City not found (weather command)
    """

    def __init__(self, message="Город не найден."):
        super().__init__(message)


exceptions = (UserNotFoundError, AccesDeniesError,
              ApiRequestError, CityNotFoundError, 
              ScoreNotFoundError, OverwritingExistingCommand)
