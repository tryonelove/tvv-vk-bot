from objects import glob
from . import utils

class LevelSystem:
    def __init__(self, user_id, chat_id):
        self._user_id = user_id
        self._chat_id = chat_id

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

    def update_data(self, user_id):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self._chat_id)
        glob.c.execute(q, (self._user_id,))
        if not glob.c.fetchall():
            data = glob.vk.users.get(user_ids=self._user_id)[0]
            full_name =  data["first_name"] + " " + data['last_name']
            glob.c.execute("INSERT OR IGNORE INTO users(id, name) VALUES(?, ?)", (user_id, full_name))
            glob.c.execute("INSERT OR IGNORE INTO konfa_{} VALUES(?, ?, ?)".format(self._chat_id), (user_id, 0, 1))
            glob.db.commit()

    def get_level(self, user_id, chat_id):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self._chat_id)
        executed = glob.c.execute(q, (self._user_id,)).fetchone()
        if executed:
            _, experience, lvl_start = executed
            user_info = glob.vk.users.get(user_id=int(self._user_id), name_case="nom")[0]
            full_name = f"{user_info['first_name']} {user_info['last_name']}"
            message = "{}, ваша статистика:\n  \
                            Уровень: {}\n \
                            Опыт: {}/{}XP".format(
                            full_name, 
                            lvl_start,
                            experience, 
                            (lvl_start+1)**3)
            return message

    def add_exp(self, user_id, chat_id, exp):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self._chat_id)
        q_update = "UPDATE konfa_{} SET experience=? WHERE id=?".format(self._chat_id)
        glob.c.execute(q, (self._user_id,))
        old = glob.c.fetchone()[1]
        new_exp = old + exp
        glob.c.execute(q_update, (new_exp, self._user_id))
        glob.db.commit()

    def get_leaderboard(self, chat_id):
        text = "Топ 10 конфы:\n\n"
        leaderboard = glob.c.execute("""
        SELECT id, experience, level FROM konfa_{0} 
        ORDER BY experience DESC LIMIT 10 
        """.format(self._chat_id)).fetchall()
        user_ids = [user[0] for user in leaderboard]
        users = glob.vk.users.get(user_ids=user_ids)
        for user_index, _ in enumerate(leaderboard):
            rank = user_index+1
            full_name = "{} {}".format(users[user_index]["first_name"], users[user_index]["last_name"])
            exp = leaderboard[user_index][1]
            level = leaderboard[user_index][2]
            text+= '#{rank} {full_name} {experience}XP ({level}lvl)\n'.format(rank=rank,full_name = full_name, experience = exp, level=level)
        return text

    
    

