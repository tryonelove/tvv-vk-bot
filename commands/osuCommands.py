import random
import logging
from commands.interfaces import IOsuCommand
from helpers import banchoApi, gatariApi, scoreFormatter, exceptions, ppCalculator
from helpers.utils import Utils
from objects import glob
from constants import servers
from constants import osuConstants
import requests
from config import OSU_MATCHMAKING_KEY


class StatsPicture(IOsuCommand):
    """
    osu! picture generator
    """
    SIG_COLORS = ('black', 'red', 'orange', 'yellow', 'green',
                  'blue', 'purple', 'pink', '2255ee')
    SERVERS = {
        "gatari": "http://sig.gatari.pw/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}",
        "bancho": "http://134.122.83.254:5000/sig?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}&{}"
    }

    def __init__(self, server, username, **kwargs):
        super().__init__()
        self._server = server
        self._username = username
        self._mode = None

    def execute(self):
        if self._server in osuConstants.server_acronyms["bancho"]:
            server = "bancho"
        else:
            server = "gatari"
        pictureUrl = self.SERVERS.get(server)
        pic = pictureUrl.format(random.choice(
            self.SIG_COLORS), self._username, self._mode, random.random())
        logging.debug(pic)
        picture = Utils.upload_picture(pic, decode_content=True)
        logging.info("Uploaded picture URL: "+picture)
        return self.Message(attachment=picture)


class OsuPicture(StatsPicture):
    KEYS = ["osu", "осу"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 0


class TaikoPicture(StatsPicture):
    KEYS = ["taiko", "тайко"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 1


class CtbPicture(StatsPicture):
    KEYS = ["ctb", "ктб"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 2


class ManiaPicture(StatsPicture):
    KEYS = ["mania", "мания"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = 3


class MatchmakingStats(IOsuCommand):
    """
    Get osu! matchchmaking stats
    """
    KEYS = ["mm"]

    def __init__(self, username, **kwargs):
        super().__init__()
        self._username = username
        self.API = "https://osumatchmaking.c7x.dev/api/users/"
        self._ruleset = "1v1"

    def execute(self):
        r = requests.get(self.API + self._username,
                         params={"key": OSU_MATCHMAKING_KEY, "rulesets": f'["{self._ruleset}"]'})
        if r.status_code != 200:
            raise exceptions.ApiRequestError
        js = r.json()
        username = js.get("osuName")
        country = js.get("countryCode")
        stats = js.get("stats")[self._ruleset]
        rank = stats.get("rank")
        rating = round(stats.get("currentVisualRating"))
        wins = stats.get("wins")
        losses = stats.get("losses")
        try:
            winrate = round((wins / (wins + losses)) * 100, 2)
        except:
            winrate = 0
        winstreak = stats.get("currentWinstreak")
        response = f"{self._ruleset}\n{country} | {username} #{rank}\nRating: {rating}\nW/L: {wins}/{losses} | WR: {winrate}%\nWinstreak: {winstreak}"
        return self.Message(response)


class MatchmakingStatsDuo(MatchmakingStats):
    """
    Get osu! matchchmaking stats
    """
    KEYS = ["mm2"]

    def __init__(self, username, **kwargs):
        super().__init__(username)
        self._ruleset = "2v2"


class OsuSet(IOsuCommand):
    """
    Connect user_id to osu! account
    """
    KEYS = ["osuset"]

    def __init__(self, server, username, user_id, **kwargs):
        super().__init__()
        self._server = "bancho" if server in osuConstants.server_acronyms["bancho"] else "gatari"
        self._username = username
        self._user_id = user_id
        self._api = banchoApi.BanchoApi(
        ) if server in osuConstants.server_acronyms["bancho"] else gatariApi.GatariApi()

    def _get_real_username(self):
        user = self._api.get_user(u=self._username)
        if self._server in osuConstants.server_acronyms["bancho"]:
            if not user:
                raise exceptions.UserNotFoundError
            username = user[0]["username"]
        else:
            if not user["users"]:
                raise exceptions.UserNotFoundError
            username = user["users"][0]["username"]
        return username

    def execute(self):
        self._username = self._get_real_username()
        glob.c.execute(
            "INSERT OR IGNORE INTO osu(id) VALUES(?)", (self._user_id,))
        if self._server == "bancho":
            glob.c.execute("UPDATE osu SET main_server=?, bancho_username=? WHERE id=?",
                           (self._server, self._username, self._user_id))
        elif self._server == "gatari":
            glob.c.execute("UPDATE osu SET main_server=?, gatari_username=? WHERE id=?",
                           (self._server, self._username, self._user_id))
        glob.db.commit()
        return self.Message(f"Аккаунт {self._server} {self._username} был успешно привязан к вашему айди.")


class BanchoScore:
    def __init__(self, username, api_response):
        self.username = username
        self.api_response = api_response

    def get_response(self):
        params = {}
        params["username"] = self.username
        params["beatmap_id"] = self.api_response['beatmap_id']
        params["combo"] = self.api_response['maxcombo']
        params["count50"] = self.api_response['count50']
        params["count100"] = self.api_response['count100']
        params["count300"] = self.api_response['count300']
        params["misses"] = self.api_response['countmiss']
        params["m"] = self.api_response['enabled_mods']
        params["ranking"] = self.api_response['rank']
        params["accuracy"] = Utils.calculate_accuracy_std(
            *map(int, (params["misses"], params["count50"], params["count100"], params["count300"])))
        beatmap = Utils().get_cached_beatmap(params["beatmap_id"])
        params["max_combo"] = beatmap["max_combo"]
        params["title"] = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]"
        # Calculate pp
        calculator = ppCalculator.PpCalculator(**params)
        calculator.parse_map()
        params["real_pp"] = calculator.get_real_pp()
        params["pp_if_fc"] = calculator.get_if_fc_pp()
        score_message = scoreFormatter.Formatter(**params)
        score_background = beatmap["background_url"]
        return score_message, score_background


class GatariScore:
    def __init__(self, username, api_response):
        self.username = username
        self.api_response = api_response

    def top(self):
        params = {}
        params["username"] = self.username
        params["beatmap_id"] = self.api_response["beatmap"]["beatmap_id"]
        params["combo"] = self.api_response['max_combo']
        params["misses"] = self.api_response['count_miss']
        params["m"] = self.api_response['mods']
        params["ranking"] = self.api_response['ranking']
        params["accuracy"] = self.api_response["accuracy"]
        params["count50"] = self.api_response["count_50"]
        params["count100"] = self.api_response["count_100"]
        params["count300"] = self.api_response["count_300"]
        beatmap = Utils().get_cached_beatmap(params["beatmap_id"])
        params["max_combo"] = self.api_response["beatmap"]["fc"]
        params["title"] = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]"
        # Calculate pp
        calculator = ppCalculator.PpCalculator(**params)
        calculator.parse_map()
        params["real_pp"] = calculator.get_real_pp()
        params["pp_if_fc"] = calculator.get_if_fc_pp()
        score_message = scoreFormatter.Formatter(**params)
        score_background = beatmap["background_url"]
        return score_message, score_background

    def recent(self):
        return self.top()

    def compare(self):
        params = {}
        params["username"] = self.username
        params["beatmap_id"] = self.api_response["beatmap"]["beatmap_id"]
        params["combo"] = self.api_response['max_combo']
        params["misses"] = self.api_response['count_miss']
        params["m"] = self.api_response['mods']
        params["ranking"] = self.api_response['ranking']
        params["accuracy"] = self.api_response["accuracy"]
        params["count50"] = self.api_response["count_50"]
        params["count100"] = self.api_response["count_100"]
        params["count300"] = self.api_response["count_300"]
        beatmap = Utils().get_cached_beatmap(params["beatmap_id"])
        params["max_combo"] = beatmap["max_combo"]
        params["title"] = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]"
        # Calculate pp
        calculator = ppCalculator.PpCalculator(**params)
        calculator.parse_map()
        params["real_pp"] = calculator.get_real_pp()
        params["pp_if_fc"] = calculator.get_if_fc_pp()
        score_message = scoreFormatter.Formatter(**params)
        score_background = beatmap["background_url"]
        return score_message, score_background


class TopScoreCommand(IOsuCommand):
    """
    Manager for top score command
    """
    KEYS = ["top"]

    def __init__(self, server, username, limit, **kwargs):
        super().__init__()
        self._server = server
        self._username = username
        self._limit = limit or 1
        self._mode = 0
        self._api = BanchoTopScore if server in osuConstants.server_acronyms[
            "bancho"] else GatariTopScore

    def execute(self):
        result = self._api(self._username, self._limit, self._mode).get()
        return self.Message(*result)


class OsuTopScore(TopScoreCommand):
    def __init__(self, server, username, limit):
        super().__init__(server, username, limit)
        self._mode = 0


class TaikoTopScore(TopScoreCommand):
    def __init__(self, server, username, limit):
        super().__init__(server, username, limit)
        self._mode = 1


class CtbTopScore(TopScoreCommand):
    def __init__(self, server, username, limit):
        super().__init__(server, username, limit)
        self._mode = 2


class ManuaTopScore(TopScoreCommand):
    def __init__(self, server, username, limit):
        super().__init__(server, username, limit)
        self._mode = 3


class BanchoTopScore:
    """
    Get bancho top score
    """

    def __init__(self, username, limit, mode):
        self._username = username
        self._limit = int(limit)
        self._mode = mode
        self._api = banchoApi.BanchoApi()

    def get(self):
        api_response = self._api.get_user_best(
            u=self._username, limit=self._limit, m=self._mode)
        if not api_response:
            raise exceptions.ScoreNotFoundError
        return BanchoScore(self._username, api_response[self._limit-1]).get_response()


class GatariTopScore:
    def __init__(self, username, limit, mode):
        self._username = username
        self._limit = int(limit)
        self._api = gatariApi.GatariApi()

    def get(self):
        user = self._api.get_user(self._username)
        if not user:
            raise exceptions.ApiRequestError
        if not user["users"]:
            raise exceptions.UserNotFoundError
        user_id = user["users"][0]["id"]
        best_scores = self._api.get_user_best(user_id, self._limit)
        score = best_scores["scores"][self._limit-1]
        return GatariScore(self._username, score).top()


class RecentScoreCommandOsu(IOsuCommand):
    """
    Manager for recent score command
    """

    KEYS = ["last", "ласт"]

    def __init__(self, server, username, limit, **kwargs):
        super().__init__()
        self._server = server
        self._username = username
        self._limit = limit or 1
        self._mode = 0
        self._api = BanchoRecentScore if server in osuConstants.server_acronyms[
            "bancho"] else GatariRecentScore

    def execute(self):
        result = self._api(self._username, self._limit, self._mode).get()
        return self.Message(*result)


class BanchoRecentScore:
    """
    Get recent bancho score
    """

    def __init__(self, username, limit, mode):
        self._username = username
        self._limit = int(limit)
        self._mode = mode
        self._api = banchoApi.BanchoApi()

    def get(self):
        api_response = self._api.get_user_recent(
            u=self._username, limit=self._limit, m=self._mode)
        if not api_response:
            raise exceptions.ScoreNotFoundError
        return BanchoScore(self._username, api_response[self._limit-1]).get_response()


class GatariRecentScore:
    """
    Get recent gatari score
    """

    def __init__(self, username, limit, *args, **kwargs):
        self._username = username
        self._limit = int(limit)
        self._api = gatariApi.GatariApi()

    def get(self):
        user = self._api.get_user(self._username)
        if not user:
            raise exceptions.ApiRequestError
        if not user["users"]:
            raise exceptions.UserNotFoundError
        user_id = user["users"][0]["id"]
        best_scores = self._api.get_user_recent(
            user_id, self._limit, show_failed=True)
        score = best_scores["scores"][self._limit-1]
        return GatariScore(self._username, score).recent()


class Compare(IOsuCommand):
    """
    Compare scores
    """
    KEYS = ["c", "с", "compare"]

    def __init__(self, server, username, beatmap_id, **kwargs):
        super().__init__()
        self._username = username
        self._beatmap_id = beatmap_id
        self._limit = 1
        self._api = BanchoCompare if server in osuConstants.server_acronyms[
            "bancho"] else GatariCompare

    def execute(self):
        result = self._api(self._username, self._beatmap_id).get()
        return self.Message(*result)


class GatariCompare:
    def __init__(self, username, beatmap_id, **kwargs):
        self._username = username
        self._beatmap_id = beatmap_id
        self._limit = 1
        self._api = gatariApi.GatariApi()

    def get(self):
        user = self._api.get_user(self._username)
        if not user:
            raise exceptions.ApiRequestError
        if not user["users"]:
            raise exceptions.UserNotFoundError
        user_id = user["users"][0]["id"]
        scores = self._api.get_scores(
            user_id, self._beatmap_id)
        if scores.get("error"):
            raise exceptions.ScoreNotFoundError
        score = scores["score"]
        # API fix
        score["ranking"] = score["rank"]
        score["beatmap"] = {}
        score["beatmap"]["beatmap_id"] = self._beatmap_id
        return GatariScore(self._username, score).compare()


class BanchoCompare:
    def __init__(self, username, beatmap_id, **kwargs):
        self._username = username
        self._beatmap_id = beatmap_id
        self._limit = 1
        self._api = banchoApi.BanchoApi()

    def get(self):
        api_response = self._api.get_scores(
            b=self._beatmap_id, u=self._username, limit=self._limit)
        if not api_response:
            raise exceptions.ScoreNotFoundError
        api_response[self._limit-1]["beatmap_id"] = self._beatmap_id
        return BanchoScore(self._username, api_response[self._limit-1]).get_response()
