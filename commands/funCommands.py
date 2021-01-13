import json
import random
from commands.interfaces import ICommand
import requests
from helpers import exceptions
from objects import glob
from helpers.utils import Utils


class WeatherSet(ICommand):
    KEYS = ["weatherset"]

    def __init__(self, city, user_id, *args, **kwargs):
        super().__init__()
        self._city = city
        self._user_id = user_id

    def execute(self):
        glob.c.execute("INSERT OR IGNORE INTO weather VALUES (?, ?)",
                       (self._user_id, self._city))
        glob.c.execute("UPDATE weather SET city=? WHERE id=?",
                       (self._city, self._user_id))
        glob.db.commit()
        return self.Message(f"Город {self._city} был успешно привязан.")


class Weather(ICommand):
    """
    Weather command
    """
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
    KEYS = ["weather", "погода"]

    def __init__(self, city, user_id, *args, **kwargs):
        super().__init__()
        self._city = city
        self._user_id = user_id

    def execute(self):
        if not self._city:
            try:
                self._city = Utils.get_weather_city(self._user_id)[0]
            except:
                raise exceptions.CityNotLinkedError

        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
                         params={"q": self._city, "APPID": "81d59d3e4bcd5bd5b69f6f95250213ee"})
        if r.status_code != 200:
            raise exceptions.ApiRequestError

        js = r.json()
        if not js or js["cod"] == "404":
            raise exceptions.CityNotFoundError

        temperature = round(float(js['main']['temp']) - 273)
        wind = js['wind']['speed']
        descr = self.WEATHER_STATE.get(
            js['weather'][0]['main'], js['weather'][0]['main'])
        country = js['sys']['country']
        humidity = js['main']['humidity']
        text = f"{self._city.capitalize()}, {country}\n{descr}\nТемпература: {temperature}°C\nВлажность: {humidity}%\nСкорость ветра: {wind} м/с"
        return self.Message(text)


class Roll(ICommand):
    """
    Roll a random number command
    """
    KEYS = ["roll", "ролл"]

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
