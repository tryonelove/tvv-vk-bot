from commands.interfaces import ICommand
from objects import glob
from math import ceil
from constants.messageTypes import MessageTypes
import helpers


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
    RESPONSE = "Страница {}"

    def __init__(self, page, *args, **kwargs):
        super().__init__()
        try:
            self._page = int(page)
        except:
            self._page = 1
        self.overall_pages = 0

    def get_default_commands(self):
        commands = list(dict.fromkeys(helpers.commandsList.commands_list))
        return commands

    def get_static_commands(self):
        k = 50  # Number of commands per page
        commands = glob.c.execute(
            "SELECT * FROM commands ORDER BY key ASC").fetchall()
        # Calculate overall amount of pages
        self.overall_pages = ceil(len(commands) / k)
        self.RESPONSE += f" из {self.overall_pages}"
        page_start = self._page*k
        commands = [str(command[0])
                    for command in commands[page_start:page_start+k]]
        return commands

    def execute(self):
        if self._page == "":
            self._page = 1
        self.RESPONSE = self.RESPONSE.format(self._page)
        if self._page == 1:
            list_of_commands = self.get_default_commands()
        else:
            list_of_commands = self.get_static_commands()
        self.RESPONSE += "\n------------------------\n"
        self.RESPONSE += "\n".join(list_of_commands)
        return self.Message(message_type=MessageTypes.PRIVATE, message=self.RESPONSE)
