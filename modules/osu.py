import json
from objects import glob
from constants import exceptions
import requests
import json
import random
import utils 
from constants.osuConst import *  


class Osu:
    def __init__(self, key, from_id, upload):
        self.key = key
        self.from_id = from_id
        self.upload = upload
        self.session = requests.Session() 

    def osuset(self, args):
        message = args.split(" ")
        if str(self.from_id) in glob.config["donators"] or self.from_id in glob.config["admin"]:
            if len(message)>1 and message[0] in ('bancho', 'gatari'):
                from_id = str(self.from_id)
                glob.users[from_id]['server'] = message[1]
                glob.users[from_id]['osu_username'] = " ".join(message[2:])
                utils.users_update()
                return f"Аккаунт {args} был успешно привязан к вашему айди."
            raise exceptions.ArgumentError("Доступные сервера: bancho, gatari")
    
    def lemmyPicture(self, args, mode = 0):
        """
        Функция, возвращающая ссылку на пикчу с osu!lemmy
        :param: args - сервер, ник
        :param: mode - мод 
        0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania
        """
        args = utils.checkArgs(args)
        server, username = utils.getUserFromDB(args, self.from_id)
        if mode == 0:
            return None, self.osuPicture(server, username)
        if mode == 1:
            return None, self.taikoPicture(server, username)
        if mode == 2:
            return None, self.ctbPicture(server, username)
        if mode == 3:
            return None, self.maniaPicture(server, username)

    @staticmethod
    def getOfficialLemmyLink(mode, username):
        url = f'https://lemmmy.pw/osusig/sig.php?colour={random.choice(sig_colors)}&uname={username}&xpbar&xpbarhex&darktriangles&pp=1&mode={mode}'
        return url

    @staticmethod
    def getGatariLemmyLink(mode, username):
        url = f'https://lemmmy.pw/osusig/sig.php?colour={random.choice(sig_colors)}&uname={username}&xpbar&xpbarhex&darktriangles&pp=1&mode={mode}'
        return url  

    def osuPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(0, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(0, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
    
    def taikoPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(1, username)
            return None, utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(1, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
    
    def ctbPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(2, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(2, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
    
    def maniaPicture(self, server, username):
        if server == "bancho":
            image_url = self.getOfficialLemmyLink(3, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
        if server == "gatari":
            image_url = self.getGatariLemmyLink(3, username)
            return utils.upload_pic(upload = self.upload, url = image_url, decode_content = True)
    