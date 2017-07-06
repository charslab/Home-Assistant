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
import auth

yandex_detect_url = "https://translate.yandex.net/api/v1.5/tr.json/detect?key=" + auth.YANDEX_KEY
yandex_translate_url = "https://translate.yandex.net/api/v1.5/tr.json/translate?key=" + auth.YANDEX_KEY


def detect_language(text):
    global yandex_detect_url

    r = requests.post(yandex_detect_url, data={'text': text})
    res = r.json()

    if 'lang' in res:
        return res['lang']
    else:
        return None


def translate(target, text):
    global yandex_translate_url

    lang = "it-" + target

    r = requests.post(yandex_translate_url, data={'lang': lang,
                                                  'text': text})
    res = r.json()
    return str(res['text'][0])