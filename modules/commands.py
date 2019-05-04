import datetime
import json
import logging
from vk_api import VkUpload

import requests

from . import fun
from .levels import LevelSystem
from . import utils
from .admin import Admin
from helpers import checks
from constants import exceptions
from .osu import Osu
from objects import glob


class CommandsHandler:
    def __init__(self, vk, upload, event):
        self.vk = vk
        self.upload = upload
        self.event = event.obj
        self.parsed_msg = self.parse_command(self.event)
        self.key = self.parsed_msg.get("key").lower()
        self.value = self.parsed_msg.get("value")
        self.request = requests.Session()
        self.level = LevelSystem(self.vk)
        self.admin = Admin(self.event.from_id)
        self.osu = Osu(glob.config["osu_api_key"], self.event.from_id, self.upload)
        self.data = {
            "peer_id" : self.event.peer_id,
            "message": None,
            "attachment": None
        }

    def process_message(self):
        """
        Функция, обрабатывающая сообщение
        :return : значение команды в формате text, attachment, если это tuple,
                    иначе None
        """
        self.level.levelCheck(self.event.peer_id,
                              self.event.from_id,
                              self.event.text)
        self.donatorCheck()
        if self.event.text.startswith("!"):
            value = self.process_command()
            if value is not None:
                if isinstance(value, tuple):
                    self.data["message"] = value[0]
                    self.data["attachment"] = value[1]
                else:
                    self.data["message"] = value
                return self.data
            return None

    def process_command(self):
        # ---- Commands managing ----
        if self.key == "addpic":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return utils.addpic(self.upload,
                                self.value,
                                self.event.attachments)
        if self.key == "delpic":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return utils.delcom(self.value)
        if self.key == "addcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return utils.addcom(self.value)
        if self.key == "delcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return utils.delcom(self.value)
        if self.key == "editcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return utils.editcom(self.value)
        # ---- Built-in ----
        if self.key in ["help", "хелп"]:
            self.data["peer_id"] = self.event.from_id
            return "\n".join(glob.commands.keys())
        if self.key in glob.commands:
            return self.static_cmd()
        if self.key in ["role", "роль"]:
            return self.getRole(self.event.from_id)
        if self.key == "osuset":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return self.osu.osuset(self.parsed_msg["value"])
        # ---- Donators ----
        if self.key == "add_donator":
            if not checks.isAdmin(self.event.from_id):
                raise exceptions.NoAdminPermissions("Нет прав, команда для админов")
            text = self.value.split(" ")
            return self.admin.add_donator(text[0], text[1] if text[1] else 25)
        if self.key == "rm_donator":
            if not checks.isAdmin(self.event.from_id):
                raise exceptions.NoAdminPermissions("Нет прав, команда для админов")
            return self.admin.remove_donator(self.parsed_msg['value'])
        # ---- Tracking ----
        if self.key == "track":
            pass
        if self.key == "untrack":
            pass
        if self.key == "tracking":
            pass
        #  ---- Levels ----
        if self.key in ["lvl", "лвл", "level"]:
            return self.level.show_lvl(self.event.from_id)
        if self.key in ["leaderboard", "лидерборд"]:
            return self.level.show_leaderboard()
        #  ---- osu!lemmy ----
        if self.key in ["osu", "осу"]:
            return self.osu.lemmyPicture(self.value, 0)
        if self.key in ["taiko", "тайко"]:
            return self.osu.lemmyPicture(self.value, 1)
        if self.key in ["ctb", "ктб"]:
            return self.osu.lemmyPicture(self.value, 2)
        if self.key in ["mania", "мания"]:
            return self.osu.lemmyPicture(self.value, 3)
        # ---- osu! stats ----
        if self.key in ["top"]:
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            userData = utils.getServerUsername(self.value, self.event.from_id)
            return self.osu.getUserBest(userData)
        if self.key in ["last", "recent", "ласт"]:
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            userData = utils.getServerUsername(self.value, self.event.from_id)
            return self.osu.getUserRecent(userData)
        # ---- Fun ----
        if self.key in ["weather", "погода"]:
            return fun.weather(self.value)
        if self.key in ["roll", "ролл"]:
            return fun.roll(self.value)

    def donatorCheck(self):
        if not self.admin.stillDonator():
            self.admin.remove_donator(self.event.from_id)
            vk_api_name = self.vk.users.get(
                    user_ids = self.event.from_id, 
                    name_case = 'gen')[0]
            self.vk.messages.send(
                peer_id= self.event.peer_id,
                message = "Минус донатер у *id{}({} {})".format(
                    self.event.from_id,
                    vk_api_name['first_name'],
                    vk_api_name['last_name']))
            
    def parse_command(self, event):
        """
        Функция парсит сообщение на словарь, 
        состоящий из команды, значения и первого изображения в сообщении
        :param event: VK API event
        """
        parsed_msg = {}
        text = event.text.split(" ")
        parsed_msg['key'] = text[0][1:].lower()
        parsed_msg['value'] = " ".join(text[1:])
        return parsed_msg

    def static_cmd(self):
        """
        Вызов команды из базы
        :return : text, attachment
        """
        attachment = None
        message = None
        message = glob.commands[self.key].get("message", None)
        attachment = glob.commands[self.key].get("attachment", None)
        if message is not None:        
            message = message.replace("&quot;", '"')
        return message, attachment

    def getRole(self, user_id):
        if user_id in glob.config['admin']:
            return 'Роль: админ'
        elif str(user_id) in glob.config['donators']:
            date = datetime.datetime.strptime(
                glob.config['donators'][str(user_id)], "%Y-%m-%d %H:%M:%S")
            date_now = datetime.datetime.now()
            delta = date.year - date_now.year
            if delta >= 1:
                return 'Роль: супердонатер\nВы будете гением до ' \
                    + glob.config['donators'][str(user_id)]+" (-2 от мск)"
            return 'Роль: донатер\nВы будете донатером до ' \
                + glob.config['donators'][str(user_id)]+" (-2 от мск)"
        return 'Роль: юзер'
