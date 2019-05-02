import json
import requests
from constants import exceptions
from objects import glob
import re

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

def uploadPicture(upload, url, decode_content = False):
    session = requests.Session()
    image = session.get(url, stream=True).raw
    image.decode_content = decode_content
    photo = upload.photo_messages(photos=image)[0]
    return "photo{}_{}".format(photo['owner_id'], photo['id'])

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

def addcom(text = None, attachment = None):
    """
    Функция добавления текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    key = key.lower()
    if not(key):
        raise exceptions.ArgumentError
    cmd = {"message": value, "attachment": attachment}
    glob.commands[key] = cmd
    commands_update()
    return "Команда {} была успешно добавлена!".format(key)

def delcom(key):
    """
    Функция добавления текстовой команды
    :param key: название команды
    """
    if key not in glob.commands:
        raise exceptions.CustomException("Нет такой команды")
    del glob.commands[key.lower()]
    commands_update()
    return "Команда {} была успешно удалена!".format(key)

def editcom(text):
    """
    Функция редактирования текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    if not(key and value):
        raise exceptions.ArgumentError
    cmd = {"message": value, "attachment": None}
    glob.commands[key.lower()] = cmd
    commands_update()
    return "Команда {} была успешно изменена!".format(key)

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
    addcom(text = text, attachment = uploadPicture(upload, image_url))
    message = 'Пикча {} была успешно добавлена!'.format(text.split()[0])
    return message
    
def osuset(from_id, user_id, text):
    text = text.split(" ")
    if text[1] not in ('bancho', 'gatari'): 
        raise exceptions.ArgumentError('Доступные сервера: bancho, gatari')
    args = " ".join(text[2:])
    glob.users[str(from_id)]['server'] = text[1]
    glob.users[str(from_id)]['osu_username'] = args
    users_update()
    return 'Аккаунт '+args+' был успешно привязан к вашему айди'
    

def checkArgs(text):
    return text if text!="" else None

def getServerUsername(text, from_id):
    text = checkArgs(text)
    if text is None:
        text = "1"
    if text.isdigit():
        text = " " + text
    r = re.search(r'(bancho|gatari)?(.*?)(\s\d+)?$', text)
    if r:
        server = r.group(1)
        username = r.group(2)
        limit = r.group(3)
        if server is None:
            server = glob.users[str(from_id)].get('server', "bancho")
        if username == "":
            username = glob.users[str(from_id)].get('osu_username')
        if limit is not None:
            limit = int(limit)
        else:
            limit = 1
        return { "server" : server.strip(), "username" : username.strip(), "limit" : limit}

def getUserFromDB(from_id):
    server = glob.users[str(from_id)].get('server')
    username = glob.users[str(from_id)].get('osu_username')
    return { "server" : server, "username" : username }

    

    