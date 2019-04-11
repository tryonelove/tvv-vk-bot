import json
import vk_api
import logging
from helpers.checks import *
from objects import glob
from .utils import users_update

class LevelSystem:
    def __init__(self, vk):
        self.vk = vk
    
    def users_update(self):
        with open('users.json', 'w') as f:
            json.dump(glob.users, f, indent=4)

    def update_data(self, user_id):
        if user_id not in glob.users.keys():
            glob.users[user_id] = {}
            glob.users[user_id]['experience'] = 0
            glob.users[user_id]['level'] = 1
            data = self.vk.users.get(user_ids=user_id)[0]
            full_name =  data["first_name"] + " " + data['last_name']
            glob.users[user_id]['full_name'] = full_name
            users_update()
    
    def add_exp(self, user_id ,exp):
        glob.users[user_id]['experience'] += exp
        users_update()

    def level_up(self, user_id, peer_id):
        experience = glob.users[user_id]['experience']
        lvl_start = glob.users[user_id]['level']
        lvl_end = int(experience ** (1/3))
        data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
        if lvl_start < lvl_end:
            if lvl_end>=7:
                username =  data["first_name"] + " " + data["last_name"]
                self.vk.messages.send(peer_id = peer_id, message="{} апнул {} лвл!".format(username, lvl_end))
            glob.users[user_id]['level'] = lvl_end
    
    def show_lvl(self, user_id):
        user_id = str(user_id)
        if user_id in glob.users:
            lvl_start = glob.users[user_id]['level']
            data = self.vk.users.get(user_id=int(user_id), name_case = "nom")[0]
            username =  data["first_name"] + " " + data["last_name"]
            text = "{}, ваша статистика:\nУровень: {}\nОпыт: {}/{}XP".format(username, 
                                        glob.users[user_id]['level'],
                                        glob.users[user_id]['experience'], 
                                        (lvl_start+1)**3)
            return text
        return "Вас нету в базе, попробуйте написать что-нибудь в конфе osu!community"
    
    def show_leaderboard(self):
        text = "Топ 10 конфы osu!community:\n\n"
        leaderboard_user_ids = glob.users.values()
        leaderboard = sorted(leaderboard_user_ids, key=lambda leaderboard_user_ids: leaderboard_user_ids["experience"], reverse=True)
        for i in range(10):
            rank = i+1
            full_name = leaderboard[i]['full_name']
            exp = leaderboard[i]['experience']
            level = leaderboard[i]['level']
            text+= '#{rank} {full_name} {experience}XP ({level}lvl)\n'.format(rank=rank,full_name = full_name, experience = exp, level=level)
        return text

    def levelCheck(self, peer_id, from_id, text):
        """
        Функция проверяет на левел + обновляет экспу
        :param peer_id: ID чата с отправителем
        :param from_id: ID пользователя
        """
        if not isMainChat(peer_id):
            return  
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