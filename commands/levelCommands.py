from commands.interfaces import ILevelCommand
from objects import glob
from helpers.utils import Utils
from constants.roles import Roles
from helpers import exceptions
import config

class GetLevel(ILevelCommand):
    """
    Get user level and experience
    """
    KEYS = ["level", "lvl", "лвл"]

    def __init__(self, chat_id, user_id):
        super().__init__(chat_id=chat_id, user_id=user_id)

    def _get_level(self):
        q = f"SELECT * FROM konfa_{self._chat_id} WHERE id=?"
        executed = glob.c.execute(q, (self._user_id,)).fetchone()
        if executed:
            _, experience, lvl_start = executed
            exp_required = (lvl_start+1)**3
            user_info = glob.vk.users.get(
                user_id=int(self._user_id), name_case="nom")[0]
            full_name = f"{user_info['first_name']} {user_info['last_name']}"
            message = f"{full_name}, ваша статистика:\nУровень: {lvl_start}\nОпыт: {experience}/{exp_required}XP"
            return message

    def execute(self):
        message = self._get_level()
        return self.Message(message)


class GetLeaderboard(ILevelCommand):
    """
    Get chat experience leaderboard
    """
    KEYS = ["лидерборд", "leaderboard"]

    def __init__(self, chat_id, **kwargs):
        super().__init__(chat_id=chat_id)

    def _get_leaderboard(self):
        text = "Топ 10 конфы:\n\n"
        leaderboard = glob.c.execute("""
                SELECT id, experience, level FROM konfa_{0} 
                ORDER BY experience DESC LIMIT 10 
            """.format(self._chat_id)).fetchall()
        user_ids = [user[0] for user in leaderboard]
        users = glob.vk.users.get(user_ids=user_ids)
        for user_index, _ in enumerate(leaderboard):
            rank = user_index+1
            full_name = f"{users[user_index]['first_name']} {users[user_index]['last_name']}"
            if Utils.has_role(users[user_index]["id"], Roles.DONATOR):
                full_name += "⭐"
            exp = leaderboard[user_index][1]
            level = leaderboard[user_index][2]
            text += f'#{rank} {full_name} {exp}XP ({level}lvl)\n'
        return text

    def execute(self):
        message = self._get_leaderboard()
        return self.Message(message)


class LevelToggler(ILevelCommand):
    def __init__(self, user_id, chat_id, **kwargs):
        super().__init__()
        self._user_id = user_id
        self._chat_id = chat_id

    def _is_chat_admin(self):
        admins = []
        users = glob.vk.messages.getConversationMembers(peer_id=self._chat_id)
        if not users:
            raise exceptions.AccesDeniesError
        for user in users["items"]:
            if user.get("is_admin", False):
                admins.append(user["member_id"])
        return self._user_id in admins or self._user_id == config.CREATOR_ID


class DisableLevels(LevelToggler):
    """
    Disable levels command
    """
    KEYS = ["disable_levels"]

    def __init__(self, user_id, chat_id, **kwargs):
        super().__init__(user_id, chat_id)

    def execute(self):
        if self._is_chat_admin():
            glob.c.execute(
                "INSERT OR IGNORE INTO disabled_level(chat_id) VALUES (?)", (self._chat_id,))
            glob.db.commit()
            return self.Message("Экспа была выключена в конфе.")


class EnableLevels(LevelToggler):
    """
    Enable levels command
    """
    KEYS = ["enable_levels"]

    def __init__(self, user_id, chat_id, **kwargs):
        super().__init__(user_id, chat_id)

    def execute(self):
        if self._is_chat_admin():
            glob.c.execute(
                "DELETE FROM disabled_level WHERE chat_id=?", (self._chat_id,))
            glob.db.commit()
            return self.Message("Экспа была включена в конфе.")


class WipeLevels(LevelToggler):
    KEYS = ["wipelevels"]

    def __init__(self, user_id, chat_id, **kwargs):
        super().__init__(user_id, chat_id)

    def execute(self):
        if self._is_chat_admin():
            glob.c.execute(f"DELETE FROM konfa_{self._chat_id}")
            glob.db.commit()
            return self.Message("Лидерборд конфы был очищен. SPAM !анал CHAT")