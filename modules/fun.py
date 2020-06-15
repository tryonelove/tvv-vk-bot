import json
import random
from .command import Command
import requests

class Weather(Command):
    WEATHER_STATE = {
        "Clear": "Ясно ☀ ",
        "Cloudsovercast": "Переменная облачность ⛅ ",
        "Clouds": "Облачно ☁ ",
        "Rainlight": "Пасмурно ☁",
        "Rain": "Дождь ☔",
        "Mist": "Легкий туман 🌫",
        "Fog": "Туман 🌫",
        "Snow": "Снег ❄"
    }

    def __init__(self, *city):
        super().__init__()
        self._city = " ".join(city)

    def execute(self):
        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
                             params={"q": self._city, "APPID": "81d59d3e4bcd5bd5b69f6f95250213ee"})
        if r.status_code != 200:
            raise NotImplementedError()
        js = r.json()
        if not js or js["cod"] == "404":
            raise NotImplementedError()
        temperature = round(float(js['main']['temp']) - 273)
        wind = js['wind']['speed']
        descr = self.WEATHER_STATE.get(
            js['weather'][0]['main'], js['weather'][0]['main'])
        country = js['sys']['country']
        humidity = js['main']['humidity']
        text = "{}, {}\n{}\nТемпература: {}°C\n\
        Влажность: {}%\nСкорость ветра: {} м/с".format(self._city.capitalize(), country,
                                                       descr, temperature, humidity, wind)
        return self.Message(text)


class Roll(Command):
    def __init__(self, limit, *args):
        super().__init__()
        self._limit = self.__check_value(limit)

    def __check_value(self, value):
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            return 100
        return value

    def execute(self):
        value = str(random.randint(1, self._limit))
        return self.Message(value)