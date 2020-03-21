import random
from .command import Command
from . import utils
from objects import glob
import logging
from helpers import checks


class StatsPicture(Command):
    SIG_COLORS = ('black', 'red', 'orange', 'yellow', 'green',
                  'blue', 'purple', 'pink', 'hex2255ee')
    SERVERS = {
        "gatari": "http://sig.gatari.pw/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}",
        "bancho": "http://134.209.249.44:5000/sig?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}&{}"
    }

    def __init__(self, server, *username):
        super().__init__()
        self._pictureUrl = self.SERVERS.get(server)
        self._username = " ".join(username)
        self._mode = None

    def execute(self):
        pic = self._pictureUrl.format(random.choice(
            self.SIG_COLORS), self._username, self._mode, random.random())
        logging.info(pic)
        picture = utils.upload_picture(pic, decode_content=True)
        logging.info(picture)
        return self.message(attachments=picture)


class OsuPicture(StatsPicture):
    def __init__(self, *args):
        super().__init__(*args)
        self._mode = 0


class TaikoPicture(StatsPicture):
    def __init__(self, *args):
        super().__init__(*args)
        self._mode = 1


class CtbPicture(StatsPicture):
    def __init__(self, *args):
        super().__init__(*args)
        self._mode = 2


class ManiaPicture(StatsPicture):
    def __init__(self, *args):
        super().__init__(*args)
        self._mode = 3
