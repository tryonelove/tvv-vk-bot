import requests
from objects import glob
from constants.roles import Roles
from constants import osuConstants
from config import OSU_API_KEY
import re
import datetime
from helpers import banchoApi

class Utils:
    def __init__(self):
        self.api = banchoApi.BanchoApi()

    @staticmethod
    def upload_picture(url, decode_content=False):
        """
        Upload image to the server
        :param url: image URL
        """
        image = requests.get(url, stream=True).raw
        image.decode_content = decode_content
        photo = glob.upload.photo_messages(photos=image)[0]
        return "photo{}_{}".format(photo['owner_id'], photo['id'])

    @staticmethod
    def find_largest_attachment(attachments):
        """
        Find the largest attached image
        :param attachments: attachments list
        """
        largest = 0
        for image in attachments:
            larger = image["width"]*image["height"]
            if larger > largest:
                largest = larger
                largest_pic = image["url"]
        return largest_pic

    @staticmethod
    def get_role(user_id):
        """
        Get user role

        :param user_id: user_id
        """
        return glob.c.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()[0]

    @staticmethod
    def has_role(user_id, required_role):
        """
        Check if user has a required role

        :param user_id: user_id to check
        :param required_role: role to check
        """
        role = Utils.get_role(user_id)
        return role & required_role.value > 0

    @staticmethod
    def get_server_username(user_id):
        """
        Return server and username from database
        """
        return glob.c.execute("SELECT server, username FROM users WHERE id = ?", (user_id,)).fetchone()

    def get_cached_beatmap(self, beatmap_id):
        """
        Get cached beatmap data
        """
        db_data = glob.c.execute(
            "SELECT * FROM beatmaps WHERE beatmap_id = ?", (beatmap_id,)).fetchone()
        if db_data is None:
            beatmap = self.api.get_beatmaps(b=beatmap_id)
            db_data = Utils._cache_beatmap(beatmap[0])
        else:
            beatmapData = glob.c.execute(
                "SELECT beatmapsets.background_url, beatmaps.beatmapset_id, beatmapsets.artist, beatmapsets.title, beatmaps.version, beatmaps.max_combo FROM beatmaps INNER JOIN beatmapsets ON beatmaps.beatmapset_id = beatmapsets.beatmapset_id WHERE beatmap_id=?", (beatmap_id,)).fetchone()
            template = ["background_url", "beatmapset_id", "artist",
                        "title", "version", "max_combo"]
            db_data = dict(zip(template, beatmapData))
        return db_data

    @staticmethod
    def _cache_beatmap(beatmap_object):
        """
        Save beatmap into database and return its object

        :param beatmap_object: osu! api beatmap object
        """
        beatmap_object["background_url"] = Utils.upload_beatmapset_background(
            beatmap_object["beatmapset_id"])
        glob.c.execute("INSERT OR IGNORE INTO beatmapsets VALUES (?, ?, ?, ?)", (
            beatmap_object["beatmapset_id"], beatmap_object["artist"], beatmap_object["title"], beatmap_object["background_url"]))
        glob.c.execute("INSERT OR IGNORE INTO beatmaps VALUES(?,?,?,?)", (
            beatmap_object["beatmapset_id"], beatmap_object["beatmap_id"], beatmap_object["version"], beatmap_object["max_combo"]))
        glob.db.commit()
        return beatmap_object

    @staticmethod
    def upload_beatmapset_background(beatmapSet_id):
        """
        Upload beatmapset background image

        :param beatmapSet_id: osu! beatmapset id
        """
        background_url = "https://assets.ppy.sh/beatmaps/{}/covers/cover.jpg".format(
            beatmapSet_id)
        try:
            uploaded_url = Utils.upload_picture(background_url)
        except:
            uploaded_url = "photo-178909901_456239049"
        return uploaded_url

    @staticmethod
    def is_creator(user_id):
        return user_id == 236965366

    @staticmethod
    def get_osu_params(string, user_id):
        """
        Get a dictionary, containing 
        server, username, score limit and user_id
        """

        params = {"server": None, "username": None,
                  "limit": 1, "user_id": user_id}
        data = Utils.get_server_username(user_id)
        if string:
            result = re.match(r"(bancho|gatari|банчо|гатари)?(.*?)?(\d+)?$", string)
            params["server"] = result.group(1) or None
            params["username"] = result.group(2) or None
            params["limit"] = result.group(3) or 1
        if not params["server"]:
            params["server"] = data[0]
        if not params["username"] or params["username"].isspace():
            params["username"] = data[1]
        params["server"] = params["server"].strip()
        params["username"] = params["username"].strip()
        return params

    @staticmethod
    def find_beatmap_id(string):
        """
        Return beatmap id from a text message
        """
        beatmap_id = None
        if "beatmapsets" in string:
            result = re.search(
                r"^https?:\/\/?osu.ppy.sh\/beatmapsets\/(\d+)(#\w+)\/(\d+)?", string)
            beatmap_id = result.group(3)
        elif "/b/" in string:
            result = re.search(r".*\/b/(\d+)", string)
            beatmap_id = result.group(1)
        return beatmap_id

    @staticmethod
    def calculate_accuracy(misses, count50, count100, count300):
        accuracy = (50*count50+100*count100+300*count300) * \
            100/(300*(misses+count50+count100+count300))
        return accuracy

    @staticmethod
    def find_user_id(string):
        """
        Return user_id from a message with a mention.
        """
        user_id = re.search(r"id(\d+)", string).group(1)
        return user_id

    @staticmethod
    def get_donator_expire_date(user_id):
        """
        Get expire date and role name

        :param user_id: target user_id
        """
        return glob.c.execute("SELECT expires, role FROM donators WHERE id=?", (user_id,)).fetchone()
            
    @staticmethod
    def get_weather_city(user_id):
        return glob.c.execute("SELECT city FROM weather WHERE id=?", (user_id,)).fetchone()

    @staticmethod
    def is_level_disabled(chat_id):
        return glob.c.execute("SELECT * FROM disabled_level WHERE chat_id=?", (chat_id,)).fetchone()