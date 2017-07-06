"""
    Copyright (C) 2017 charslab

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA"""

import requests
import datetime


class Forecast(object):
    location = None
    wind = None
    atmosphere = None
    item = None
    forecast = None


def fahrenheit_to_celsius(temp):
    return str(int((int(temp) - 32) * 5 / 9))


def celsius_to_fahrenheit(temp):
    return int(temp) * 9 / 5 + 32


def translateText(string):
    string = string.lower()

    if string == "rain":
        return "pioggia"

    if string == "scattered showers":
        return "piogge sparse"

    if string == "showers":
        return "piogge"

    if string == "scattered thunderstorms":
        return "temporali sparsi"

    if string == "cloudy":
        return "nuvoloso"

    if string == "partly cloudy":
        return "parzialmente nuvoloso"

    if string == "sunny":
        return "soleggiato"

    if string == "mostly sunny":
        return "prevalentemente soleggiato"

    if string == "thunderstorms":
        return "temporali"

    if string == "mostly cloudy":
        return "prevalentemente nuvoloso"

    return string


def dateToDay(date):
    day = datetime.datetime.strptime(date, "%d %b %Y").strftime("%A")

    if day == "Monday":
        return "Lunedì"

    elif day == "Tuesday":
        return "Martedì"

    elif day == "Wednesday":
        return "Mercoledì"

    elif day == "Thursday":
        return "Giovedì"

    elif day == "Friday":
        return "Venerdì"

    elif day == "Saturday":
        return "Sabato"
    else:
        return "Domenica"


def getForecast(city, state):
    req = requests.get(
        'http://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="' + city + ',' + state + '")&format=json&u=c')

    result = req.json()

    location = result["query"]["results"]["channel"]["units"]
    wind = result["query"]["results"]["channel"]["wind"]
    atmosphere = result["query"]["results"]["channel"]["atmosphere"]
    astronomy = result["query"]["results"]["channel"]["astronomy"]
    item = result["query"]["results"]["channel"]["item"]
    forecast = item['forecast']

    obj = Forecast()
    obj.wind = wind
    obj.atmosphere = atmosphere
    obj.astronomy = astronomy
    obj.item = item
    obj.forecast = forecast

    obj.item['condition']['temp'] = fahrenheit_to_celsius(obj.item['condition']['temp'])
    obj.item['condition']['text'] = translateText(obj.item['condition']['text'])

    for i in range(0, 7):
        obj.forecast[i]['high'] = fahrenheit_to_celsius(obj.forecast[i]['high'])
        obj.forecast[i]['low'] = fahrenheit_to_celsius(obj.forecast[i]['low'])
        obj.forecast[i]['text'] = translateText(obj.forecast[i]['text'])
        obj.forecast[i]['date'] = dateToDay(obj.forecast[i]['date'])

    speed = wind["speed"]  # km/h
    humidity = atmosphere['humidity']  # 0-100
    visibility = atmosphere['visibility']  # km

    return obj