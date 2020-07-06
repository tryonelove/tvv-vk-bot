import logging
import commands
from objects import glob
from helpers import commandsList, levels
from helpers.utils import Utils
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
        params = {"peer_id": message_object.peer_id or self.event.peer_id}
        params["message"] = message_object.message or None
        params["attachment"] = message_object.attachment or None
        if params["message"] is None and params["attachment"] is None:
            return
        glob.vk.messages.send(**params)

    def _invoke_command(self):
        if self.cmd is None or Utils.has_role(self.event.from_id, Roles.RESTRICTED):
            return
        if issubclass(self.cmd, commands.staticCommands.StaticCommand):
            logging.debug("Static command.")
            command_object = self.cmd(key=self._key)

        elif issubclass(self.cmd, (commands.interfaces.ILevelCommand)):
            logging.debug("Level command.")
            command_object = self.cmd(
                user_id=self.event.from_id, chat_id=self.event.peer_id)

        elif issubclass(self.cmd, commands.interfaces.ICommandManager):
            logging.debug("Commands managing.")
            if not Utils.has_role(self.event.from_id, Roles.DONATOR | Roles.ADMIN):
                return
            command_object = self.cmd(
                message=self.event.text, attachments=self.event.attachments, author_id=self.event.from_id)

        elif issubclass(self.cmd, (commands.interfaces.IDonatorManager, commands.interfaces.IAdminCommand)):
            logging.debug("Admin managing.")
            if not Utils.is_creator(self.event.from_id):
                return
            command_object = self.cmd(self._value)

        elif issubclass(self.cmd, commands.interfaces.IOsuCommand):
            logging.debug("osu! command")
            # Need to get server and username from db
            params = Utils.get_osu_params(self._value, self.event.from_id)
            command_object = self.cmd(**params)
        else:
            logging.debug("Other command.")
            command_object = self.cmd(self._value)
        executed = command_object.execute()
        if executed:
            self._send_message(executed)        

    def _invoke_level(self):
        logging.debug("Changing user level.")
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
