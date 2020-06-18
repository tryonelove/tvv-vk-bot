from commands.command import Command
from objects import glob

class AdminManager(Command):
    def __init__(self, user_id):
        super().__init__()
        self._user_id = user_id

class Op(AdminManager):
    def __init__(self, args):
        super().__init__(args)

    def execute(self):
        q = "UPDATE users SET admin = 1 WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был добавлен как админ.")
        

class Deop(AdminManager):
    def __init__(self, args):
        super().__init__(args)

    def execute(self):
        q = "UPDATE users SET admin = 0 WHERE id = ?"
        glob.c.execute(q, (self._user_id))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был удалён из админов.")