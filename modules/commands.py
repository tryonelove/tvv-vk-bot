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
    def __init__(self, vk, event):
        self.vk = vk
        self.event = event.obj
        self.parsed_msg = self.parse_command(self.event)
        self.key = self.parsed_msg.get("key").lower()
        self.value = self.parsed_msg.get("value")
        self.request = requests.Session()
        self.level = LevelSystem(self.vk)
        self.upload = VkUpload(self.vk)
        self.osu = Osu(glob.config["osu_api_key"], self.event.from_id)

    def process_message(self):
        """
        Функция, обрабатывающая сообщение
        :return : значение команды в формате text, attachment
        """
        self.level.levelCheck(self.event.peer_id,
                              self.event.from_id,
                              self.event.text)
        if self.event.text.startswith("!"):
            data = self.process_command()
            if isinstance(data, tuple):
                message, attach = data[0], data[1]
                return { "messageText" : message , "attach" : attach }
            return { "messageText" : message , "attach" : None }

    def process_command(self):
        # ---- Built-in ----
        if self.key in ["help", "хелп"]:
            return "\n".join(glob.commands.keys())
        if self.key in glob.commands:
            return self.static_cmd()
        if self.key in ["role", "роль"]:
            return self.getRole(self.event.from_id)
        if self.key == "osuset":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.osu.osuset(self.parsed_msg["value"])
        # ---- Commands managing ----
        if self.key == "addpic":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoDonorPermissions
            return utils.addpic(self.upload,
                                self.value,
                                self.event.attachments)
        if self.key == "delpic":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoDonorPermissions
            return utils.delcom(self.value)
        if self.key == "addcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoDonorPermissions
            return utils.addcom(self.value)
        if self.key == "delcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoDonorPermissions
            return utils.delcom(self.value)
        if self.key == "editcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoDonorPermissions
            return utils.editcom(self.value)
        # ---- Donators ----
        if self.key == "add_donator":
            if not checks.isAdmin(self.event.from_id):
                raise exceptions.NoAdminPermissions
            text = self.value.split(" ")
            return Admin(self.event.from_id).add_donator(text[0], text[1] if text[1] else 25)
        if self.key == "rm_donator":
            if not checks.isAdmin(self.event.from_id):
                raise exceptions.NoAdminPermissions
            return Admin(self.event.from_id).remove_donator(self.parsed_msg['value'])
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
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.osu.lemmyPicture(self.value)
        if self.key in ["taiko", "тайко"]:
            pass
        if self.key in ["ctb", "ктб"]:
            pass
        if self.key in ["mania", "мания"]:
            pass
        # ---- osu! stats ----
        if self.key == "top":
            pass
        if self.key in ["last", "recent", "ласт"]:
            pass
        # ---- Fun ----
        if self.key in ["weather", "погода"]:
            return fun.weather(self.value)
        if self.key in ["roll", "ролл"]:
            return fun.roll(self.value)

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
        msg = glob.commands[self.key].split(" ")
        if "photo" in msg[-1]:
            attachment = msg[-1]
            if len(msg) > 1:
                message = " ".join(msg[:-1]).replace("&quot;", '"')
            return message, attachment
        message = " ".join(msg).replace("&quot;", '"')
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
