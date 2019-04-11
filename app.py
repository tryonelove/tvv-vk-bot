from bot import Bot

import json


with open("config.json", "r") as f:
    config = json.load(f)

bot = Bot(api_token="d10f958717ec12d4b668fe4506f50db8bd6e053535ca377ee89d157bf02b8841d47dd736644087be2922e", group_id=178909901)

bot.start()