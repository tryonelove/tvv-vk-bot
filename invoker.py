import logging
import commands
from objects import glob, message
from helpers import commandsList, levels
from helpers.utils import Utils
from constants.roles import Roles
from config import CREATOR_ID
from constants.messageTypes import MessageTypes
import datetime
from threading import Lock

lock = Lock()

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
        params = {}
        if message_object.message_type == MessageTypes.PRIVATE:
            params["peer_id"] = self.event.from_id
        else:
            params["peer_id"] = self.event.peer_id
        params["message"] = message_object.message or None
        params["attachment"] = message_object.attachment or None
        logging.debug(params)
        if params["message"] is None and params["attachment"] is None:
            return
        glob.vk.messages.send(**params)

    def _get_command_object(self):
        command_object = None
        if issubclass(self.cmd, commands.staticCommands.StaticCommand):
            logging.debug("Static command.")
            command_object = self.cmd(key=self._key)

        elif issubclass(self.cmd, commands.interfaces.ILevelCommand):
            logging.debug("Level command.")
            command_object = self.cmd(
                user_id=self.event.from_id, chat_id=self.event.peer_id)

        elif issubclass(self.cmd, commands.interfaces.ICommandManager):
            logging.debug("Commands managing.")
            if not Utils.has_role(self.event.from_id, Roles.DONATOR | Roles.ADMIN):
                return
            command_object = self.cmd(
                message=self.event.text, attachments=self.event.attachments, author_id=self.event.from_id)

        elif issubclass(self.cmd, commands.interfaces.IAdminCommand):
            logging.debug("Admin managing.")
            if not Utils.is_creator(self.event.from_id):
                return
            user_id = Utils.find_user_id(self.event.text)
            command_object = self.cmd(user_id, self.event.from_id)

        elif issubclass(self.cmd, commands.interfaces.IDonatorManager):
            logging.debug("Donator managing.")
            if not Utils.is_creator(self.event.from_id):
                return
            command_object = self.cmd(self._value, self.event.from_id)

        elif issubclass(self.cmd, commands.interfaces.IOsuCommand):
            logging.debug("osu! command")
            # Need to get server and username from db
            # server, username, user_id dict
            params = Utils.get_osu_params(self._value, self.event.from_id)
            if self.event.fwd_messages:
                fwd_message = self.event.fwd_messages[-1]
                params["beatmap_id"] = Utils.find_beatmap_id(
                    fwd_message["text"])
            command_object = self.cmd(**params)

        else:
            logging.debug("Other command.")
            command_object = self.cmd(self._value, self.event.from_id)
        return command_object

    def _invoke_command(self):
        logging.info(f"Got a {self.cmd}, message: {self.event.text}")
        if self.cmd is None or Utils.has_role(self.event.from_id, Roles.RESTRICTED):
            return
        command_object = self._get_command_object()
        executed = command_object.execute() or None
        if executed:
            self._send_message(executed)

    def _invoke_level(self):
        levelSystem = levels.LevelSystem(
            self.event.from_id, self.event.peer_id)
        levelSystem.level_check(self.event.text)

    def _invoke_donator(self):
        if Utils.has_role(self.event.from_id, Roles.DONATOR):
            expires = Utils.get_donator_expire_date(self.event.from_id)
            if not expires:
                return
            now = datetime.datetime.now().timestamp()
            if now > expires[0]:
                cmd = commandsList.commands_list.get(
                    "rm_donator")(self.event.from_id)
                msg = cmd.execute()
                msg.message = f"Минус донатер у *id{self.event.from_id}"
                self._send_message(msg)

    def invoke(self):
        if self.event.from_id < 0:
            return
        try:
            lock.acquire(True)
            self._invoke_level()
            self._invoke_donator()
            lock.release()
            if self._is_command():
                self._set_key_value()
                logging.info(f"Command: {self._key}")
                self._get_command()
                self._invoke_command()
        except Exception as e:
            logging.error(self.event)
            logging.error(e.args)
