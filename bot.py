import vk_api
from vk_api.bot_longpoll import VkBotEventType
from longpoll import VkBotLongPollFix
import logging
from objects import glob
import threading
import invoker
import config
import sqlite3

class Bot:
    def __init__(self, api_token, group_id):
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.DEBUG)
        self.vk_session = vk_api.VkApi(token=api_token, api_version='5.89')
        self.longpoll = VkBotLongPollFix(self.vk_session, group_id)
        glob.vk = self.vk_session.get_api()
        glob.upload = vk_api.VkUpload(glob.vk)
        glob.db = sqlite3.connect("database.db")
        glob.c = glob.db.cursor()

    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                invoker.Invoker(event).invoke()


if __name__ == "__main__":
    bot = Bot(config.API_KEY_TEST, config.GROUP_ID_TEST)
    # bot = Bot(config.API_KEY, config.GROUP_ID)

    bot.start()
