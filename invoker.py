import modules
import logging
from objects import glob
from commands import commands_list


class Invoker:
    def __init__(self, event):
        self.event = event.obj
        self.cmd = None
        if self.is_command():
            self.set_key_value()
            logging.info("Command has been set: {}".format(self._key))
            self.get_command()
            logging.info("Got a command: {}".format(self.cmd))

    def is_command(self):
        return self.event.text.startswith("!")

    def get_command(self):
        self.cmd = commands_list.get(self._key, modules.staticCommand.StaticCommand)
        logging.debug(self.cmd)

    def set_key_value(self):
        message = self.event.text.split()
        self._key = message[0][1:].lower()
        self._value = " ".join(message[1:])

    def send_message(self, message_object):
        params = {"peer_id":self.event.peer_id}
        params["message"] = message_object.message or None
        params["attachment"] = message_object.attachment or None
        glob.vk.messages.send(**params)

    def invoke(self):
        if self.cmd is None:
            return
        logging.info("Sending a message")

        # Check if it's a custom command or built-in one
        if isinstance(self.cmd, modules.staticCommand.StaticCommand):
            command_object = self.cmd(self._key)
        else:
            command_object = self.cmd(self._value)
        executed = command_object.execute()
        if executed:
            self.send_message(executed)
