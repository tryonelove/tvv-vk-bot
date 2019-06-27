import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from modules.commands import CommandsHandler
import logging
from objects import glob
import json
from constants import exceptions
import time
import sqlite3


class VkBotLongPollFix(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                logging.error(e)


class Bot:
    def __init__(self, api_token, group_id):
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.DEBUG)
        self.vk_session = vk_api.VkApi(token=api_token, api_version='5.89')
        self.longpoll = VkBotLongPollFix(self.vk_session, group_id)
        self.vk = self.vk_session.get_api()
        self.upload = VkUpload(self.vk)
        self.set_globals()

    def set_globals(self):
        with open("commands.json", "r", encoding="utf-8") as f:
            glob.commands = json.load(f)
        with open("config.json", "r", encoding="utf-8") as f:
            glob.config = json.load(f)
        with open("users.json", "r", encoding="utf-8") as f:
            glob.users = json.load(f)
        

    def sendMsg(self, peer_id, message=None, attachment=None):
        """
        Отправка сообщения через метод messages.send
        :param send_id: vk id пользователя, который получит сообщение
        :param message: содержимое отправляемого сообщения
        :param attachment: содержимое отправляемого сообщения
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=message,
                              attachment=attachment)

    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                handler = CommandsHandler(self.vk, self.upload, event)
                data = {}
                try:
                    data = handler.processMessage()
                except (exceptions.ArgumentError,
                        exceptions.CustomException,
                        exceptions.NoAdminPermissions,
                        exceptions.NoDonorPermissions,
                        exceptions.NoPrivilegesPermissions,
                        exceptions.ApiError) as e:
                    data = {
                            "peer_id": event.obj.peer_id,
                            "message": "Ошибка: {}".format(e.args[0]), 
                            "attachment": None
                    }
                except Exception as e:
                    data["peer_id"] = 236965366
                    if data.get("message") is not None:
                        data["message"] += "\nОшибка: {}".format(e.args[0])
                    else:
                        data["message"] = "\nОшибка: {}".format(e.args[0])
                if data is not None:
                    try:
                        self.sendMsg(**data)
                    except Exception as e:
                        logging.error(e)
                    
