from websocket import create_connection
import time
import json
import logging
import requests
from helpers.osuHelpers import scoreFormat
from .utils import uploadPicture
from objects.glob import config
"""
--------------------------------------------
--------------EXAMPLE OF DATA---------------
--------------------------------------------
{'data': 
    {
        'beatmapSetID': 413987, 
        'rawoldpp': 3361, 
        'time': '2018-12-29T23:37:39',
        'count_50': 0, 
        'user': 
                {   
                    'username': 'TheWorldman', 
                    'id': 10189
                },
        'count_100': 4,
        'beatmap_md5': '53e6856b79f33b4e2623b09aa3e99b5f',
        'count_300': 391,
        'score': 3790610,
        'count_miss': 2,
        'full_combo': False,
        'play_mode': 0,
        'beatmapID': 979805,
        'mods': 0,
        'pp': 150.19,
        'rawpp': 3362,
        'rank': 'A',
        'accuracy': 98.824516296387,
        'scoreID': 23800870,
        'max_combo': 381
                },
    'type': 'score'
}

"""

class Tracking:
    def __init__(self, upload, vk, trackingList):
        self.upload = upload
        self.vk = vk
        self.connect()
        self.trackingList = trackingList

    def scoreHandler(self, data):
        logging.info(data)
        if data.get("type") == "score" and data.get("data") is not None:
            # if username not in self.trackingList:
                # return None
            score = data["data"]
            pp = score["pp"]
            if pp < 200.0:
                return None
            username = score["user"]["username"]
            beatmapSetID = score["beatmapSetID"]
            beatmapID = score["beatmapID"]
            m = score["mods"]
            combo = score["max_combo"]
            old_pp = score["rawoldpp"]
            userID = score["user"]["id"]
            new_pp = score["rawpp"]
            count_miss = score["count_miss"]
            accuracy = score["accuracy"]
            r = requests.get("https://api.gatari.pw/user/scores/recent", 
            params = {
                'id' : userID,
                'l': '1'
            })
            scoreData = r.json()
            title = scoreData["scores"][0]["beatmap"]["song_name"]
            max_combo = scoreData["scores"][0]["beatmap"]["fc"]
            text = ""
            ppFarmed = new_pp - old_pp
            if ppFarmed>1:
                text += "Лёгкие {}pp для {}\n".format(ppFarmed, username)
            text += scoreFormat(
                username, title, m, accuracy, combo, 
                max_combo, count_miss, pp, beatmapID)
            attachment = uploadPicture(self.upload,
            "https://assets.ppy.sh/beatmaps/{}/covers/cover.jpg".format(beatmapSetID))
            return {"messageText": text, "attachment": attachment}

    def connect(self):
        logging.info("Connected succesfully!")
        ws = create_connection("wss://ws.gatari.pw")
        data = json.dumps({"type":"subscribe_scores", "data":[]})
        ws.send(data)
        self.ws = ws

    def start(self):
        try:
            while not self.ws.connected:
                logging.info("WebSocket connection lost, reconnecting...")
                self.connect()
            result = self.ws.recv()
            data = json.loads(result)
            yield data
            # alert = self.scoreHandler(data)
            # if alert is not None:
            #     self.vk.messages.send(
            #                     chat_id = 1, 
            #                     message = alert["messageText"], 
            #                     attachment = alert["attachment"])
        except Exception as e:
            logging.error(str(e))

