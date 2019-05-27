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
import logging
import pyttanko
from .api import BanchoApi, GatariApi
import time

class Osu:
    def __init__(self, key, from_id, upload):
        self.banchoApi = BanchoApi(key)
        self.gatariApi = GatariApi()
        self.from_id = from_id
        self.upload = upload
        self.session = requests.Session()
        with open("maps.json", 'r', encoding= "UTF-8") as maps:
            self.maps = json.load(maps)

    def getBeatmap(self, beatmap_id):
        if isinstance(beatmap_id, str):
            beatmap_id = int(beatmap_id)
        r = self.session.get("https://osu.ppy.sh/osu/%d" % beatmap_id)
        open("temp.osu", 'wb').write(r.content)
        f = open("temp.osu")
        return f

    def calculatePP(self, osuFile, **kwargs):
        p = pyttanko.parser()
        bmap = p.map(osuFile)
        stars = pyttanko.diff_calc().calc(bmap, kwargs.get("mods", 0))
        pp,_,_,_,_ = pyttanko.ppv2(stars.aim, stars.speed, **kwargs, bmap=bmap)
        kwargs["nmiss"] = 0
        kwargs["combo"] = bmap.max_combo()
        pp_if_fc,_,_,_,_ = pyttanko.ppv2(stars.aim, stars.speed, **kwargs, bmap=bmap)
        return round(pp, 2), round(pp_if_fc, 2)
    
    def getPP(self, beatmap_id, **kwargs):
        f = self.getBeatmap(beatmap_id)
        return self.calculatePP(f, **kwargs)

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
        beatmapData["background_url"] = self.getBeatmapBG(beatmapSet_id)
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
        beatmap_id = str(beatmap_id)
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
        """Загрузка бг карты в вк
        
        :param beatmapSet_id: айди сета
        :return: vk_background_url
        """
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
        js = self.banchoApi.get_user_recent(u=username, limit=limit)
        limit -= 1 
        if not js:
            return "Нет данных, возможно, что пользователь в бане, либо нет скоров за последние 24 часа"
        beatmap_id = int(js[limit]['beatmap_id'])
        combo =  int(js[limit]['maxcombo'])
        count50 = int(js[limit]['count50'])
        count100 = int(js[limit]['count100'])
        count300 = int(js[limit]['count300'])
        misses = int(js[limit]['countmiss'])
        m = int(js[limit]['enabled_mods'])
        ranking = js[limit]['rank']
        accuracy = osuHelpers.acc_calc(misses,count50,count100,count300)
        if self.getBeatmapFromDB(beatmap_id) is None:
            beatmapInfo = self.banchoApi.get_beatmaps(b=beatmap_id)[0]
            self.addBeatmapToDB(beatmapInfo)
        else:
            beatmapInfo = self.getBeatmapFromDB(beatmap_id)
        beatmapSet_id = beatmapInfo["beatmapset_id"]
        artist = beatmapInfo['artist']
        songTitle = beatmapInfo['title']
        version = beatmapInfo['version']
        title = "{} - {} [{}]".format(artist, songTitle, version)
        js = self.banchoApi.get_user(u=username)[0]
        pp, pp_if_fc = self.getPP(beatmap_id = beatmap_id, mods=m, n300=count300, 
            n100=count100, n50=count50,combo=combo, nmiss=misses)
        text = osuHelpers.scoreFormat(
            username = js["username"], 
            m = m,
            title = title, 
            combo = combo, 
            accuracy = accuracy,
            max_combo = beatmapInfo['max_combo'],
            _pp = pp,
            pp_if_fc=pp_if_fc, 
            misses = misses, 
            beatmap_id = beatmap_id
        )
        bgPicture = beatmapInfo.get("background_url", None)
        if bgPicture is None:
            bgPicture = self.getBeatmapBG(beatmapSet_id)
        if ranking == 'F':
            text = "UNSUBMITTED\n" + text
        return text, bgPicture

    def getGatariUserRecent(self, username, limit):
        text = ""
        user_id = self.gatariApi.get_user(username)["users"][0]["id"]
        js = self.gatariApi.get_user_recent(user_id, limit, show_failed=True)['scores']
        limit -= 1
        js = js[limit]
        beatmapSet_id = js['beatmap']['beatmapset_id']
        beatmap_id = js['beatmap']['beatmap_id']
        max_combo =  js['beatmap']['fc']
        combo = js['max_combo']
        count50 = js['count_50']
        count100 = js['count_100']
        count300 = js['count_300']
        misses = js['count_miss']
        m = js['mods']
        accuracy = js['accuracy']
        title = js['beatmap']['song_name']
        pp, pp_if_fc = self.getPP(beatmap_id = beatmap_id, mods=m, n300=count300, 
        n100=count100, n50=count50,combo=combo, nmiss=misses)
        ranking = js['ranking']
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        if ranking == 'F':
            text += "UNSUBMITTED\n"
        text += osuHelpers.scoreFormat(
            username = username,
            title = title,
            m = m,
            accuracy = accuracy,
            max_combo = max_combo,
            combo = combo,
            misses = misses,
            _pp = pp,
            pp_if_fc = pp_if_fc,
            beatmap_id = beatmap_id
        )
        return text, bgPicture
        
    def getOfficialUserBest(self, username, limit = 1):
        if limit > 50:
            return "Слишком большой предел, максимум 50"
        js = self.banchoApi.get_user_best(u=username, limit=limit)
        limit -= 1
        if not js:
            return "Нет данных, пользователь не найден"
        beatmap_id = int(js[limit]['beatmap_id'])
        combo =  int(js[limit]['maxcombo'])
        count50 = int(js[limit]['count50'])
        count100 = int(js[limit]['count100'])
        count300 = int(js[limit]['count300'])
        misses = int(js[limit]['countmiss'])
        m = int(js[limit]['enabled_mods'])
        accuracy = osuHelpers.acc_calc(misses,count50,count100,count300)
        if self.getBeatmapFromDB(beatmap_id) is None:
            beatmapInfo = self.banchoApi.get_beatmaps(b=beatmap_id)[0]
            self.addBeatmapToDB(beatmapInfo)
        else:
            beatmapInfo = self.getBeatmapFromDB(beatmap_id)
        beatmapSet_id = beatmapInfo["beatmapset_id"]
        artist = beatmapInfo['artist']
        songTitle = beatmapInfo['title']
        version = beatmapInfo['version']
        title = "{} - {} [{}]".format(artist, songTitle, version)
        js = self.banchoApi.get_user(u=username)[0]
        pp, pp_if_fc = self.getPP(beatmap_id = beatmap_id, mods=m, n300=count300, 
        n100=count100, n50=count50,combo=combo, nmiss=misses)
        text = osuHelpers.scoreFormat(
            username = js["username"], 
            m = m,
            title = title, 
            combo = combo, 
            accuracy = accuracy,
            max_combo = beatmapInfo['max_combo'], 
            misses = misses, 
            _pp = pp,
            pp_if_fc=pp_if_fc,
            beatmap_id = beatmap_id
        )
        bgPicture = beatmapInfo.get("background_url", None)
        if bgPicture is None:
            bgPicture = self.getBeatmapBG(beatmapSet_id)
        return text, bgPicture

    def getGatariUserBest(self, username, limit = 1):
        try:
            js = self.gatariApi.get_user(username=username)
            user_id = js["users"][0]["id"]
            username = js["users"][0]["username"]
        except:
            return "Нет данных, пользователь не найден"
        js = self.gatariApi.get_user_best(user_id, limit)
        limit -= 1
        js = js['scores'][limit]
        beatmapSet_id = js['beatmap']['beatmapset_id']
        beatmap_id = js['beatmap']['beatmap_id']
        max_combo =  js['beatmap']['fc']
        combo = js['max_combo']
        misses = js['count_miss']
        m = js['mods']
        accuracy = js['accuracy']
        count50 = js['count_50']
        count100 = js['count_100']
        count300 = js['count_300']
        misses = js['count_miss']
        title = js['beatmap']['song_name']
        pp, pp_if_fc = self.getPP(beatmap_id = beatmap_id, mods=m, n300=count300, 
        n100=count100, n50=count50,combo=combo, nmiss=misses)
        text = osuHelpers.scoreFormat(
            username = username,
            title = title,
            m = m,
            accuracy = accuracy,
            max_combo = max_combo,
            combo = combo,
            misses = misses,
            _pp = pp,
            pp_if_fc=pp_if_fc,
            beatmap_id = beatmap_id
        )
        bgPicture = self.getBeatmapBG(beatmapSet_id)
        return text, bgPicture

    def compare(self, messages, username: str = None):
        limit = 1
        if username == "":
            username = utils.getUserFromDB(self.from_id).get("username")
        if username is None:
            return "Чё за чел?"
        if title_re.findall(messages["text"]):
            beatmap_id = int(beatmap_id_re.findall(messages["text"])[0])
        else:
            return "хз"
        js = self.banchoApi.get_scores(b=beatmap_id, u=username, limit = limit)
        limit -= 1
        if not js:
            return "Нет данных, возможно, что пользователь не найден, либо нет скоров на мапе"
        combo =  int(js[limit]['maxcombo'])
        count50 = int(js[limit]['count50'])
        count100 = int(js[limit]['count100'])
        count300 = int(js[limit]['count300'])
        misses = int(js[limit]['countmiss'])
        m = int(js[limit]['enabled_mods'])
        accuracy = osuHelpers.acc_calc(misses,count50,count100,count300)
        if self.getBeatmapFromDB(beatmap_id) is None:
            beatmapInfo = self.banchoApi.get_beatmaps(b=beatmap_id)[0]
            self.addBeatmapToDB(beatmapInfo)
        else:
            beatmapInfo = self.getBeatmapFromDB(beatmap_id)
        beatmapSet_id = beatmapInfo["beatmapset_id"]
        artist = beatmapInfo['artist']
        songTitle = beatmapInfo['title']
        version = beatmapInfo['version']
        title = "{} - {} [{}]".format(artist, songTitle, version)
        js = self.banchoApi.get_user(u=username)[0]
        pp, pp_if_fc = self.getPP(beatmap_id = beatmap_id, mods=m, n300=count300, 
        n100=count100, n50=count50,combo=combo, nmiss=misses)
        text = osuHelpers.scoreFormat(
            username = js["username"], 
            m = m,
            title = title, 
            combo = combo, 
            accuracy = accuracy,
            max_combo = beatmapInfo['max_combo'], 
            misses = misses, 
            _pp = pp,
            pp_if_fc=pp_if_fc,
            beatmap_id = beatmap_id
        )
        bgPicture = beatmapInfo.get("background_url", None)
        if bgPicture is None:
            bgPicture = self.getBeatmapBG(beatmapSet_id)
        return text, bgPicture