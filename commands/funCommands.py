import json
import random
from commands.interfaces import ICommand
import requests
from helpers import exceptions


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

    def __init__(self, *city):
        super().__init__()
        self._city = " ".join(city)

    def execute(self):
        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
                         params={"q": self._city, "APPID": "81d59d3e4bcd5bd5b69f6f95250213ee"})
        if r.status_code != 200:
            raise exceptions.APIRequestError()
        js = r.json()
        if not js or js["cod"] == "404":
            raise exceptions.APIRequestError()
        temperature = round(float(js['main']['temp']) - 273)
        wind = js['wind']['speed']
        descr = self.WEATHER_STATE.get(
            js['weather'][0]['main'], js['weather'][0]['main'])
        country = js['sys']['country']
        humidity = js['main']['humidity']
        text = f"{self._city.capitalize()}, {country}\n{descr}\nТемпература: {temperature}°C\n\
        Влажность: {humidity}%\nСкорость ветра: {wind} м/с"
        return self.Message(text)


class Roll(ICommand):
    """
    Roll a random number command
    """
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
