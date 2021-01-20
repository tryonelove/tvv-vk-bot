from objects import glob
from vk_api.utils import get_random_id

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
        self.update_data()
        k = self.calc_exp(message)
        self.add_exp(k)
        self.level_up()
        glob.db.commit()

    def level_up(self):
        q = f"SELECT experience, level FROM users_experience WHERE user_id=? AND chat_id=?"
        q_upd = f"UPDATE users_experience SET level=? WHERE user_id=? AND chat_id=?"
        experience, lvl_start = glob.c.execute(q, (self._user_id, self._chat_id)).fetchone()
        if experience is None or lvl_start is None:
            # temp fix
            glob.c.execute(f"UPDATE users_experience SET experience=0, level=1 WHERE user_id=? AND chat_id=?", (self._user_id, self._chat_id))
            experience = 0
            lvl_start = 1

        lvl_end = int(experience ** (1/3))
        if lvl_start < lvl_end:
            data = glob.vk.users.get(user_id=int(self._user_id), name_case = "nom")[0]
            if lvl_end>=7:
                username =  f"{data['first_name']} {data['last_name']}"
                glob.vk.messages.send(
                    peer_id = self._chat_id, 
                    message=f"{username} апнул {lvl_end} лвл!",
                    random_id = get_random_id())
            glob.c.execute(q_upd, (lvl_end, self._user_id, self._chat_id))

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
        q = f"SELECT * FROM users_experience WHERE user_id=? AND chat_id=?"
        glob.c.execute(q, (self._user_id, self._chat_id))
        if not glob.c.fetchone():
            glob.c.execute(f"INSERT OR IGNORE INTO users_experience(user_id, chat_id) VALUES(?, ?)", (self._user_id, self._chat_id))

    def add_exp(self, exp):
        q = f"UPDATE users_experience SET experience = experience + ? WHERE user_id=? AND chat_id=?"
        glob.c.execute(q, (exp, self._user_id, self._chat_id))