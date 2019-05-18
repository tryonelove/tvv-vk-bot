from bot import Bot
import json

    
if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)
    # osu!community 176954825
    # test 178909901
    bot = Bot(config["test_token"], 178909901)
    bot.start()