import modules
import logging
from objects import glob
from commands import commands_list


class Invoker:
    def __init__(self, event):
        self.event = event.obj
        self.cmd = None
        if self.is_command():
            logging.info("It's a command")
            self.set_key_value()
            logging.info("Command has been set: {}".format(self._key))
            self.get_command()
            logging.info("Got a command: {}".format(self.cmd))

    def is_command(self):
        if self.event.text.startswith("!"):
            return True
        return False

    def get_command(self):
        self.cmd = commands_list.get(self._key)

    def set_key_value(self):
        message = self.event.text.split()
        self._key = message[0][1:].lower()
        self._value = " ".join(message[1:])

    def send_message(self, **kwargs):
        glob.vk.messages.send(peer_id=self.event.peer_id, **kwargs)

    def invoke(self):
        if self.cmd is None:
            return
        logging.info("Sending a message")
        executed = self.cmd(*self._value.split()).execute()
        logging.info(executed)
        self.send_message(**executed)
