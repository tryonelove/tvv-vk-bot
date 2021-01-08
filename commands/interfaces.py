from abc import ABC, abstractmethod
import requests
from objects import message


class ICommand(ABC):
    """
    Base command interface
    """
    KEYS: list = None

    def __init__(self, *args, **kwargs):
        self.KEYS = []
        self.Message = message.MessageObject

    @abstractmethod
    def execute(self):
        pass


class IAdminCommand(ICommand):
    """
    Interface for admin-managing commands 
    """

    def __init__(self, user_id, **kwargs):
        super().__init__()
        self._user_id = user_id


class IOsuCommand(ICommand):
    """
    Interface for all osu! commands
    """

    def __init__(self):
        super().__init__()


class ILevelCommand(ICommand):
    """
    Interface for level commands
    """

    def __init__(self, **kwargs):
        super().__init__()
        self._user_id = kwargs.get("user_id")
        self._chat_id = kwargs.get("chat_id")

    def _is_chat_admin(self):
        pass


class ICommandManager(ICommand):
    """
    Interface for user-created commands
    """

    def __init__(self, **kwargs):
        super().__init__()
        self._message = kwargs.get("message")
        self._attachments = kwargs.get("attachments")
        self._author_id = kwargs.get("author_id")
        self._key = kwargs.get("key")
        self._value = kwargs.get("value")

    def _set_values(self):
        """
        Set command key, value, attachment 
        """
        pass


class IDonatorManager(ICommand):
    """
    Interface to manage donators
    """

    def __init__(self, args, **kwargs):
        super().__init__()
        try:
            self._args = args.split()
            self._user_id = int(self._args[0]) if self._args else None
        except:
            self._user_id = args
