import requests
import json
from constants import exceptions

class BanchoApi:
    def __init__(self, key):
        self.key = key
        self.API = "https://osu.ppy.sh/api/"
        self.session = requests.Session()

    def get_beatmaps(
        self, since=None, s=None, b=None,
        u=None, type=None, m=None, a=0, h=None, limit=500):
        """
        Retrieve general beatmap information.
        """
        data = self.__make_request('get_beatmaps', locals())
        return data
    
    def get_user(self, u, m=0, type=None, event_days=1):
        """
        Retrieve general user information.
        """
        data = self.__make_request('get_user', locals())
        return data

    def get_scores(self, b, u=None, m=0, mods=None, type=None, limit=50):
        data = self.__make_request('get_scores', locals())
        return data

    def get_user_best(self, u, m=0, limit=10, type=None):
        data = self.__make_request('get_user_best', locals())
        return data

    def get_user_recent(self, u, m=0, limit=10, type=None):
        data = self.__make_request('get_user_recent', locals())
        return data

    def get_match(self, mp):
        data = self.__make_request('get_match', locals())
        return data
    
    def get_replay(self, m, b, u, mods=None):
        data = self.__make_request('get_replay', locals())
        return data

    def __make_request(self, endpoint, params):
        del params['self']
        params["k"] = self.key
        r = self.session.get(
            self.API + endpoint, params = params)
        if r.status_code == 200:
            return r.json()
        raise exceptions.ApiError("Ошибка при запросе, возможно, что серваки сдохли")


class GatariApi:
    def __init__(self):
        self.OLD_API = "https://osu.gatari.pw/api/v1/"
        self.NEW_API = "https://api.gatari.pw/"
        self.session = requests.Session()

    def __make_request(self, API_VERSION ,endpoint, params):
        r = self.session.get(
            API_VERSION + endpoint, params = params, timeout=3.0)
        if r.status_code == 200:
            js = r.json()
            if js:
                return js
        raise exceptions.ApiError       

    def get_user(self, username):
        data = self.__make_request(self.NEW_API, "users/get", params = {
            "id" : username
        })
        return data

    def get_user_best(self, user_id, limit = 1):
        data = self.__make_request(self.NEW_API, "user/scores/best", params = { 
            'id' : user_id,
            'l': limit
        })
        return data

    def get_user_recent(self, user_id, limit = 1, show_failed = False):
        data = self.__make_request(self.NEW_API, "user/scores/recent", params = { 
            'id' : user_id,
            'l': limit,
            'f': int(show_failed)
        })
        return data

    def get_user_score(self, user_id, beatmap_id, mode = 0):
        data = self.__make_request(self.NEW_API, "beatmap/user/score", params = {
            "u" : user_id,
            "b" : beatmap_id,
            "mode" : mode
        })
        return data
    