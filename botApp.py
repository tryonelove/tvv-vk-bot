from bot import Bot
import json



    
if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)
    bot = Bot(config["token"], 176954825)
    bot.start()