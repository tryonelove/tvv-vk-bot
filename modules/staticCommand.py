from .command import Command
from objects import glob

class StaticCommand(Command):
    def __init__(self, key): 
        super().__init__()
        self._key = key

    def execute(self):
        message = glob.c.execute(
            "SELECT message, attachment FROM commands WHERE key = ?",
            (self._key,)).fetchone()
        if message:
            return self.Message(*message)


