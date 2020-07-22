from objects import glob
from helpers import utils
import logging


class LevelSystem:
    def __init__(self, user_id, chat_id):
        self._user_id = user_id
        self._chat_id = chat_id

    def level_check(self, message):
        # Skip bot accounts
        if self._user_id < 0:
            return
        # Still need to add user to db if doesn't exist
        glob.c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (self._user_id,))
        # Skip private vonversations
        if self._chat_id < 2000000000:
            return
        glob.c.execute("""
            CREATE TABLE IF NOT EXISTS konfa_{} 
            (id INTEGER PRIMARY KEY, experience FLOAT DEFAULT 0, level INTEGER DEFAULT 1, 
            FOREIGN KEY(id) REFERENCES users(id)
            ON DELETE CASCADE ON UPDATE CASCADE)
        """.format(self._chat_id))
        self.update_data()
        k = self.calc_exp(message)
        self.add_exp(k)
        self.level_up()

    def level_up(self):
        q = "SELECT experience, level FROM konfa_{} WHERE id=?".format(self._chat_id)
        q_upd = "UPDATE konfa_{} SET level=? WHERE id=?".format(self._chat_id)
        experience, lvl_start = glob.c.execute(q, (self._user_id,)).fetchone()
        lvl_end = int(experience ** (1/3))
        data = glob.vk.users.get(user_id=int(self._user_id), name_case = "nom")[0]
        if lvl_start < lvl_end:
            # if lvl_end>=7:
            username =  f"{data['first_name']} {data['last_name']}"
            glob.vk.messages.send(peer_id = self._chat_id, message="{} апнул {} лвл!".format(username, lvl_end))
            glob.c.execute(q_upd, (lvl_end, self._user_id))
            glob.db.commit()

    @staticmethod
    def calc_exp(message):
        k = 0
        message = message.split()
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

    def update_data(self):
        q = f"SELECT * FROM konfa_{self._chat_id} WHERE id=?"
        glob.c.execute(q, (self._user_id,))
        if not glob.c.fetchall():
            glob.c.execute(f"INSERT OR IGNORE INTO konfa_{self._chat_id}(id) VALUES(?)", (self._user_id,))
            glob.db.commit()

    def add_exp(self, exp):
        q = f"UPDATE konfa_{self._chat_id} SET experience=experience + ? WHERE id=?"
        glob.c.execute(q, (exp, self._user_id))
        glob.db.commit()