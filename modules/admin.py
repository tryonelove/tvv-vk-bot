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
            date = datetime.datetime.strptime(glob.config["donators"][str(self.from_id)]["expires"], "%Y-%m-%d %H:%M:%S")
            date_now = datetime.datetime.now()
            delta = date - date_now
            return True if delta.days > 0 else False
        return True

    def add_donator(self, user_id, donation_sum, role_name):
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
            date = datetime.datetime.strptime(glob.config["donators"][user_id]["expires"], "%Y-%m-%d %H:%M:%S")
            date += datetime.timedelta(days=+31*donator_duration)
            glob.config["donators"][user_id]["expires"] = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if donation_sum != 25:
                now += datetime.timedelta(days=+31*donator_duration)
            else:
                now += datetime.timedelta(days=+31)
            glob.config["donators"][user_id] = {}
            glob.config["donators"][user_id]["expires"] = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            glob.config["donators"][user_id]["role_name"] = role_name
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
        return "Чел {} был удалён из админов!".format(user_id)

    def restrict(self, user_id):
        """
        Запрещает доступ пользователя к командам
        :param user_id: айди пользователя
        """
        glob.config["restricted"].append(user_id)
        config_update()
        return "{} теперь не может юзать бота. бб очередняра".format(user_id)

    def unrestrict(self, user_id):
        """
        Разрешает доступ пользователя к командам
        :param user_id: айди пользователя
        """
        glob.config["restricted"].remove(user_id)
        config_update()
        return "{} теперь может юзать бота".format(user_id)

    def bot_help(self):
        text = "Команды для донатеров/админов:\npic\nlast\ntop\nosuset\n\n \
                Дефолтные команды:\nпогода\nosu\nmania\ntaiko" \
                + "\n" + "\n".join(glob.commands.keys())
        return text

