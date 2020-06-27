import requests
import json

class BanchoApi:
    """
    Official documentation: 
    https://github.com/ppy/osu-api/wiki
    """
    API = "https://osu.ppy.sh/api/"
    def __init__(self, key):
        self.session = requests.Session()
        self.key = key

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