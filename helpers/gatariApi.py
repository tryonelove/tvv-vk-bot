import requests
from helpers import exceptions

class GatariApi:
    def __init__(self):
        self.OLD_API = "https://osu.gatari.pw/api/v1/"
        self.NEW_API = "https://api.gatari.pw/"
        self.session = requests.Session()

    def __make_request(self, API_VERSION ,endpoint, params):
        r = self.session.get(
            API_VERSION + endpoint, params = params, timeout=3.0)
        if r.status_code != 200:
            return {}      
        return r.json()

    def get_user(self, u):
        data = self.__make_request(self.NEW_API, "users/get", params = {
            "id" : u
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