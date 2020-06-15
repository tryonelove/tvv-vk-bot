from objects import glob
from . import utils

class LevelSystem:
    def __init__(self, user_id, chat_id):
        self._user_id = user_id
        self._chat_id = chat_id

    def level_check(self, message):
        if self._user_id < 0 or self._chat_id < 2000000000:
            return
        glob.c.execute("""
            CREATE TABLE IF NOT EXISTS konfa_{} 
            (id INTEGER PRIMARY KEY, experience FLOAT, level INTEGER, 
            FOREIGN KEY(id) REFERENCES users(id)
            ON DELETE CASCADE ON UPDATE CASCADE)
        """.format(self._chat_id))
        self.update_data(self._chat_id)
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

    def update_data(self, user_id):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self._chat_id)
        glob.c.execute(q, (self._user_id,))
        if not glob.c.fetchall():
            data = glob.vk.users.get(user_ids=self._user_id)[0]
            full_name =  data["first_name"] + " " + data['last_name']
            glob.c.execute("INSERT OR IGNORE INTO users(id, name) VALUES(?, ?)", (user_id, full_name))
            glob.c.execute("INSERT OR IGNORE INTO konfa_{} VALUES(?, ?, ?)".format(self._chat_id), (user_id, 0, 1))
            glob.db.commit()

    def add_exp(self, exp):
        q = "SELECT * FROM konfa_{} WHERE id=?".format(self._chat_id)
        q_update = "UPDATE konfa_{} SET experience=? WHERE id=?".format(self._chat_id)
        glob.c.execute(q, (self._user_id,))
        old = glob.c.fetchone()[1]
        new_exp = old + exp
        glob.c.execute(q_update, (new_exp, self._user_id))
        glob.db.commit()