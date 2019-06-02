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
        """Retrieve general beatmap information.

        :param since: return all beatmaps ranked or loved since this date. 
        Must be a MySQL date. In UTC. defaults to None
        :param s: 
        specify a beatmapset_id to return metadata from, defaults to None
        :param b: specify a beatmap_id to return metadata from,
        defaults to None
        :param u: specify a user_id or a username to return metadata from,
        defaults to None
        :param type: specify if u is a user_id or a username, defaults to None
        :param m:  mode (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania). 
        Optional, maps of all modes are returned by default, defaults to None
        :param a: specify whether converted beatmaps are included 
        (0 = not included, 1 = included). 
        Only has an effect if m is chosen and not 0, defaults to 0
        :param h:  the beatmap hash, defaults to None
        :param limit: amount of results.
        defaults to 500
        :return: beatmap information
        """
        data = self.make_request('get_beatmaps', locals())
        return data
    
    def get_user(self, u, m=0, type=None, event_days=1):
        """Retrieve general user information.
        
        :param u: specify a user_id or a username to return metadata from
        :param m:  mode (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania), 
        defaults to 0
        :param type:  specify if u is a user_id or a username, defaults to None
        :param event_days: Max number of days between now and last event date. 
        Range of 1-31, defaults to 1
        :return: user information
        """
        data = self.make_request('get_user', locals())
        return data

    def get_scores(self, b, u=None, m=0, mods=None, type=None, limit=50):
        data = self.make_request('get_scores', locals())
        return data

    def get_user_best(self, u, m=0, limit=10, type=None):
        data = self.make_request('get_user_best', locals())
        return data

    def get_user_recent(self, u, m=0, limit=10, type=None):
        data = self.make_request('get_user_recent', locals())
        return data

    def get_match(self, mp):
        data = self.make_request('get_match', locals())
        return data
    
    def get_replay(self, m, b, u, mods=None):
        data = self.make_request('get_replay', locals())
        return data

    def make_request(self, endpoint, params):
        del params['self']
        params["k"] = self.key
        r = self.session.get(
            self.API + endpoint, params = params, timeout=1.0)
        if r.status_code == 200:
            return r.json()
        raise exceptions.ApiError("Ошибка при запросе, возможно, что серваки сдохли")
        # else:
            # raise requests.exceptions.UnrewindableBodyError


class GatariApi:
    def __init__(self):
        self.OLD_API = "https://osu.gatari.pw/api/v1/"
        self.NEW_API = "https://api.gatari.pw/"
        self.session = requests.Session()

    def make_request(self, API_VERSION ,endpoint, params):
        r = self.session.get(
            API_VERSION + endpoint, params = params, timeout=1)
        if r.status_code == 200:
            js = r.json()
            if js:
                return js
        raise exceptions.ApiError("Ошибка при запросе, возможно, что серваки сдохли")        

    def get_user(self, username):
        data = self.make_request(self.NEW_API, "users/get", params = {
            "id" : username
        })
        return data

    def get_user_best(self, user_id, limit = 1):
        data = self.make_request(self.NEW_API, "user/scores/best", params = { 
            'id' : user_id,
            'l': limit
        })
        return data

    def get_user_recent(self, user_id, limit = 1, show_failed = False):
        data = self.make_request(self.NEW_API, "user/scores/recent", params = { 
            'id' : user_id,
            'l': limit,
            'f': int(show_failed)
        })
        return data
    