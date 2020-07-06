import random
import logging
from commands.interfaces import IOsuCommand
from helpers import banchoApi, gatariApi, scoreFormatter
from helpers.utils import Utils
from objects import glob
from constants import servers
import requests
from config import OSU_API_KEY


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

    def __init__(self, server, username, **kwargs):
        super().__init__(**kwargs)
        self._pictureUrl = self.SERVERS.get(server)
        self._username = " ".join(username)
        self._mode = None

    def execute(self):
        pic = self._pictureUrl.format(random.choice(
            self.SIG_COLORS), self._username, self._mode, random.random())
        logging.debug(pic)
        picture = Utils.upload_picture(pic, decode_content=True)
        logging.info("Uploaded picture URL: "+picture)
        return self.Message(attachment=picture)


class OsuPicture(StatsPicture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 0


class TaikoPicture(StatsPicture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 1


class CtbPicture(StatsPicture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 2


class ManiaPicture(StatsPicture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 3


class MatchmakingStats(IOsuCommand):
    """
    Get osu! matchchmaking stats
    """

    def __init__(self, username, **kwargs):
        super().__init__()
        self._username = username
        self.API = "https://osumatchmaking.c7x.dev/users/"

    def execute(self):
        r = requests.get(self.API + self._username)
        if r.status_code != 200:
            raise NotImplementedError()
        js = r.json()
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


class OsuSet(IOsuCommand):
    """
    Connect user_id to osu! account
    """
    def __init__(self, server, username, user_id, **kwargs):
        super().__init__()
        self._server = server
        self._username = username
        self._user_id = user_id

    def execute(self):
        glob.c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (self._user_id,))
        glob.c.execute("UPDATE users SET server=?, username=? WHERE id=?",(self._server, self._username, self._user_id))
        glob.db.commit()
        return self.Message(f"Аккаунт {self._server} {self._username} был успешно привязан к вашему айди.")


class TopScoreCommand(IOsuCommand):
    """
    Interface for top score command
    """

    def __init__(self, server, username, limit, **kwargs):
        super().__init__()
        self._server = server
        self._username = username
        self._limit = limit or 1
        self._api = BanchoTopScore if server == "bancho" else GatariTopScore

    def execute(self):
        result = self._api(self._username, self._limit).get()
        return self.Message(*result)


class BanchoTopScore:
    def __init__(self, username, limit):
        super().__init__()
        self._username = username
        self._limit = int(limit)
        self.api = banchoApi.BanchoApi(OSU_API_KEY)

    def get(self):
        result = self.api.get_user_best(
            u=self._username, limit=self._limit)[self._limit-1]
        beatmap_id = result['beatmap_id']
        combo = result['maxcombo']
        count50 = result['count50']
        count100 = result['count100']
        count300 = result['count300']
        misses = result['countmiss']
        m = result['enabled_mods']
        ranking = result['rank']
        accuracy = Utils.calculate_accuracy(
            *map(int, (misses, count50, count100, count300)))
        beatmap = Utils(api=self.api).get_cached_beatmap(beatmap_id)
        max_combo = beatmap["max_combo"]
        title = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]"
        username = self.api.get_user(u=self._username)[0]["username"]
        score_message = scoreFormatter.Formatter(
            username=username,
            title=title,
            m=m,
            accuracy=accuracy,
            combo=combo,
            max_combo=max_combo,
            misses=misses,
            pp=0,
            pp_if_fc=0,
            beatmap_id=beatmap_id
        )
        score_background = beatmap["background_url"]
        return score_message, score_background

class GatariTopScore:
    def __init__(self, server, username, limit, **kwargs):
        super().__init__()
        self._username = username
        self._limit = limit
        self.api = gatariApi.GatariApi()

    def get(self):
        return 1
