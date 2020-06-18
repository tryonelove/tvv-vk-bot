from commands.command import Command
import datetime
from objects import glob
from modules import utils
import logging

class DonatorManager(Command):
    def __init__(self, args):
        super().__init__()
        self._args = args.split()
        self._user_id = int(self._args[0])


class GetRole(DonatorManager):
    def __init__(self, args):
        super().__init__(args)        

    def _get_expire_date(self):
        return glob.c.execute("SELECT expires, role_name FROM donators WHERE id=?", (self._user_id,)).fetchone()

    def execute(self):
        logging.info("Getting user role.")
        message = "Роль: "
        if utils.is_admin(self._user_id):
            role = "админ"
        elif utils.is_donator(self._user_id):
            expires, role = self._get_expire_date()
            expires = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
            role+=f"\nВы будете донатером до {expires}"
        else:
            role = "юзер"
        message+=role
        return self.Message(message)


class AddDonator(DonatorManager):
    RESPONSE = "Пользователь {} получил роль донатера."
    def __init__(self, args):
        super().__init__(args)
        self._donation_sum = self._parse_donation_sum()
        self._role_name = self._parse_role_name() if len(self._args)>2 else None

    def _parse_donation_sum(self):
        return int(self._args[1])
            
    def _parse_role_name(self):
        return " ".join(self._args[2:])
    
    def _add_new_donator(self):
        duration = self._donation_sum // 25
        now = datetime.datetime.now()
        now += datetime.timedelta(days=+31*duration)
        glob.c.execute("INSERT INTO donators VALUES(?,?,?)", (self._user_id, now.strftime("%Y-%m-%d %H:%M:%S"), self._role_name))
        glob.db.commit()

    def _add_existing_donator(self):
        duration = self._donation_sum // 25
        expires = glob.c.execute("SELECT expires FROM donators WHERE id=?", (self._user_id,)).fetchone()[0]
        date = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
        date += datetime.timedelta(days=+31*duration)
        glob.c.execute("UPDATE donators SET expires = ? WHERE id = ?", (date.strftime("%Y-%m-%d %H:%M:%S"), self._user_id))
        glob.db.commit()

    def execute(self):
        logging.info("Adding a donator.")
        if utils.is_donator(self._user_id):
            self._add_existing_donator()
        else:
            self._add_new_donator()
        return self.Message(self.RESPONSE.format(self._user_id))


class RemoveDonator(DonatorManager):
    SUCCESS = "Пользователь {} был удалён из списка донатеров."
    NOT_DONATOR = "Пользователь {} не является донатером."
    def __init__(self, args):
        super().__init__(args)

    def _remove_completely(self):
        glob.c.execute("DELETE FROM donators WHERE id=?",(self._user_id,))
        glob.db.commit()

    def _decrease_duration(self):
        # TODO
        pass

    def execute(self):
        logging.info("Removing from donators.")
        if not utils.is_donator(self._user_id):
            return self.Message(self.NOT_DONATOR.format(self._user_id))
        self._remove_completely()        
        return self.Message(self.SUCCESS.format(self._user_id))
