import requests
from objects import glob
from constants.roles import Roles
from constants import osuConstants
from config import OSU_API_KEY
import re
import datetime
from helpers import banchoApi
from helpers import exceptions

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
        return max(attachments, key=lambda size: (size["width"] * size["height"])).get("url")

    @staticmethod
    def get_role(user_id):
        """
        Get user role

        :param user_id: user_id
        """
        return glob.c.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()

    @staticmethod
    def has_role(user_id, required_role):
        """
        Check if user has a required role

        :param user_id: user_id to check
        :param required_role: role to check
        """
        role = Utils.get_role(user_id)
        return role[0] & required_role.value > 0

    @staticmethod
    def get_server_username(user_id):
        """
        Return server and username from database
        """
        return glob.c.execute("SELECT * FROM osu WHERE id = ?", (user_id,)).fetchone()

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
    def get_osu_params(message, user_id):
        """
        Get a dictionary, containing 
        server, username, score limit and user_id
        """

        params = {"server": None, "username": None,
                  "limit": 1, "user_id": user_id}
        data = Utils.get_server_username(user_id)
        if message:
            result = re.match(r"(bancho|gatari|банчо|гатари|g|b|г|б)?(.*?)?(\s+\d+)?$", message)
            params["server"] = result.group(1) or None
            params["username"] = result.group(2) or None
            params["limit"] = result.group(3) or 1
        if not params["server"]:
            params["server"] = data[1] if data is not None else "bancho"
        if not params["username"] or params["username"].isspace():
            if params["server"] in osuConstants.SERVER_ACRONYMS.get("bancho"):
                params["username"] = data[2] if data is not None else None
            elif params["server"] in osuConstants.SERVER_ACRONYMS.get("gatari"):
                params["username"] = data[3] if data is not None else None
        try:
            params["server"] = params["server"].strip()
            params["username"] = params["username"].strip()
            params["limit"] = int(params["limit"])
        except:
            raise exceptions.AccountNotLinked
        return params

    @staticmethod
    def find_beatmap_id(message):
        """
        Return beatmap id from a text message
        """
        beatmap_id = None
        if "beatmapsets" in message:
            result = re.search(
                r"^https?:\/\/?osu.ppy.sh\/beatmapsets\/(\d+)(#\w+)\/(\d+)?", message)
            beatmap_id = result.group(3)
        elif "/b/" in message:
            result = re.search(r".*\/b/(\d+)", message)
            beatmap_id = result.group(1)
        return beatmap_id

    @staticmethod
    def calculate_accuracy_std(misses, count50, count100, count300):
        accuracy = (50*count50+100*count100+300*count300) * \
            100/(300*(misses+count50+count100+count300))
        return accuracy

    @staticmethod
    def calculate_accuracy_taiko(bad, good, great):
        """
        AFAIU 
        bad - countMiss
        good - count100
        great - count300
        """
        accuracy = (0.5*good+great)/(bad+good+great)
        return accuracy

    @staticmethod
    def calculate_accuracy_ctb(droplet, drop, fruit, missed_droplet, missed_drop, missed_fruit):
        """
        Note for API users: 
        To calculate the accuracy in osu!catch, 
        the number of droplets are under count50 
        and the number of missed droplets are under countkatu
        """
        accuracy = (droplet+drop+fruit)/(missed_droplet+missed_drop+missed_fruit+droplet+drop+fruit)
        return accuracy

    @staticmethod
    def find_user_id(message):
        """
        Return user_id from a message with a mention.
        """
        try:
            user_id = re.search(r"(\d+)", message).group(1)
        except:
            user_id = 0
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

    @staticmethod
    def get_reply_message_from_event(event):
        fwd_message = None
        if event.get("reply_message") is not None:
            fwd_message = event.reply_message
        if event.fwd_messages: 
            fwd_message = event.fwd_messages[-1]
        return fwd_message

    @staticmethod
    def get_experience_amount(message):
        try:
            result = re.search(
                r"(\+|\-)\d+", message)
            amount = result.group(0)
        except:
            amount = 0
        return amount