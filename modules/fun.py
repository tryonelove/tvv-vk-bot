import requests
from constants.weather import weather_state
import random
import re
from objects import glob
from constants import exceptions

def weather(city):
    emoji = ''
    descr = ''
    request = requests.Session()
    r = request.get('http://api.openweathermap.org/data/2.5/weather',
                    params={'q': city, 'APPID': '81d59d3e4bcd5bd5b69f6f95250213ee'})
    js = r.json()
    if not js or js["cod"]=="404":
        raise exceptions.CustomException("Не нашёл такого города")
    C = round(float(js['main']['temp']) - 273)
    wind = js['wind']['speed']
    descr = weather_state.get(js['weather'][0]['main'])
    if descr is None:
        descr = js['weather'][0]['main']
    text = (city.capitalize() + ', ' + js['sys']['country']+"\n"+emoji + descr + '\nТемпература: ' + str(C) + "°C" +
            '\nВлажность: ' + str(js['main']['humidity']) + '%' +
            '\nСкорость ветра: ' + str(wind) + ' м/c')
    return text


def roll(text):
    if text!="":
        text = text.split()
    if len(text) >= 1:
        if text[0].isdigit() and int(text[0]) > 0:
            return random.randint(1, int(text[0]))
    return random.randint(1, 100)

