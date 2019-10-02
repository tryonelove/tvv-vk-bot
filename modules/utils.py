import json
import requests
from constants import exceptions
from objects import glob
import re
from helpers import checks
import datetime

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
    Функция перезаписи users.db
    """
    glob.db.commit()

def insertUser(user_id, name=None):
    glob.c.execute("INSERT OR IGNORE INTO users(id, name) VALUES(?, ?)", (user_id, name))

def insertLevels(chat_id, user_id, experience=None, level=None):
    glob.c.execute("INSERT OR IGNORE INTO konfa_{} VALUES(?, ?, ?)".format(chat_id), (user_id, experience, level))

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
        raise exceptions.ArgumentError
    if key in glob.commands and not checks.commandAdder(from_id, key):
        raise exceptions.NoEditPermissions
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
        raise exceptions.NoEditPermissions
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

def getUserFromDB(from_id):
    server, username = glob.c.execute("SELECT server, osu_username FROM users WHERE id=?", (from_id,)).fetchone()
    return { "server" : server, "username" : username }

def setServerUsername(src, text):
    text = checkArgs(text)
    server = username = None
    limit = 1
    if text is not None:
        r = re.search(r'(bancho|gatari)?(?:\s)?(.*?)(?:\s)?(\d+)?$', text)
        if r:
            server = r.group(1)
            username = r.group(2)
            limit = r.group(3)
    if server:
        src["server"] = server.strip()
    if username:
        src["username"] = username.strip()
    if limit:
        src["limit"] = int(limit)
    if None in src.values():
        raise exceptions.dbUserNotFound
    return src

def formatServerUsername(from_id, text):
    return setServerUsername(getUserFromDB(from_id), text)

def isRestricted(user_id):
    user_id = str(user_id)
    return user_id in glob.config["restricted"]


def isDonator(user_id):
    return glob.c.execute("SELECT id FROM donators WHERE id = ?", (user_id,)).fetchone() is not None

def stillDonator(user_id):
    date = glob.c.execute("SELECT expires FROM donators WHERE id = ?", (user_id,)).fetchone()
    if date is not None:
        date = date[0]
    else:
        return
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_now = datetime.datetime.now()
    delta = date - date_now
    return True if delta.days > 0 else False

def getRole(user_id):
    role = "Роль: {}"
    if user_id in glob.config["admin"]:
        return role.format("админ")
    elif isDonator(user_id):
        user = glob.c.execute("SELECT expires, role_name FROM donators WHERE id=?", (user_id,)).fetchone()
        role+="\nВы будете донатером до {} (-2 от мск)"
        return role.format(user[1] if user[1] is not None else "донатер", user[0])
    else:
        return role.format("юзер")