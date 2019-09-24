import json
import datetime
import requests
import constants.exceptions as exceptions
from helpers.checks import isAdmin
from objects import glob
from objects import glob
from . import utils

class Admin:
    def __init__(self, from_id):
        self.from_id = from_id

    def add_donator(self, user_id, donation_sum, role_name):
        """
        Функция добавления донатера
        :param user_id: айди добавляемого пользователя
        :param donation_sum: сумма доната (кратная 25)
        """
        donation_sum = int(donation_sum)
        now = datetime.datetime.now()
        donator_duration = donation_sum // 25      
        if utils.isDonator(user_id):                  
            expires = glob.c.execute("SELECT expires FROM donators WHERE id=?", (user_id,)).fetchone()[0]
            date = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
            date += datetime.timedelta(days=+31*donator_duration)
            glob.c.execute("UPDATE donators SET expires = ? WHERE id = ?", (date.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        else:                  
            now += datetime.timedelta(days=+31*donator_duration)
            glob.c.execute("INSERT INTO donators VALUES(?,?,?)", (user_id, now.strftime("%Y-%m-%d %H:%M:%S"), role_name))                       
        glob.db.commit()                        
        return "Пользователь {} получил роль донатера\n" \
                "Не забудьте привязать осу акк с помощью команды" \
                "!osuset bancho/gatari никнейм".format(user_id)

    def remove_donator(self, user_id):
        """
        Удаляет пользователя из донатеров
        :param user_id: айди пользователя
        """
        if utils.isDonator(user_id):
            glob.c.execute("DELETE FROM donators WHERE id=?",(user_id,))
            glob.db.commit()
            return "Пользователь {} был успешно удалён.".format(user_id)
        return "Пользователь {} не является донатером.".format(user_id)

    def op(self, user_id):
        """
        Добавляет пользователя как админа
        :param user_id: айди пользователя
        """
        glob.config["admin"].append(user_id)
        utils.config_update()
        return "Чел {} был добавлен как админ!".format(user_id)
    
    def deop(self, user_id):
        """
        Удаляет пользователя из админов
        :param user_id: айди пользователя
        """
        glob.config["admin"].remove(user_id)
        utils.config_update()
        return "Чел {} был удалён из админов!".format(user_id)

    def restrict(self, user_id):
        """
        Запрещает доступ пользователя к командам
        :param user_id: айди пользователя
        """
        glob.config["restricted"].append(user_id)
        utils.config_update()
        return "{} теперь не может юзать бота. бб очередняра".format(user_id)

    def unrestrict(self, user_id):
        """
        Разрешает доступ пользователя к командам
        :param user_id: айди пользователя
        """
        glob.config["restricted"].remove(user_id)
        utils.config_update()
        return "{} теперь может юзать бота".format(user_id)

    def add_role(self, text):
        text = text.split(" ", 1)
        user_id = text[0]
        role_name = " ".join(text[1:])       
        if not utils.isDonator(user_id):                    
            raise exceptions.CustomException("Такого пользователя нет в списке донатеров")
        glob.c.execute("UPDATE donators SET role_name = ? WHERE id = ?", (role_name, user_id))                           
        glob.db.commit()                                   
        return "Роль {} для {} была успешно добавлена".format(role_name, user_id)
    
    def rm_role(self, user_id):
        if not utils.isDonator(user_id):
            raise exceptions.CustomException("Такого пользователя нет в списке донатеров")
        glob.c.execute("UPDATE donators SET role_name = ? WHERE id = ?", (None, user_id))     
        glob.db.commit()
        return "Роль была успешно удалена"