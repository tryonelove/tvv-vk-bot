import json
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import requests
import logging


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', filename='log.log' ,level=logging.DEBUG)
    try:
        vk_session = vk_api.VkApi(token='d10f958717ec12d4b668fe4506f50db8bd6e053535ca377ee89d157bf02b8841d47dd736644087be2922e', api_version='5.89')
        print("Logged in")
    except vk_api.AuthError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, '178909901')
    upload = VkUpload(vk_session)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    if event.obj.text:
                        logging.info(event.obj.text)
                except requests.exceptions.Timeout:
                        pass
                except Exception as e:
                        logging.error(str(e))


if __name__ == "__main__":
    main()