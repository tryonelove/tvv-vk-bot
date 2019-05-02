from bot import Bot
from threading import Thread
import json


with open("config.json", "r") as f:
    config = json.load(f)

    
if __name__ == "__main__":
    bot = Bot(config["test_token"], 178909901)
    bot.botStart()
    # a.start()
    # b.start()
    # a.join()
    # b.join()