import json
import requests
from constants import exceptions
from objects import glob
import re
from helpers import checks

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

def updateUsers():
    """
    Функция перезаписи users.json
    """
    glob.db.commit()

def insertUser(cursor, user_id, name=None):
    cursor.execute("INSERT OR REPLACE INTO users(id, name) VALUES(?, ?)", (user_id, name))

def insertLevels(cursor, chat_id, user_id, experience=None, level=None):
    cursor.execute("INSERT OR REPLACE INTO konfa_{} VALUES(?, ?, ?)".format(chat_id), (user_id, experience, level))

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

def addcom(from_id, text = None, attachment = None):
    """
    Функция добавления текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    key = key.lower()
    if not key or (value == "" and not attachment):
        raise exceptions.ArgumentError("Проверьте правильность аргументов")
    if key in glob.commands and not checks.commandAdder(from_id, key):
        raise exceptions.NoPrivilegesPermissions("Изменять команды могут их создатели или админы")
    cmd = {"author": from_id, "message": value, "attachment": attachment}
    glob.commands[key] = cmd
    commands_update()
    return "Команда {} была успешно добавлена!".format(key)

def delcom(key):
    """
    Функция удаления команды
    :param key: название команды
    """
    if key not in glob.commands:
        raise exceptions.CustomException("Нет такой команды")
    del glob.commands[key.lower()]
    commands_update()
    return "Команда {} была успешно удалена!".format(key)

def editcom(from_id, text):
    """
    Функция редактирования текстовой команды
    :param key: название команды
    :param value: значение команды
    """
    key, value = messageToCommand(text)
    if not(key and value):
        raise exceptions.ArgumentError
    if not checks.commandAdder(from_id, key):
        raise exceptions.NoPrivilegesPermissions("Изменять команды могут их создатели или админы")
    cmd = {"author":from_id,"message": value, "attachment": None}
    glob.commands[key.lower()] = cmd
    commands_update()
    return "Команда {} была успешно изменена!".format(key)

def addpic(from_id, upload, text, attachments):
    """
    Функция добавления пикчи
    :param upload: VK API класс VkUpload
    :param key: название команды
    :param value: значение
    """
    image_url = findLargestPic(attachments[0]['photo']["sizes"])
    addcom(from_id=from_id, text = text, attachment = uploadPicture(upload, image_url))
    message = 'Пикча {} была успешно добавлена!'.format(text.split()[0])
    return message
    
def checkArgs(text):
    return text if text!="" else None

def getServerUsername(cursor, text, from_id):
    # spaghetti
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
            server = cursor.execute("SELECT server FROM users WHERE id=?", (from_id,)).fetchone()
        if username == "":
            username = cursor.execute("SELECT osu_username FROM users WHERE id=?", (from_id,)).fetchone()
        if limit is not None:
            limit = int(limit)
        else:
            limit = 1
        if not server or not username or username is None:
            raise exceptions.CustomException("Не удалось найти аккаунт в базе, попробуйте указать сервер и ник.\n Например: !last bancho cookiezi")
        if isinstance(server, tuple):
            server = server[0]
        if isinstance(username, tuple):
            username = username[0]            
        return { "server" : server, "username" : username.strip(), "limit" : limit}

def getUserFromDB(cursor, from_id):
    server, username = cursor.execute("SELECT server, osu_username FROM users WHERE id=?", (from_id,)).fetchone()
    return { "server" : server, "username" : username }

def getRole(vk, user_id):
    user_id = str(user_id)
    if "id" in user_id:
        user_id = re.search(r'\d+', user_id).group(0)
    if int(user_id) in glob.config['admin']:
        return 'Роль: админ'
    elif user_id in glob.config["donators"]:
        role_name = glob.config["donators"][user_id].get("role_name", "донатер")
        return 'Роль: {}\nВы будете донатером до {} (-2 от мск)'.format(
            role_name, glob.config["donators"][user_id]["expires"])
    return 'Роль: юзер'

def isRestricted(user_id):
    user_id = str(user_id)
    return user_id in glob.config["restricted"]