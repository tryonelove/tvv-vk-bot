import json
import vk_api
import logging
from helpers.checks import *
from objects import glob
from . import utils

class LevelSystem:
    def __init__(self, vk, chat_id, cursor):
        self.vk = vk
        self.chat_id = chat_id
        self.c = cursor

    def levelCheck(self, peer_id, from_id, text):
        """
        Функция проверяет на левел + обновляет экспу

        :param peer_id: ID чата с отправителем
        :param from_id: ID пользователя
        """
        if from_id < 0 or peer_id < 2000000000:
            return
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS konfa_{} 
        (id INTEGER PRIMARY KEY, experience FLOAT, level INTEGER, 
        FOREIGN KEY(id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE)
        """.format(peer_id))
        message = text.split()
        from_id = str(from_id)
        self.update_data(from_id)
        k = self.calc_exp(message)
        self.add_exp(from_id, k)
        self.level_up(from_id, peer_id)       

    def update_data(self, user_id):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self.chat_id)
        self.c.execute(q, (user_id,))
        if not self.c.fetchall():
            data = self.vk.users.get(user_ids=user_id)[0]
            full_name =  data["first_name"] + " " + data['last_name']
            utils.insertUser(self.c, user_id, full_name)
            utils.insertLevels(self.c, self.chat_id, user_id, 0, 1)
            glob.db.commit()
    
    def add_exp(self, user_id ,exp):
        q_select = "SELECT * FROM konfa_{} WHERE id=?".format(self.chat_id)
        q_update = "UPDATE konfa_{} SET experience=? WHERE id=?".format(self.chat_id)
        self.c.execute(q_select, (user_id,))
        old = self.c.fetchone()[1]
        new_exp = old + exp
        self.c.execute(q_update, (new_exp, user_id))
        glob.db.commit()
    
    def edit_exp(self, user_id ,exp):
        q = "SELECT experience FROM konfa_{} WHERE id=?".format(self.chat_id)
        q_update = "UPDATE konfa_{} SET experience=?, level=1 WHERE id=?".format(self.chat_id)
        self.c.execute(q, (user_id,))
        old = self.c.fetchone()[0]
        new_exp = old + int(exp)
        self.c.execute(q_update, (new_exp, user_id))
        glob.db.commit()
        return "Экспа была успешно изменена"

    def level_up(self, user_id, peer_id):
        q = "SELECT experience, level FROM konfa_{} WHERE id=?".format(self.chat_id)
        q_upd = "UPDATE konfa_{} SET level=? WHERE id=?".format(self.chat_id)
        experience, lvl_start = self.c.execute(q, (user_id,)).fetchone()
        lvl_end = int(experience ** (1/3))
        data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
        if lvl_start < lvl_end:
            if lvl_end>=7:
                username =  data["first_name"] + " " + data["last_name"]
                self.vk.messages.send(peer_id = peer_id, message="{} апнул {} лвл!".format(username, lvl_end))
            self.c.execute(q_upd, (lvl_end, user_id))
            glob.db.commit()
    
    def show_lvl(self, user_id):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self.chat_id)
        self.c.execute(q, (user_id,))
        if self.c.fetchall():
            _, experience, lvl_start = self.c.execute(q, (user_id,)).fetchone()
            data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
            username =  data["first_name"] + " " + data["last_name"]
            text = "{}, ваша статистика:\nУровень: {}\nОпыт: {}/{}XP".format(username, 
                                        lvl_start,
                                        experience, 
                                        (lvl_start+1)**3)
            return text
        return "error?"
    
    def show_leaderboard(self):
        text = "Топ 10 конфы:\n\n"
        leaderboard = self.c.execute("""
        SELECT name, experience, level FROM konfa_{0} 
        INNER JOIN users ON konfa_{0}.id=users.id ORDER BY experience DESC LIMIT 10 
        """.format(self.chat_id)).fetchall()
        for i, user in enumerate(leaderboard):
            rank = i+1
            full_name = leaderboard[i][0]
            exp = leaderboard[i][1]
            level = leaderboard[i][2]
            text+= '#{rank} {full_name} {experience}XP ({level}lvl)\n'.format(rank=rank,full_name = full_name, experience = exp, level=level)
        return text


    @staticmethod
    def calc_exp(message):
        k = 0
        if len(message)>100:
            return 0
        for word in message:
            length = len(word)
            if length<=4:
                k += 0.25
            elif length<=7:
                k += 0.5
            elif length>7:
                k += 1
        return k