import datetime
import json
import logging
from vk_api import VkUpload
import requests
from math import ceil

from . import fun
from .levels import LevelSystem
from . import utils
from .admin import Admin
from helpers import checks
from constants import exceptions
from .osu import Osu
from objects import glob
import sqlite3

class CommandsHandler:
    def __init__(self, vk, upload, event, cursor):
        self.vk = vk
        self.upload = upload
        self.event = event.obj
        self.parsed_msg = self.parse_command(self.event)
        self.key = self.parsed_msg.get("key").lower()
        self.value = self.parsed_msg.get("value")
        self.request = requests.Session()
        self.c = cursor
        self.level = LevelSystem(self.vk, self.event.peer_id, self.c)
        self.admin = Admin(self.event.from_id, self.c)
        self.osu = Osu(glob.config["osu_api_key"],self.c, self.event.from_id, self.upload)
        self.data = {
            "peer_id" : self.event.peer_id,
        }

    def preProcessor(self):
        self.level.levelCheck(self.event.peer_id,
                              self.event.from_id,
                              self.event.text)
        self.donatorCheck()
        # self.osu.findBeatmap(self.vk.messages.send, self.event)

    def processMessage(self):
        """
        Функция, обрабатывающая сообщение
        :return : значение команды в формате text, attachment, если это tuple,
                    иначе None
        """
        self.preProcessor()
        if self.event.text.startswith("!"):
            if utils.isRestricted(self.event.from_id):
                return None
            value = self.processCommand()
            if value is not None:
                if isinstance(value, tuple):
                    self.data["message"] = value[0]
                    self.data["attachment"] = value[1]
                else:
                    self.data["message"] = value
                return self.data
            return None

    def processCommand(self):
        # ---- Commands managing ----
        if self.key in ["addcom", "editcom"]:
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            if self.event.attachments:
                return utils.addpic(
                                    self.event.from_id,
                                    self.upload,
                                    self.value,
                                    self.event.attachments)
            return utils.addcom(self.event.from_id, self.value)
        if self.key == "delcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            if not checks.commandAdder(self.event.from_id, self.value):
                raise exceptions.NoEditPermissions
            return utils.delcom(self.value)
        # ---- Built-in ----
        if self.key in ["help", "хелп"]:
            return self.generateHelp()
        if self.key in glob.commands:
            return self.static_cmd()
        if self.key in ["role", "роль"]:
            user = self.event.from_id if not self.value else self.value
            return utils.getRole(self.vk, user)
        if self.key == "osuset":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.osu.osuset(self.parsed_msg["value"])
        if self.key == "op":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.op(self.value)
        if self.key == "deop":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.deop(self.value)
        if self.key == "restrict":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.restrict(self.value)   
        if self.key == "unrestrict":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.unrestrict(self.value)
        if self.key == ["add_role", "edit_role"]:
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.add_role(self.value)
        if self.key == "rm_role":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions
            return self.admin.rm_role(self.value)
        # ---- Donators ----
        if self.key == "add_donator":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoAdminPermissions
            text = self.value.split(" ")
            return self.admin.add_donator(text[0], text[1], " ".join(text[2:]) if len(text)>2 else None)
        if self.key == "rm_donator":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoAdminPermissions
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
        if self.key == "edit_exp":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoAdminPermissions
            user_id, expEdit = self.value.split()
            return self.level.edit_exp(user_id, expEdit)
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
            userData = utils.getServerUsername(self.c, self.value, self.event.from_id)
            return self.osu.getUserBest(userData)
        if self.key in ["last", "recent", "ласт", "rs"]:
            userData = utils.getServerUsername(self.c, self.value, self.event.from_id)
            return self.osu.getUserRecent(userData)
        if self.key in ["c", "compare", "с"]:
            if not self.event["fwd_messages"]:
                raise exceptions.ScoreMessageNotFound
            return self.osu.compare(self.event["fwd_messages"][-1], self.value)
        if self.key in ["newpp"]:
            self.data["peer_id"] = self.event.from_id
            return self.osu.rebalancedPP(self.value)
        # ---- Fun ----
        if self.key in ["weather", "погода"]:
            return fun.weather(self.value)
        if self.key in ["roll", "ролл"]:
            return fun.roll(self.value)

    def generateHelp(self):
        k = 50
        if self.value == "":
            page = 0
        else:
            page = int(self.value) - 1
        page_num = ceil(len(glob.commands.keys()) / k)
        self.data["peer_id"] = self.event.from_id
        text = "Страница {} из {}\n------------------------\n".format(page+1, page_num)
        page_start = page*k
        commands = list(glob.commands.keys())[page_start:page_start+k]
        text+= "\n".join(commands)
        return text

    def donatorCheck(self):
        if not self.admin.stillDonator(self.event.from_id) and self.admin.isDonator(self.event.from_id):
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
