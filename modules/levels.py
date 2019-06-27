import json
import vk_api
import logging
from helpers.checks import *
from objects import glob
from . import utils

class LevelSystem:
    def __init__(self, vk, cursor):
        self.vk = vk
        self.c = cursor

    def update_data(self, user_id):
        self.c.execute("SELECT * FROM levels WHERE id=?", (user_id,))
        if not self.c.fetchall():
            data = self.vk.users.get(user_ids=user_id)[0]
            full_name =  data["first_name"] + " " + data['last_name']
            utils.insertUsers(self.c, user_id, full_name, None, None)
            utils.insertLevels(self.c, user_id, 0, 1)
            glob.db.commit()
    
    def add_exp(self, user_id ,exp):
        self.c.execute("SELECT experience FROM levels WHERE id=?", (user_id,))
        old = self.c.fetchone()
        new_exp = old[0] + exp
        self.c.execute("UPDATE levels SET experience=? WHERE id=?", (new_exp, user_id))
        glob.db.commit()

    def level_up(self, user_id, peer_id):
        experience, lvl_start = self.c.execute("SELECT experience, level FROM levels WHERE id=?", (user_id,)).fetchone()
        lvl_end = int(experience ** (1/3))
        data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
        if lvl_start < lvl_end:
            if lvl_end>=7:
                username =  data["first_name"] + " " + data["last_name"]
                self.vk.messages.send(peer_id = peer_id, message="{} апнул {} лвл!".format(username, lvl_end))
            self.c.execute("UPDATE levels SET level=? WHERE id=?", (lvl_end, user_id))
            glob.db.commit()
    
    def show_lvl(self, user_id):
        self.c.execute("SELECT * FROM levels WHERE id=?", (user_id,))
        if self.c.fetchall():
            _, experience, lvl_start = self.c.execute("SELECT * FROM levels WHERE id=?", (user_id,)).fetchone()
            data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
            username =  data["first_name"] + " " + data["last_name"]
            text = "{}, ваша статистика:\nУровень: {}\nОпыт: {}/{}XP".format(username, 
                                        lvl_start,
                                        experience, 
                                        (lvl_start+1)**3)
            return text
        return "Вас нету в базе, попробуйте что-нибудь написать в конфе osu!community"
    
    def show_leaderboard(self):
        text = "Топ 10 конфы osu!community:\n\n"
        leaderboard = self.c.execute("""
        SELECT name, experience, level FROM levels 
        INNER JOIN users ON levels.id=users.id ORDER BY experience DESC LIMIT 10 
        """).fetchall()
        for i in range(10):
            rank = i+1
            full_name = leaderboard[i][0]
            exp = leaderboard[i][1]
            level = leaderboard[i][2]
            text+= '#{rank} {full_name} {experience}XP ({level}lvl)\n'.format(rank=rank,full_name = full_name, experience = exp, level=level)
        return text

    def levelCheck(self, peer_id, from_id, text):
        """
        Функция проверяет на левел + обновляет экспу
        :param peer_id: ID чата с отправителем
        :param from_id: ID пользователя
        """
        # if not isMainChat(peer_id):
            # return  
        message = text.split()
        from_id = str(from_id)
        self.update_data(from_id)
        k = self.calc_exp(message)        
        self.add_exp(from_id, k)
        self.level_up(from_id, peer_id)       

    @staticmethod
    def calc_exp(message):
        k = 0
        if len(message)<100:
            for word in message:
                length = len(word)
                if length<=4:
                    k += 0.25
                    continue
                if length<=7:
                    k += 0.5
                    continue
                if length>7:
                    k += 1
                    continue
        return k