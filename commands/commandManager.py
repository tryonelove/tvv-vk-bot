from commands.interfaces import ICommandManager
from objects import glob
from helpers.utils import Utils
import logging
from helpers import exceptions 

class CommandManager(ICommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def _photo_handler(self):
        largest_url = Utils.find_largest_attachment(
                    self._attachments[0]["photo"]["sizes"])
        logging.info("Uploading picture: "+largest_url)
        self._attachments = Utils.upload_picture(largest_url)

    def _video_handler(self):
        self._attachments = f"video{self._attachments[0]['video']['owner_id']}_{self._attachments[0]['video']['id']}"


    def _set_values(self):
        """
        Split message into key: value format
        """
        message = self._message.split()
        self._key = message[1]
        if len(message) > 1:
            self._value = " ".join(message[2:])
        if self._attachments:
            if self._attachments[0]["type"] not in ["photo", "video"]:
                self._attachments = None
                return
            if self._attachments[0]["type"] == "video":
                self._video_handler()
            elif self._attachments[0]["type"] == "photo":
                self._photo_handler()
        else:
            self._attachments = None


class AddCommand(CommandManager):
    """
    Create command

    :param message: message containing key and value message for command
    :param attachments: command attachments
    :param author_id: user_id the message has been sent from 
    """

    def __init__(self, message, attachments, author_id):
        super().__init__(message=message, attachments=attachments, author_id=author_id)

    def execute(self):
        self._set_values()
        author_id = glob.c.execute("SELECT author FROM commands WHERE key = ?", (self._key,)).fetchone()
        if author_id is not None:
            if author_id[0] != self._author_id:
                raise exceptions.OverwritingExistingCommand
        q = "INSERT OR REPLACE INTO commands VALUES (?, ?, ?, ?)"
        glob.c.execute(q, (self._key, self._value,
                           self._attachments, self._author_id))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно добавлена!")


class DeleteCommand(CommandManager):
    """
    Delete command by key

    :param message: message containing key for removing command
    """
    def __init__(self, message, **kwargs):
        super().__init__(message=message)

    def execute(self):
        self._set_values()
        q = "DELETE FROM commands WHERE key = ?"
        glob.c.execute(q, (self._key,))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно удалена!")
