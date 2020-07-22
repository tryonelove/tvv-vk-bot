from commands.interfaces import ICommand
import datetime
from objects import glob
from constants.roles import Roles
from helpers.utils import Utils 
import logging


class GetRole(ICommand):
    """
    Get user role command

    :param user_id: target_user_id
    :param from_id: from_id (in case user_id is empty)
    """

    def __init__(self, user_id, from_id, **kwargs):
        self._user_id = user_id
        self._from_id = from_id

    def execute(self):
        if not self._user_id:
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

