import logging
import commands
from objects import glob 
from helpers import commandsList, utils, levels
from constants.roles import Roles


class Invoker:
    def __init__(self, event):
        self.event = event.obj
        self.cmd = None

    def _is_command(self):
        return self.event.text.startswith("!")

    def _get_command(self):
        self.cmd = commandsList.commands_list.get(
            self._key, commands.staticCommands.StaticCommand)
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
        if issubclass(self.cmd, commands.staticCommands.StaticCommand):
            logging.info("Static command.")
            command_object = self.cmd(self._key)
        elif issubclass(self.cmd, (commands.levelCommands.GetLevel, commands.levelCommands.GetLeaderboard)):
            logging.info("Level command.")
            command_object = self.cmd(self.event.from_id, self.event.peer_id)
        elif issubclass(self.cmd, commands.commandManager.CommandManager):
            logging.info("Commands managing.")
            if not utils.has_role(self.event.from_id, Roles.DONATOR | Roles.ADMIN):
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
        levelSystem = levels.LevelSystem(
            self.event.from_id, self.event.peer_id)
        levelSystem.level_check(self.event.text)

    def invoke(self):
        self._invoke_level()
        if self._is_command():
            self._set_key_value()
            logging.info(f"Command: {self._key}")
            self._get_command()
            self._invoke_command()