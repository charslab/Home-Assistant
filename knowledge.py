import requests
import auth
import wolframalpha
import translator
import pprint

service_url = 'https://kgsearch.googleapis.com/v1/entities:search'


def wiki_search(query, lang):
    req = requests.get('https://kgsearch.googleapis.com/v1/entities:search',
                       params={'query': query,
                               'limit': 1,
                               'indent': True,
                               'key': auth.GOOGLE_KNOWLEDGE_KEY,
                               'languages': lang
                               })
    response = req.json()
    return response['itemListElement'][0]['result']['detailedDescription']['articleBody']


wolfram_client = wolframalpha.Client(auth.WOLFRAM_ALPHA_KEY)


def wolfram_search(query, lang):
    global wolfram_client

    query = translator.translate(lang, 'en', query)
    print(query)
    res = wolfram_client.query(query)

    pprint.pprint(res)

    return translator.translate('en', lang, next(res.results).text)

