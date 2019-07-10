from bot import Bot
import json
import sqlite3

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
        "maps": {}, 
        "commands": {}
        }
    for filename, value in required.items():
        try:
            open(filename+".json")
        except FileNotFoundError:
            with open(filename+".json", "w+") as f:
                json.dump(value, f, indent=4)
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, server TEXT, osu_username TEXT)")
    db.commit()
    cursor.close()
    db.close()

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
