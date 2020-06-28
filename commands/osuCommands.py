import random
import logging
from commands.command import Command
from helpers import utils, banchoApi
from objects import glob
from constants import servers
import requests


class StatsPicture(Command):
    SIG_COLORS = ('black', 'red', 'orange', 'yellow', 'green',
                  'blue', 'purple', 'pink', 'hex2255ee')
    SERVERS = {
        "gatari": "http://sig.gatari.pw/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}",
        "bancho": "http://134.122.83.254:5000/sig?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}&{}"
    }

    def __init__(self, server, *username):
        super().__init__()
        self._pictureUrl = self.SERVERS.get(server)
        self._username = " ".join(username)
        self._mode = None

    def execute(self):
        pic = self._pictureUrl.format(random.choice(
            self.SIG_COLORS), self._username, self._mode, random.random())
        logging.debug(pic)
        picture = utils.upload_picture(pic, decode_content=True)
        logging.info("Uploaded picture URL: "+picture)
        return self.Message(attachment=picture)


class OsuPicture(StatsPicture):
    def __init__(self, args):
        super().__init__(*args.split())
        self._mode = 0


class TaikoPicture(StatsPicture):
    def __init__(self, args):
        super().__init__(*args.split())
        self._mode = 1


class CtbPicture(StatsPicture):
    def __init__(self, args):
        super().__init__(*args.split())
        self._mode = 2


class ManiaPicture(StatsPicture):
    def __init__(self, args):
        super().__init__(*args.split())
        self._mode = 3


class MatchmakingStats(Command):
    API = "https://osumatchmaking.c7x.dev/users/"

    def __init__(self, username):
        super().__init__()
        self._username = username

    def _make_request(self):
        session = requests.Session()
        r = session.get(self.API + self._username)
        if r.status_code != 200:
            return None
        return r.json()

    def execute(self):
        js = self._make_request()
        username = js.get("osuName")
        country = js.get("countryCode")
        rank = js.get("rank")
        rating = round(js.get("currentVisualRating"))
        wins = js.get("wins")
        losses = js.get("losses")
        winrate = round((wins / (wins + losses)) * 100, 2)
        winstreak = js.get("currentWinstreak")
        response = f"{country} | {username} #{rank}\nRating: {rating}\nW/L: {wins}/{losses} | WR: {winrate}%\nWinstreak: {winstreak}"
        return self.Message(response)
