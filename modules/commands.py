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
        if self.key == "addcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            if self.event.attachments:
                return utils.addpic(
                                    self.event.from_id,
                                    self.upload,
                                    self.value,
                                    self.event.attachments)
            return utils.addcom(self.event.from_id, self.value)
        if self.key == "delcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            if not checks.commandAdder(self.event.from_id, self.value):
                raise exceptions.NoPrivilegesPermissions("Удалять команды могут их создатели или админы")
            return utils.delcom(self.value)
        if self.key == "editcom":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            if not checks.commandAdder(self.event.from_id, self.value):
                raise exceptions.NoPrivilegesPermissions("Изменять команды могут их создатели или админы")
            if self.event.attachments:
                return utils.addpic(
                                    self.event.from_id,
                                    self.upload,
                                    self.value,
                                    self.event.attachments)
        # ---- Built-in ----
        if self.key in ["help", "хелп"]:
            self.data["peer_id"] = self.event.from_id
            text = "osu \ taiko \ mania \ ctb\n"
            text+= "top\n"
            text+= "last \ recent \ rs \ ласт\n"
            text+= "погода \ weather\n"
            text+= "roll \ ролл\n"
            text+= "\n----------------------------\n"
            text+= "\n".join(glob.commands.keys())
            return text
        if self.key in glob.commands:
            return self.static_cmd()
        if self.key in ["role", "роль"]:
            return utils.getRole(self.event.from_id)
        if self.key == "osuset":
            if not checks.hasPrivileges(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав, однако ты можешь задонатить и взамен получить возможность юзать эту команду"
                    )
            return self.osu.osuset(self.parsed_msg["value"])
        if self.key == "op":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав"
                    )
            return self.admin.op(self.value)
        if self.key == "deop":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoPrivilegesPermissions(
                    "Недостаточно прав"
                    )
            return self.admin.deop(self.value)
        # ---- Donators ----
        if self.key == "add_donator":
            if not checks.isOwner(self.event.from_id):
                raise exceptions.NoAdminPermissions("Нет прав, команда для админов")
            text = self.value.split(" ")
            return self.admin.add_donator(text[0], text[1], " ".join(text[2:]) if len(text)>2 else "донатер")
        if self.key == "rm_donator":
            if not checks.isOwner(self.event.from_id):
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
            userData = utils.getServerUsername(self.value, self.event.from_id)
            return self.osu.getUserBest(userData)
        if self.key in ["last", "recent", "ласт", "rs"]:
            userData = utils.getServerUsername(self.value, self.event.from_id)
            return self.osu.getUserRecent(userData)
        if self.key in ["c", "compare", "с"]:
            if not self.event["fwd_messages"]:
                raise exceptions.ArgumentError("Необходимо переслать сообщение со скором")
            return self.osu.compare(self.event["fwd_messages"][-1], self.value)
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
