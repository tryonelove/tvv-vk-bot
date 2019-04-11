from websocket import create_connection
import time
import json
import helpers.glob as glob
from helpers.osu_stuff import readableMods
import logging
import requests
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


def scoreFormat(username, title, m, accuracy, combo, max_combo, misses, pp, beatmap_id):
    misses = "" if str(misses) == "0" else str(misses)+"xMiss"
    mods = "" if str(m)=="0" else "+" + readableMods(int(m))
    text = '{username} | {title} {mods} ({accuracy}%) {combo}/{max_combo} {misses} | {pp}pp\nhttps://osu.ppy.sh/b/{beatmap_id}'.format(username = username, mods=mods, title=title, combo=combo, accuracy=accuracy,max_combo=max_combo, misses=misses, pp=pp, beatmap_id=beatmap_id)
    return text

def dataHandler(data):
    # logging.info("gagaru TRACKING LIST NOW: "+ str(glob.config["gatari_tracking"]))
    if data.get("type") == "score" and data.get("data"):
        data = data.get("data")
        username = data["user"].get("username")
        if username in glob.config["gatari_tracking"]:
            pp = data.get("pp")
            id = data["user"]["id"]
            session = requests.Session()
            try:
                r = session.get("http://api.gatari.pw/user/scores/best?id={}&l=10&p=1&mode=0&f=0".format(id))
                top10score = r.json()["scores"][9]["pp"]
            except IndexError:
                top10score = 0
            if float(pp)>200 or float(pp)>float(top10score):
                message = ""
                beatmapSetID = data.get("beatmapSetID")
                beatmapID = data.get("beatmapID")
                rawoldpp = data.get("rawoldpp")
                rawpp = data.get("rawpp")
                username = data["user"].get("username")
                count_miss = data.get("count_miss")
                pp = data.get("pp")
                accuracy = round(float(data.get("accuracy")), 2)
                combo = data.get("max_combo")
                mods = data.get("mods")
                r = session.get("https://osu.ppy.sh/api/get_beatmaps", params = {"k": "5beebba6ca8a4ba4a95cb2993117424a401df550", "b": beatmapID})
                js = r.json()[0]
                title = js["artist"] + " - " + js["title"] + " [" + js["version"] + "]"
                max_combo = js["max_combo"]
                if rawpp>rawoldpp:
                    message += "Лёгкие %sпп для %s\n" % (rawpp-rawoldpp, username)
                message += scoreFormat(username, title, mods, accuracy, combo, max_combo, count_miss, pp, beatmapID)
                try:
                    img = session.get("https://assets.ppy.sh/beatmaps/{}/covers/cover.jpg".format(beatmapID), stream=True).raw
                    bg = glob.upload.photo_messages(photos=img)[0]
                    bg_link = 'photo{}_{}'.format(bg['owner_id'], bg['id'])
                except:
                    bg_link = "photo-176954825_456239264"
                glob.vk.messages.send(peer_id = 2000000001, message = message, attachment = bg_link)

def connect():
    logging.info("Connected succesfully!")
    ws = create_connection("wss://ws.gatari.pw")
    ws.send(json.dumps({"type":"subscribe_scores", "data":[]}))
    return ws

def tracking_start():
    ws = connect()
    while True:
        try:
            if not ws.connected:
                logging.info("WebSocket connection lost, reconnecting...")
                ws = connect()
            result = ws.recv()
            data = json.loads(result)
            dataHandler(data)
            time.sleep(1)
        except Exception as e:
            logging.error(str(e))