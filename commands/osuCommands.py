import random
import logging
from commands.interfaces import IOsuCommand
from helpers import utils, banchoApi
from objects import glob
from constants import servers
import requests


class StatsPicture(IOsuCommand):
    """
    osu! picture generator
    """
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


class APIRequest(IOsuCommand):
    """
    Class for API requests
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.session = requests.Session()
        self.API = None
        self._username = None
    
    def _make_request(self):
        """
        Returns API json response
        """
        r = self.session.get(self.API + self._username)
        if r.status_code != 200:
            return None
        return r.json()


class MatchmakingStats(APIRequest):
    """
    Get osu! matchchmaking stats
    """
    def __init__(self, username):
        super().__init__()
        self.API = "https://osumatchmaking.c7x.dev/users/"
        self._username = username

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