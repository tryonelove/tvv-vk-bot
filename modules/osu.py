import random
from .command import Command
from . import utils

class OsuStatsPicture(Command):
    sig_colors = ['black', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'hex2255ee']
    def __init__(self, upload, server, username, mode):
        Command.__init__(self)
        self._server = server
        self._username = username
        self._mode = mode
        self._upload = upload

    def setServerUrl(self):
        if self._server == "gatari":
            self._server = "http://sig.gatari.pw/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}"
        elif self._server == "bancho":
            self._server = 'http://134.209.249.44:5000/sig?{}&colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}'

    def execute(self):
        self.setServerUrl()
        picture = utils.uploadPicture(self._upload, self._server, decode_content=True)
        if self._server == "gatari":
            return self.message(attachments=picture.format(random.randint(1, 1000), random.choice(self.sig_colors), self._username, self._mode))
        return self.message(attachments=picture.format(random.choice(self.sig_colors), self._username, self._mode))