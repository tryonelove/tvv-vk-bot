from commands.interfaces import IAdminCommand, IDonatorManager
from objects import glob
from constants.roles import Roles
import logging
from helpers.utils import Utils 


class AdminCommand(IAdminCommand):
    RESPONSE = ""

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role: Roles = None

    def execute(self):
        q = f"UPDATE users SET role = {self.role} WHERE id = ?"
        glob.c.execute(q, (self._user_id,))
        glob.db.commit()
        return self.Message(self.RESPONSE)


class Op(AdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role = Roles.ADMIN.value
        self.RESPONSE = f"Пользователь {self._user_id} был добавлен как админ."


class Deop(AdminCommand):
    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role = Roles.USER.value
        self.RESPONSE = f"Пользователь {self._user_id} был удалён из админов."


class Restrict(AdminCommand):
    """
    Restrict bot usage for users.

    :param user_id: target user_id
    """

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role = Roles.RESTRICTED.value
        self.RESPONSE = f"Пользователь {self._user_id} больше не может юзать бота."


class Unrestrict(AdminCommand):
    """
    Unrestrict bot usage for users.

    :param user_id: target user_id
    """

    def __init__(self, user_id, *args):
        super().__init__(user_id)
        self.role = Roles.USER.value
        self.RESPONSE = f"Пользователь {self._user_id} теперь может юзать бота."


class AddDonator(IDonatorManager):
    """
    Add donator command
    """
    RESPONSE = "Пользователь {} получил роль донатера."

    def __init__(self, message, *args, **kwargs):
        super().__init__(message)
        self._donation_sum = 25
        self._role_name = None

    def _parse_donation_sum(self):
        return int(self._args[1])

    def _parse_role_name(self):
        return " ".join(self._args[2:])

    def _add_new_donator(self):
        
        duration = self._donation_sum // 25
        q = f"INSERT INTO donators VALUES(?, (SELECT strftime('%s','now', '+{duration} month')), ?)"
        glob.c.execute(q, (self._user_id, self._role_name))
        glob.c.execute("UPDATE users SET role = ? WHERE id=?", (Roles.DONATOR.value, self._user_id))
        glob.db.commit()

    def _increase_duration(self):
        duration = self._donation_sum // 25
        q = f"SELECT strftime('%s', (SELECT expires FROM donators WHERE id={self._user_id}), '+{duration} month')"
        glob.c.execute(q)
        glob.db.commit()

    def execute(self):
        self._donation_sum = self._parse_donation_sum()
        if len(self._args) > 2:
            self._role_name = self._parse_role_name()
        logging.info(f"Adding a donator: {self._user_id}.")
        if Utils.has_role(self._user_id, Roles.DONATOR):
            self._increase_duration()
        else:
            self._add_new_donator()
        return self.Message(self.RESPONSE.format(self._user_id))


class RemoveDonator(IDonatorManager):
    """
    Remove donator command

    :param user_id: target user_id
    """
    SUCCESS = "Пользователь {} был удалён из списка донатеров."
    NOT_DONATOR = "Пользователь {} не является донатером."

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(user_id)

    def _remove_completely(self):
        glob.c.execute("DELETE FROM donators WHERE id=?", (self._user_id,))
        glob.c.execute("UPDATE users SET role=1 WHERE id=?",(self._user_id,))
        glob.db.commit()

    def _decrease_duration(self):
        # TODO
        pass

    def execute(self):
        logging.info("Removing from donators.")
        if not Utils.has_role(self._user_id, Roles.DONATOR):
            return self.Message(self.NOT_DONATOR.format(self._user_id))
        self._remove_completely()
        return self.Message(self.SUCCESS.format(self._user_id))


class AddRole(IDonatorManager):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message)
        self._user_id = None
        self._role = None

    def _parse_role_name(self):
        return " ".join(self._args[1:])

    def execute(self):
        self._user_id = Utils.find_user_id(self._args[0])
        self._role = self._parse_role_name()
        logging.info(f"Editing role: {self._user_id} -> {self._role}")
        glob.c.execute("UPDATE donators SET role = ? WHERE id = ?", (self._role, self._user_id))
        glob.db.commit()
        return self.Message(f"Роль {self._user_id} была успешно изменена на {self._role}")