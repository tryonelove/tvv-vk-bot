from objects import glob
from . import utils
import logging


class LevelSystem:
    def __init__(self, user_id, chat_id):
        self._user_id = user_id
        self._chat_id = chat_id

    def level_check(self, message):
        if self._user_id < 0 or self._chat_id < 2000000000:
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
            glob.c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (self._user_id,))
            glob.c.execute(f"INSERT OR IGNORE INTO konfa_{self._chat_id}(id) VALUES(?)", (self._user_id,))
            glob.db.commit()

    def add_exp(self, exp):
        q = f"UPDATE konfa_{self._chat_id} SET experience=experience + ? WHERE id=?"
        glob.c.execute(q, (exp, self._user_id))
        glob.db.commit()