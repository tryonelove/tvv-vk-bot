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
import threading

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
        glob.db = sqlite3.connect("users.db", check_same_thread = False)
        glob.c = glob.db.cursor()

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
                event_thread = threading.Thread(target=self.handleEvent, args=(event,))
                event_thread.start()
                event_thread.join()
                
    def handleEvent(self, event):
        handler = CommandsHandler(self.vk, self.upload, event)
        data = {
            "peer_id": event.obj.peer_id,
            "message": None,
            "attachment" : None
        }
        try:
            data = handler.processMessage()
        except exceptions.NoPrivilegesPermissions:
            data["message"] = "Ошибка: Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
        except exceptions.NoAdminPermissions:
            data["message"] = "Ошибка: Недостаточно прав, команда для админов"
        except exceptions.ScoreMessageNotFound:
            data["message"] = "Ошибка: Необходимо переслать сообщение со скором"
        except exceptions.ArgumentError:
            data["message"] = "Ошибка: Проверьте правильность аргументов"
        except exceptions.dbUserNotFound:
            data["message"] = "Ошибка: Не удалось найти аккаунт в базе, попробуйте указать сервер и ник.\n Например: !{} bancho cookiezi".format(handler.key)
        except exceptions.UserNotFound:
            data["message"] = "Ошибка: Нет данных, возможно, что пользователь в бане, либо нет скоров за последние 24 часа"
        except exceptions.CustomException as e:
            data["message"] = "Ошибка: {}".format(e.args[0])
        except Exception as e:
            data["peer_id"] = 236965366
            if data.get("message") is not None:
                data["message"] += "\nОшибка: {}".format(e.args)
            else:
                data["message"] = "\nОшибка: {}\nАвтор: *id{}\nСообщение: {}".format(e.args[0], event.obj.from_id, event.obj.text)
        if data is not None:
            try:
                self.sendMsg(**data)
            except Exception as e:
                logging.error(e)
                    
