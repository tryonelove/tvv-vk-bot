import json
import datetime
import requests
import constants.exceptions as exceptions
from helpers.checks import isAdmin
from objects import glob
from .utils import config_update
from objects import glob

class Admin:
    def __init__(self, from_id):
        self.from_id = from_id
    
    def stillDonator(self):
        if str(self.from_id) in glob.config["donators"]:
            date = datetime.datetime.strptime(glob.config["donators"][str(self.from_id)], "%Y-%m-%d %H:%M:%S")
            date_now = datetime.datetime.now()
            delta = date - date_now
            return True if delta.days > 0 else False
        return True

    def add_donator(self, user_id, donation_sum = 25):
        """
        Функция добавления донатера
        :param user_id: айди добавляемого пользователя
        :param donation_sum: сумма доната (кратная 25)
        """
        donation_sum = int(donation_sum)
        user_id = str(user_id)
        now = datetime.datetime.now()
        donator_duration = donation_sum // 25
        if user_id in glob.config["donators"]:
            date = datetime.datetime.strptime(glob.config["donators"][user_id], "%Y-%m-%d %H:%M:%S")
            date += datetime.timedelta(days=+31*donator_duration)
            glob.config["donators"][user_id] = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if donation_sum != 25:
                now += datetime.timedelta(days=+31*donator_duration)
            else:
                now += datetime.timedelta(days=+31)
            glob.config["donators"][user_id] = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        config_update()
        return "Пользователь {} получил роль донатера\n" \
                "Не забудьте привязать осу акк с помощью команды" \
                "!osuset bancho/gatari никнейм".format(user_id)

    def remove_donator(self, from_id):
        """
        Удаляет пользователя из донатеров
        :param user_id: айди пользователя
        """
        from_id = str(from_id)
        if from_id in glob.config["donators"]:
            del glob.config["donators"][from_id]
            config_update()
            return "Пользователь {} был успешно удалён.".format(from_id)
        return "Пользователь {} не является донатером.".format(from_id)

    def op(self, user_id):
        """
        Добавляет пользователя как админа
        :param user_id: айди пользователя
        """
        glob.config["admin"].append(user_id)
        config_update()
        return "Чел {} был добавлен как админ!".format(user_id)
    
    def deop(self, user_id):
        """
        Удаляет пользователя из админов
        :param user_id: айди пользователя
        """
        glob.config["admin"].remove(user_id)
        config_update()
        return "Чел {user_id} был удалён из админов!".format(user_id)

    def bot_help(self):
        text = "Команды для донатеров/админов:\npic\nlast\ntop\nosuset\n\n \
                Дефолтные команды:\nпогода\nosu\nmania\ntaiko" \
                + "\n" + "\n".join(glob.commands.keys())
        return text

