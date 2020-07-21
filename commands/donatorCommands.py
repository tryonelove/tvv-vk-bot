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

