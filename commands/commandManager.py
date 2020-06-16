from commands.command import Command
from objects import glob
from modules import utils
import logging

class CommandManager(Command):
    def __init__(self, event):
        super().__init__()
        self._event = event
        self._key = None
        self._value = None
        self._attachments = None
        self._set_values()

    def _set_values(self):
        """
        Set command key, value, attachment 
        """
        message = self._event.text.split()
        self._key = message[1]
        if len(message)>1:
            self._value = " ".join(message[2:])
        if self._event.attachments:
            if self._event.attachments[0]["type"] == "photo":
                largest_url = utils.find_largest_attachment(self._event.attachments[0]["photo"]["sizes"])
                logging.info("Uploading picture: "+largest_url)
                self._attachments = utils.upload_picture(largest_url)


class AddCommand(CommandManager):
    def __init__(self, event):
        super().__init__(event)
        self._author_id = self._event.from_id

    def execute(self):
        q = "INSERT OR REPLACE INTO commands VALUES (?, ?, ?, ?)"
        glob.c.execute(q, (self._key, self._value, self._attachments, self._author_id))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно добавлена!")


class DeleteCommand(CommandManager):
    def __init__(self, event):
        super().__init__(event)
        self._author_id = self._event.from_id

    def execute(self):
        q = "DELETE FROM commands WHERE key = ?"
        glob.c.execute(q, (self._key,))
        glob.db.commit()
        return self.Message(f"Команда {self._key} была успешно удалена!")
