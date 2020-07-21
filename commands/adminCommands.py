from commands.interfaces import IAdminCommand
from objects import glob
from constants.roles import Roles


class AdminCommand(IAdminCommand):
    RESPONSE = ""

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role = None
        self.q = f"UPDATE users SET role = {self.role} WHERE id = ?"

    def execute(self):
        glob.c.execute(self.q, (self._user_id,))
        glob.db.commit()
        return self.Message(self.RESPONSE)


class Op(AdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.RESPONSE = f"Пользователь {self._user_id} был добавлен как админ."


class Deop(IAdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.RESPONSE = f"Пользователь {self._user_id} был удалён из админов."


class Restrict(IAdminCommand):
    """
    Restrict bot usage for users.

    :param user_id: target user_id
    """

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.RESPONSE = f"Пользователь {self._user_id} больше не может юзать бота."


class Unrestrict(IAdminCommand):
    """
    Unrestrict bot usage for users.

    :param user_id: target user_id
    """

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.RESPONSE = f"Пользователь {self._user_id} теперь может юзать бота."
