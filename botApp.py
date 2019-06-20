from bot import Bot
import json
import configparser

def checkConfigs():
    required = {
        "config":
                {   
                    "token": "",
                    "osu_api_key": "",
                    "donators": "",
                    "weather_api": "",
                    "prefix": "",
                    "restricted": [],
                    "admin": []
                }, 
        "maps":{}, 
        "commands":{}, 
        "users":{}
        }
    for filename in required:
        try:
            open(filename+".json")
        except FileNotFoundError:
            with open(filename+".json", "w+") as f:
                json.dump({}, f, indent=4)

def init():
    # osu!community 176954825
    # test 178909901
    checkConfigs()
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    bot = Bot(config["test_token"], 178909901)
    bot.start()

if __name__ == "__main__":
    init()
