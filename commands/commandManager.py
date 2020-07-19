from commands.interfaces import ICommandManager
from objects import glob
from helpers.utils import Utils
import logging


class CommandManager(ICommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def _set_values(self):
        """
        Split message into {key: value} format
        """
        message = self._message.split()
        self._key = message[1]
        if len(message) > 1:
            self._value = " ".join(message[2:])
        if self._attachments:
            if self._attachments[0]["type"] != "photo":
                self._attachments = None
                return
            largest_url = Utils.find_largest_attachment(
                self._attachments[0]["photo"]["sizes"])
            logging.info("Uploading picture: "+largest_url)
            self._attachments = Utils.upload_picture(largest_url)


class AddCommand(CommandManager):
    """
    Create command
    """

    def __init__(self, message, attachments, author_id):
        super().__init__(message=message, attachments=attachments, author_id=author_id)

    def execute(self):
        self._set_values()
        q = "INSERT OR REPLACE INTO commands VALUES (?, ?, ?, ?)"
        glob.c.execute(q, (self._key, self._value,
                           self._attachments, self._author_id))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно добавлена!")


class DeleteCommand(CommandManager):
    """
    Delete command by key
    """

    def __init__(self, message, **kwargs):
        super().__init__(message=message)

    def execute(self):
        self._set_values()
        q = "DELETE FROM commands WHERE key = ?"
        glob.c.execute(q, (self._key,))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно удалена!")
