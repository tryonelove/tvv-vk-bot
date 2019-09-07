import json
import datetime
import requests
import constants.exceptions as exceptions
from helpers.checks import isAdmin
from objects import glob
from .utils import config_update
from objects import glob

class Admin:
    def __init__(self, from_id, c):
        self.from_id = from_id
        self.c = c

    def isDonator(self, user_id):
        self.c.execute("SELECT id FROM donators")
        donators = [user[0] for user in self.c.fetchall()]
        return int(user_id) in donators
    
    def stillDonator(self, user_id):
        date = self.c.execute("SELECT expires FROM donators WHERE id = ?", (self.from_id,)).fetchone()
        if date is not None:
            date = date[0]
        else:
            return
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date_now = datetime.datetime.now()
        delta = date - date_now
        return True if delta.days > 0 else False

    def getRole(self, user_id):
        role = "Роль: {}"
        if user_id in glob.config["admin"]:
            return role.format("админ")
        elif self.isDonator(user_id):
            user = self.c.execute("SELECT expires, role_name FROM donators WHERE id=?", (user_id,)).fetchone()
            role+="\nВы будете донатером до {} (-2 от мск)"
            return role.format(user[1], user[0])
        else:
            return role.format("юзер")

    def add_donator(self, user_id, donation_sum, role_name):
        """
        Функция добавления донатера
        :param user_id: айди добавляемого пользователя
        :param donation_sum: сумма доната (кратная 25)
        """
        donation_sum = int(donation_sum)
        now = datetime.datetime.now()
        donator_duration = donation_sum // 25
        if self.isDonator(user_id):
            expires = self.c.execute("SELECT expires FROM donators WHERE id=?", (user_id,)).fetchone()[0]
            date = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
            date += datetime.timedelta(days=+31*donator_duration)
            self.c.execute("UPDATE donators SET expires = ? WHERE id = ?", (date.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        else:
            if donation_sum != 25:
                now += datetime.timedelta(days=+31*donator_duration)
            else:
                now += datetime.timedelta(days=+31)
                self.c.execute("INSERT INTO donators VALUES(?,?,?)", (user_id, now.strftime("%Y-%m-%d %H:%M:%S"), role_name))
        glob.db.commit()
        return "Пользователь {} получил роль донатера\n" \
                "Не забудьте привязать осу акк с помощью команды" \
                "!osuset bancho/gatari никнейм".format(user_id)

    def remove_donator(self, user_id):
        """
        Удаляет пользователя из донатеров
        :param user_id: айди пользователя
        """
        if self.isDonator(user_id):
            self.c.execute("DELETE FROM donators WHERE id=?",(user_id,))
            glob.db.commit()
            return "Пользователь {} был успешно удалён.".format(user_id)
        return "Пользователь {} не является донатером.".format(user_id)

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

    def add_role(self, text):
        text = text.split(" ", 1)
        user_id = text[0]
        role_name = " ".join(text[1:])
        if not self.isDonator(user_id):
            raise exceptions.CustomException("Такого пользователя нет в списке донатеров")
        self.c.execute("UPDATE donators SET role_name = ? WHERE id = ?", (role_name, self.from_id))
        glob.db.commit()
        return "Роль {} для {} была успешно добавлена".format(role_name, user_id)
    
    def rm_role(self, user_id):
        if not self.isDonator(user_id):
            raise exceptions.CustomException("Такого пользователя нет в списке донатеров")
        self.c.execute("UPDATE donators SET role_name = ? WHERE id = ?", (None, self.from_id))     
        glob.db.commit()
        return "Роль была успешно удалена"