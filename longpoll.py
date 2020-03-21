import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


class VkBotLongPollFix(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                logging.error(e)
