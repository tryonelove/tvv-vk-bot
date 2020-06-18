import modules
import logging
from objects import glob
import commands
from modules import levels, utils
from helpers import commandsList


class Invoker:
    def __init__(self, event):
        self.event = event.obj
        self.cmd = None

    def _is_command(self):
        return self.event.text.startswith("!")

    def _get_command(self):
        self.cmd = commandsList.commands_list.get(self._key, commands.staticCommands.StaticCommand)
        logging.debug(self.cmd)

    def _set_key_value(self):
        message = self.event.text.split()
        self._key = message[0][1:].lower()
        self._value = " ".join(message[1:])

    def _send_message(self, message_object):
        params = {"peer_id": self.event.peer_id}
        params["message"] = message_object.message or None
        params["attachment"] = message_object.attachment or None
        glob.vk.messages.send(**params)

    def _invoke_command(self):
        if self.cmd is None:
            return
        logging.info("Sending a message.")

        # Check if it's a custom command or built-in one
        if issubclass(self.cmd, commands.staticCommands.StaticCommand):
            logging.info("Static command.")
            command_object = self.cmd(self._key)
        elif issubclass(self.cmd, (commands.levelCommands.GetLevel, commands.levelCommands.GetLeaderboard)):
            logging.info("Level command.")
            command_object = self.cmd(self.event.from_id, self.event.peer_id)
        elif issubclass(self.cmd, commands.commandManager.CommandManager):
            logging.info("Commands managing.")
            if not utils.is_donator(self.event.from_id) or not utils.is_admin(self.event.from_id):
                return
            command_object = self.cmd(self.event)
        elif issubclass(self.cmd, (commands.donatorCommands.DonatorManager, commands.adminCommands.AdminManager)):
            logging.info("Admin managing.")
            if not utils.is_creator(self.event.from_id):
                return
            command_object = self.cmd(self._value)
        else:
            logging.info("Other command.")
            command_object = self.cmd(self._value)
        executed = command_object.execute()
        if executed:
            self._send_message(executed)

    def _invoke_level(self):
        logging.info("Changing user level.")
        levelSystem = levels.LevelSystem(self.event.from_id, self.event.peer_id)
        levelSystem.level_check(self.event.text)

    def invoke(self):
        self._invoke_level()
        if self._is_command():
            self._set_key_value()
            logging.info("Command has been set: {}".format(self._key))
            self._get_command()
            logging.info("Got a command: {}".format(self.cmd))
            logging.info(self.event)
            self._invoke_command()

