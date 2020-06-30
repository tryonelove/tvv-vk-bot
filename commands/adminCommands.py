from commands.interfaces import IAdminCommand
from objects import glob


class Op(IAdminCommand):
    def __init__(self, user_id):
        super().__init__(user_id)

    def execute(self):
        q = "UPDATE users SET role = 1 WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был добавлен как админ.")


class Deop(IAdminCommand):
    def __init__(self, user_id):
        super().__init__(user_id)

    def execute(self):
        q = "UPDATE users SET role = 1 WHERE id = ?"
        glob.c.execute(q, (self._user_id))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был удалён из админов.")
