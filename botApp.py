from bot import Bot

import json


with open("config.json", "r") as f:
    config = json.load(f)

bot = Bot(api_token=config["token"], group_id=176954825)

bot.start()