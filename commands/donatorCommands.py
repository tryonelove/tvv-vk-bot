from commands.interfaces import IDonatorManager
import datetime
from objects import glob
from constants.roles import Roles
from helpers.utils import Utils 
import logging


class GetRole(IDonatorManager):
    """
    Get user role command

    :param user_id: target_user_id
    :param from_id: from_id (in case user_id is empty)
    """

    def __init__(self, user_id, from_id, **kwargs):
        super().__init__(user_id)
        self._from_id = from_id

    def execute(self):
        if self._user_id is None:
            self._user_id = self._from_id
        logging.info("Getting user role.")
        message = "Роль: "
        if Utils.has_role(self._user_id, Roles.ADMIN):
            role = "админ"
        elif Utils.has_role(self._user_id, Roles.DONATOR):
            expires, role = Utils.get_donator_expire_date(self._user_id)
            expires = datetime.datetime.fromtimestamp(expires)
            role += f"\nВы будете донатером до {expires}"
        else:
            role = "юзер"
        message += role
        return self.Message(message)


class AddDonator(IDonatorManager):
    """
    Add donator command
    """
    RESPONSE = "Пользователь {} получил роль донатера."

    def __init__(self, message, *args, **kwargs):
        super().__init__(message)
        self._donation_sum = self._parse_donation_sum()
        self._role_name = self._parse_role_name() if len(self._args) > 2 else None

    def _parse_donation_sum(self):
        return int(self._args[1])

    def _parse_role_name(self):
        return " ".join(self._args[2:])

    def _add_new_donator(self):
        duration = self._donation_sum // 25
        q = f"INSERT INTO donators VALUES(?, (SELECT strftime('%s','now', '+{duration} month')), ?)"
        glob.c.execute(q, (self._user_id, self._role_name))
        glob.c.execute("UPDATE users SET role = ?", (Roles.DONATOR.value,))
        glob.db.commit()

    def _increase_duration(self):
        duration = self._donation_sum // 25
        q = f"SELECT strftime('%s', (SELECT expires FROM donators WHERE id={self._user_id}), '+{duration} month')"
        glob.c.execute(q)
        glob.db.commit()

    def execute(self):
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

    def __init__(self, user_id):
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
