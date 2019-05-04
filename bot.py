import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from modules.commands import CommandsHandler
import logging
from objects import glob
import json
from constants import exceptions
from time import sleep

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
        with open("commands.json", "r", encoding="utf-8") as f:
            glob.commands = json.load(f)
        with open("config.json", "r", encoding="utf-8") as f:
            glob.config = json.load(f)
        with open("users.json", "r", encoding="utf-8") as f:
            glob.users = json.load(f)

    def send_msg(self, peer_id, message=None, attachment=None):
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
                data = None
                try:
                    data = handler.process_message()
                except (exceptions.ArgumentError,
                        exceptions.CustomException,
                        exceptions.NoAdminPermissions,
                        exceptions.NoDonorPermissions,
                        exceptions.NoPrivilegesPermissions) as e:
                    data = {
                            "peer_id": event.obj.peer_id,
                            "message": "Ошибка: {}".format(e.args[0]), 
                            "attachment": None
                    }
                # except Exception as e:
                    # logging.error(e)
                if data is not None:
                    try:
                        self.send_msg(**data)
                    except Exception as e:
                        logging.error(e)
                    
