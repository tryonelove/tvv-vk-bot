from commands.interfaces import ICommand
from objects import glob


class StaticCommand(ICommand):
    """
    Get a user-created command from database
    """
    def __init__(self, key):
        super().__init__()
        self._key = key

    def execute(self):
        message = glob.c.execute(
            "SELECT message, attachment FROM commands WHERE key = ?",
            (self._key,)).fetchone()
        if message:
            return self.Message(*message)