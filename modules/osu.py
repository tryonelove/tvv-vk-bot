import json
from objects import glob
from constants import exceptions
import requests
import json
import random
from . import utils
from constants.osuConst import *  
import re
from helpers import osuHelpers

class Osu:
    def __init__(self, key, from_id, upload):
        self.key = key
        self.from_id = from_id
        self.upload = upload
        self.session = requests.Session()
        self.OFFICIAL_API = "https://osu.ppy.sh/api"
        self.GATARI_API = "https://api.gatari.pw"
        with open("maps.json", 'r', encoding= "UTF-8") as maps:
            self.maps = json.load(maps)

    def mapsUpdate(self):
        """
        Обновление базы
        """

        with open('maps.json', 'w') as f:
            json.dump(self.maps, f, indent=4)

    def osuset(self, text):
        """Привязка аккаунта осу к вк
        
        :param text: сервер и ник, которые нужно добавить
        :raises exceptions.ArgumentError: [description]
        :return: 
        """
        data = utils.getServerUsername(text, self.from_id)
        if str(self.from_id) in glob.config["donators"] or self.from_id in glob.config["admin"]:
            if len(text)>1 and data["server"] in ('bancho', 'gatari'):
                from_id = str(self.from_id)
                glob.users[from_id]['server'] = data["server"].strip()
                glob.users[from_id]['osu_username'] = data["username"].strip()
                utils.users_update()
                return "Аккаунт {} был успешно привязан к вашему айди.".format(text)
            raise exceptions.ArgumentError("Доступные сервера: bancho, gatari")

    def addBeatmapToDB(self, beatmapData):
        """Добавляет карту в базу
        
        :param beatmapData: osu!api /get_beatmaps responsee
        """
        beatmapSet_id = beatmapData["beatmapset_id"]
        beatmap_id = beatmapData["beatmap_id"]
        beatmap = { beatmap_id : beatmapData }
        self.maps[beatmapSet_id] = beatmap
        self.mapsUpdate()

    def getBeatmapSetFromDB(self, beatmapSet_id):
        return self.maps.get(beatmapSet_id, None)

    def getBeatmapFromDB(self, beatmap_id):
        """Функция поиска карты в базе
        
        :param beatmap_id: айди карты
        :return: информация osu!api по beatmap_id, иначе None
        """

        for _, value in self.maps.items():
            if beatmap_id in value:
                return value.get(beatmap_id)
        return None

    def lemmyPicture(self, text, mode = 0):
        """
        Функция, возвращающая ссылку на пикчу с osu!lemmy

        :param: text - сервер, ник
        :param: mode - мод 
        0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania
        """
        data = utils.getServerUsername(text, self.from_id)
        if data is None:
            userData = utils.getUserFromDB(self.from_id)
            server = userData.get("server")
            username = userData.get("username")
        else:
            server = data.get("server")
            username = data.get("username")
        if mode == 0:
            return None, self.osuPicture(server, username)
        if mode == 1:
            return None, self.taikoPicture(server, username)
        if mode == 2:
            return None, self.ctbPicture(server, username)
        if mode == 3:
            return None, self.maniaPicture(server, username)

    def getOfficialLemmyLink(self, mode, username):
        url = 'https://lemmmy.pw/osusig/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}'.format(random.choice(sig_colors), username, mode)
        return url

    def getGatariLemmyLink(self, mode, username):
        url = 'http://sig.gatari.pw/sig.php?colour={}&uname={}&xpbar&xpbarhex&darktriangles&pp=1&mode={}'.format(random.choice(sig_colors), username, mode)
        return url

    def getBeatmapBG(self, beatmapSet_id):
        try:
            bgUrl = "https://assets.ppy.sh/beatmaps/{}/covers/cover.jpg".format(beatmapSet_id)
            bgPicture = utils.uploadPicture(self.upload, bgUrl)
        except:
            bgPicture = "photo-178909901_456239049"
        return bgPicture

    def osuPicture(self, server, username):
        """
        Пикча osu!lemmy (std)
        
        :param server: сервер (bancho, gatari)
        :param username: osu! server username
        :return: image link
        """
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(0, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(0, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
    
    def taikoPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(1, username)
            return None, utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(1, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
    
    def ctbPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(2, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(2, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
    
    def maniaPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(3, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(3, username)
            return utils.uploadPicture(upload = self.upload, url = image_url, decode_content = True)
    
    def getUserBest(self, userData):
        """Топ скор заданного пользователя
        
        :param data:    dict
                        {
                            "server" : "", 
                            "username" : "",
                            "limit" : 1
                        }
        :return: text, attachment
        """
        server = userData.get("server", None)
        username = userData.get("username", None)
        limit = userData.get("limit", 1)
        if server == "bancho":
            return self.getOfficialUserBest(username, limit)
        if server == "gatari":
            return self.getGatariUserBest(username, limit)

    def getUserRecent(self, userData):
        if userData is None:
            userData = utils.getUserFromDB(self.from_id)
        server = userData.get("server", None)
        username = userData.get("username", None)
        limit = userData.get("limit", 1)
        if server == "bancho":
            return self.getOfficialUserRecent(username, limit)
        if server == "gatari":
            return self.getGatariUserRecent(username, limit)

    def getOfficialUserRecent(self, username, limit):
        limit -= 1 
        r = self.session.get(self.OFFICIAL_API + '/get_user_recent', params={
            'k': self.key, 
            'u': username, 
            'limit': limit + 1
            })
        js = r.json()
        if not js:
            return "Пользователь не найден"
        beatmap_id = js[limit]['beatmap_id']
        combo =  js[limit]['maxcombo']
        count50 = js[limit]['count50']
        count100 = js[limit]['count100']
        count300 = js[limit]['count300']
        misses = js[limit]['countmiss']
        m = js[limit]['enabled_mods']
        accuracy = osuHelpers.acc_calc(int(misses),int(count50),int(count100),int(count300))
        if self.getBeatmapFromDB(beatmap_id) is None:
            r = self.session.get(self.OFFICIAL_API + '/get_beatmaps', params={'k': self.key, 'b' : beatmap_id})
            js = r.json()
            beatmapInfo = js[0]
            self.addBeatmapToDB(beatmapInfo)
        else:
            beatmapInfo = self.getBeatmapFromDB(beatmap_id)
        beatmapSet_id = beatmapInfo["beatmapset_id"]
        artist = beatmapInfo['artist']
        songTitle = beatmapInfo['title']
        version = beatmapInfo['version']
        title = "{} - {} [{}]".format(artist, songTitle, version)
        r = self.session.get(self.OFFICIAL_API + '/get_user', params={'k': self.key, 'u': username})
        js = r.json()[0]
        text = osuHelpers.scoreFormat(
            username = js["username"], 
            m = m,
            title = title, 
            combo = combo, 
            accuracy = accuracy,
            max_combo = beatmapInfo['max_combo'],
            pp = None, 
            misses = misses, 
            beatmap_id = beatmap_id
        )
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        return text, bgPicture

    def getGatariUserRecent(self, username, limit):
        r = self.session.get(self.GATARI_API + "/users/get", params = { 
            'u' : username
        })
        user_id = r.json()['users'][0]['id']
        r = self.session.get(self.GATARI_API + "/user/scores/recent", params = {
            'id' : user_id,
            'l' : limit,
            'f': '1'
            })
        limit -= 1
        js = r.json()['scores'][limit]
        beatmapSet_id = js['beatmap']['beatmapset_id']
        beatmap_id = js['beatmap']['beatmap_id']
        max_combo =  js['beatmap']['fc']
        combo = js['max_combo']
        misses = js['count_miss']
        m = js['mods']
        accuracy = js['accuracy']
        title = js['beatmap']['song_name']
        pp = str(js['pp'])
        ranking = js['ranking']
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        text = osuHelpers.scoreFormat(
            username = username,
            title = title,
            m = m,
            accuracy = accuracy,
            max_combo = max_combo,
            combo = combo,
            misses = misses,
            pp = pp,
            beatmap_id = beatmap_id
        )
        if ranking == 'F':
            text = "UNSUBMITTED\n" + text
        return text, bgPicture
        
    def getOfficialUserBest(self, username, limit = 1):
        if limit > 50:
            return "Слишком большой предел, максимум 50"
        limit -= 1 
        r = self.session.get(self.OFFICIAL_API + '/get_user_best', params={'k': self.key, 'u': username, 'limit': limit + 1})
        js = r.json()
        if not js:
            return "Пользователь не найден"
        beatmap_id = js[limit]['beatmap_id']
        pp = js[limit]['pp']
        combo =  js[limit]['maxcombo']
        count50 = js[limit]['count50']
        count100 = js[limit]['count100']
        count300 = js[limit]['count300']
        misses = js[limit]['countmiss']
        m = js[limit]['enabled_mods']
        accuracy = osuHelpers.acc_calc(int(misses),int(count50),int(count100),int(count300))
        if self.getBeatmapFromDB(beatmap_id) is None:
            r = self.session.get(self.OFFICIAL_API + '/get_beatmaps', params={'k': self.key, 'b' : beatmap_id})
            js = r.json()
            beatmapInfo = js[0]
            self.addBeatmapToDB(beatmapInfo)
        else:
            beatmapInfo = self.getBeatmapFromDB(beatmap_id)
        beatmapSet_id = beatmapInfo["beatmapset_id"]
        artist = beatmapInfo['artist']
        songTitle = beatmapInfo['title']
        version = beatmapInfo['version']
        title = "{} - {} [{}]".format(artist, songTitle, version)
        r = self.session.get(self.OFFICIAL_API + '/get_user', params={'k': self.key, 'u': username})
        js = r.json()[0]
        text = osuHelpers.scoreFormat(
            username = js["username"], 
            m = m,
            title = title, 
            combo = combo, 
            accuracy = accuracy,
            max_combo = beatmapInfo['max_combo'], 
            misses = misses, 
            pp = pp, 
            beatmap_id = beatmap_id
        )
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        return text, bgPicture

    def getGatariUserBest(self, username, limit = 1):
        r = self.session.get(self.GATARI_API + "/users/get", params = { 
            'u' : username
        })
        user_id = r.json()['users'][0]['id']
        r = self.session.get(self.GATARI_API + "/user/scores/best", params = { 
            'id' : user_id,
            'l': limit
        })
        limit -= 1
        js = r.json()['scores'][limit]
        beatmapSet_id = js['beatmap']['beatmapset_id']
        beatmap_id = js['beatmap']['beatmap_id']
        max_combo =  js['beatmap']['fc']
        combo = js['max_combo']
        misses = js['count_miss']
        m = js['mods']
        accuracy = js['accuracy']
        title = js['beatmap']['song_name']
        pp = js['pp']
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        text = osuHelpers.scoreFormat(
            username = username,
            title = title,
            m = m,
            accuracy = accuracy,
            max_combo = max_combo,
            combo = combo,
            misses = misses,
            pp = str(pp),
            beatmap_id = beatmap_id
        )
        return text, bgPicture