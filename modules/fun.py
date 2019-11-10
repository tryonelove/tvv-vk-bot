import json
import random
from .command import Command

class Weather(Command):
    def __init__(self, city):
        Command.__init__(self)
        self._city = city
        self._weather_state = {
                    "Clear": "Ясно ☀ ",
                    "Cloudsovercast": "Переменная облачность ⛅ ",
                    "Clouds": "Облачно ☁ ",
                    "Rainlight": "Пасмурно ☁",
                    "Rain": "Дождь ☔",
                    "Mist": "Легкий туман 🌫",
                    "Fog": "Туман 🌫",
                    "Snow": "Снег ❄"
                }

    def execute(self):
        r = self.session.get("http://api.openweathermap.org/data/2.5/weather",
                    params={"q": self._city, "APPID": "81d59d3e4bcd5bd5b69f6f95250213ee"})
        if r.status_code == 200:
            js = r.json()
        if not js or js["cod"]=="404":
            raise NotImplementedError()
        temperature = round(float(js['main']['temp']) - 273)
        wind = js['wind']['speed']
        descr = self._weather_state.get(js['weather'][0]['main'])
        if descr is None:
            descr = js['weather'][0]['main']
        country = js['sys']['country']
        humidity = js['main']['humidity']
        text = "{}, {}\n{}\nТемпература: {}°C\n\
        Влажность: {}%\nСкорость ветра: {} м/с".format(self._city.capitalize(), country, 
        descr, temperature, humidity, wind)
        return {"message":text}


class Roll(Command):
    def __init__(self, limit):
        self._limit = int(limit) if len(limit) > 0 and limit.isdigit() and int(limit)>1 else 100

    def execute(self):
        return self.message(text=random.randint(1, self._limit))