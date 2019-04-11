import json
import requests
from constants import exceptions
import logging
from objects import glob

def config_update():
    """
    Функция перезаписи users.json
    """
    with open('config.json', 'w') as f:
        json.dump(glob.config, f, indent=4)

def commands_update():
    """
    Функция перезаписи commands.json
    """
    with open('commands.json', 'w', encoding='UTF-8') as f:
        json.dump(glob.commands, f, indent=4, ensure_ascii=False)

def users_update():
    """
    Функция перезаписи users.json
    """
    with open('users.json', 'w') as f:
        json.dump(glob.users, f, indent=4)

def upload_pic(upload, url):
    session = requests.Session()
    image = session.get(url, stream=True)
    photo = upload.photo_messages(photos=image.raw)[0]
    return f"photo{photo['owner_id']}_{photo['id']}"

def findLargestPic(data):
    """
    Функция поиска самой большой картинки в сообщении
    :param event: VK API event
    """
    largest = 0
    for x in data:
        larger = x["width"]*x["height"]
        if larger>largest:
            largest = larger
            largest_pic = x["url"]
    return largest_pic

def messageToCommand(message):
    message = message.split(" ")
    key = message[0]
    value = " ".join(message[1:])
    return key, value

def addcom(text):
    """
    Функция добавления текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    if not(key and value):
        raise exceptions.ArgumentError
    glob.commands[key.lower()] = value
    commands_update()
    return f"Команда {key} была успешно добавлена!"

def delcom(key):
    """
    Функция добавления текстовой команды
    :param key: название команды
    """
    if key not in glob.commands:
        raise exceptions.CustomException("Нет такой команды")
    del glob.commands[key.lower()]
    commands_update()
    return f"Команда {key} была успешно удалена!"

def editcom(text):
    """
    Функция редактирования текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    if not(key and value):
        raise exceptions.ArgumentError
    glob.commands[key.lower()] = value
    commands_update()
    return f"Команда {key} была успешно изменена!"

def addpic(upload, text, attachments):
    """
    Функция добавления пикчи
    :param upload: VK API класс VkUpload
    :param key: название команды
    :param value: значение
    """
    if not (len(attachments)>=1 and attachments[0]["type"]=="photo"):
        raise exceptions.CustomException("Должна быть прикреплена хотя бы одна пикча.")
    image_url = findLargestPic(attachments[0]['photo']["sizes"])
    addcom(text+" "+ upload_pic(upload, image_url))
    message = 'Пикча '+text.split()[0]+' была успешно добавлена!'
    return message
    
def osuset(from_id, user_id, text):
    text = text.split(" ")

    if text[1] in ('bancho', 'gatari'): 
        args = " ".join(text[2:])
        glob.users[str(from_id)]['server'] = text[1]
        glob.users[str(from_id)]['osu_username'] = args
        users_update()
        return 'Аккаунт '+args+' был успешно привязан к вашему айди'
    return 'Доступные сервера: bancho, gatari'


def user_in_db(content = None, user_id = None):
    if content is None:
        server = glob.users[str(user_id)].get('server', None)
        username = glob.users[str(user_id)].get('osu_username', None)
    else:
        content = content.split()
        if content[0] not in ("bancho", "gatari"):
            username = ' '.join(content)
            server = 'bancho'
        else:
            username = ' '.join(content[1:])
            server = content[0]
    return server, username

    