from commands.interfaces import IAdminCommand
from objects import glob
from constants.roles import Roles

class Op(IAdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)

    def execute(self):
        q = f"UPDATE users SET role = {Roles.ADMIN} WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был добавлен как админ.")


class Deop(IAdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)

    def execute(self):
        q = f"UPDATE users SET role = {Roles.USER} WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} был удалён из админов.")


class Restrict(IAdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)

    def execute(self):
        q = f"UPDATE users SET role = {Roles.RESTRICTED} WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} больше не может юзать бота.")


class Unrestrict(IAdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)

    def execute(self):
        q = f"UPDATE users SET role = {Roles.USER} WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(f"Пользователь {self._user_id} теперь может юзать бота.")

