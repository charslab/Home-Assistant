import requests
import translator


def getCurrentCity(lang):
    city = None

    try:
        req = requests.get("https://api.ipify.org?format=json")
        result = req.json()
        ip = result['ip']

        req = requests.get('http://ipinfo.io/' + ip + '/json')
        data = req.json()

        city = translator.translate('en', lang, data['city'])

    except:
        print("Unable to autolocate city!")

    return city


def getCurrentCountry():
    req = requests.get("https://api.ipify.org?format=json")
    result = req.json()
    ip = result['ip']

    req = requests.get('http://ipinfo.io/' + ip + '/json')
    data = req.json()

    country = data['country']

    return country
