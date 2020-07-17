from commands.interfaces import ICommand
from objects import glob
from math import ceil
from constants.messageTypes import MessageTypes

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

class HelpCommand(ICommand):
    """
    Get a list of commands
    """
    def __init__(self, page):
        super().__init__()
        self._page = page

    def execute(self):
        k = 50 # Number of commands per page
        commands = glob.c.execute("SELECT * FROM commands ORDER BY key ASC").fetchall()
        if self._page == "":
            page = 0
        else:
            page = int(self._page) - 1
        page_num = ceil(len(commands) / k) # Calculate overall amount of pages
        message = f"Страница {page+1} из {page_num}\n------------------------\n"
        page_start = page*k 
        commands = [str(command[0]) for command in commands[page_start:page_start+k]]
        message+= "\n".join(commands)
        return self.Message(message_type=MessageTypes.PRIVATE, message=message)
