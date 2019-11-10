import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import json
import time
import sqlite3
import threading
import invoker

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
            format='%(levelname)s: %(message)s', level=logging.INFO)
        self.vk_session = vk_api.VkApi(token=api_token, api_version='5.89')
        self.longpoll = VkBotLongPollFix(self.vk_session, group_id)
        self.vk = self.vk_session.get_api()
        self.upload = VkUpload(self.vk)
        
    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                event_thread = threading.Thread(target=invoker.Invoker(self.vk, event).invoke)
                event_thread.start()
                event_thread.join()