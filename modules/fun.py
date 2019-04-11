import requests
from constants.weather import weather_state
import random


def weather(city):
    emoji = ''
    descr = ''
    request = requests.Session()
    try:
        r = request.get('http://api.openweathermap.org/data/2.5/weather',
                        params={'q': city, 'APPID': '81d59d3e4bcd5bd5b69f6f95250213ee'})
        js = r.json()
        C = round(float(js['main']['temp']) - 273)
        wind = js['wind']['speed']
        try:
            descr = weather_state.get(js['weather'][0]['main'])
        except:
            descr = js['weather'][0]['main']
        text = (city.capitalize() + ', ' + js['sys']['country']+"\n"+emoji + descr + '\nТемпература: ' + str(C) + "°C" +
                '\nВлажность: ' + str(js['main']['humidity']) + '%' +
                '\nСкорость ветра: ' + str(wind) + ' м/c')
    except:
        text = "Не нашёл такого города"
    return text


def roll(limit):
    if limit.isdigit():
        return random.randint(1, int(limit))
    return random.randint(1, 100)
