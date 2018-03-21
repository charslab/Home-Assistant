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

import datetime
import os
import threading
import snowboydecoder
import translator
import weather
import geolocation
import knowledge
import pprint

from gtts import gTTS


class HomeAssistant:
    def __init__(self, default_language='en'):
        self.default_language = default_language
        self.callbacks = {}
        self.current_city = geolocation.getCurrentCity(default_language)
        if self.current_city is None:
            self.current_city = "Torino"

        self.semaphore_speaking = threading.Semaphore(1)
        self.semaphore_hotword = threading.Semaphore(1)
        self.semaphore_assistant = threading.Semaphore(0)
        self.on_hotword_detected_callback = self.on_hotword_detected
        self.on_assistant_activated_callback = None
        self.running = True
        self.detector = None
        self.hotword_detected = False

    def __play(self, cmd, audio_path, speech=False):
        if speech is True:
            self.semaphore_speaking.acquire()

        os.system(cmd + " " + audio_path)

        if speech is True:
            self.semaphore_speaking.release()

    def play_audio(self, audio_path, async=False):
        cmd = "mplayer -quiet -really-quiet"

        if async is True:
            thread = threading.Thread(target=self.__play, args=(cmd,), kwargs={'audio_path': audio_path})
            thread.start()
        else:
            self.__play(cmd, audio_path)

    def speak(self, string, async=False, lang=None):
        print(string)
        file = 'tmp.mp3'

        if lang is None:
            lang = self.default_language

        tts = gTTS(text=string, lang=lang)
        tts.save(file)

        # cmd = "mplayer -quiet -really-quiet -speed 1.4 -af volume=10 -af ladspa=/usr/lib/ladspa/tap_pitch:tap_pitch:0:-33:-90:0"
        cmd = "mplayer -quiet -really-quiet"
        
        if async is True:
            thread = threading.Thread(target=self.__play, args=(cmd,),
                                      kwargs={'audio_path': file, 'speech': True})
            thread.start()
        else:
            self.__play(cmd, file, speech=True)

    def handle_response(self, response):

        if 'entities' in response:
            entities = response['entities']

            if 'intent' in entities:

                intent = entities['intent']
                confidence = 0.0

                for i in intent:
                    if i['confidence'] > confidence:
                        confidence = i['confidence']
                        intent = i

                print("Intent is: {0}".format(intent['value']))

                if intent['value'] in self.callbacks:
                    self.callbacks[intent['value']](self, entities)

            elif '_text' in response:
                    self.handle_free_text(response['_text'])

    def handle_free_text(self, text): # TODO: user defined callback?
        if text is None:
            self.speak("Non ho capito")

        else:
            print("You said: " + text)

    def add_intent_callback(self, f):
        self.callbacks.setdefault(f.__name__, f)

    def on_hotword_detected(self):
        self.play_audio('resources/audio/hotword_detected.mp3', async=True)
        self.hotword_detected = True
        self.detector.terminate()
        self.semaphore_assistant.release()

    def hotword_detector_thread(self, model, sensitivity):
        self.detector = snowboydecoder.HotwordDetector(decoder_model=model, sensitivity=sensitivity)

        while self.running:
            print("HomeAssistant::hotword_detector_thread() Trying to acquire lock")
            self.semaphore_hotword.acquire()

            if self.running is False:
                print("HomeAssistant::hotword_detector_thread() Quitting")
                break

            print("HomeAssistant::hotword_detector_thread() Starting detector thread")
            self.detector.start(detected_callback=self.on_hotword_detected_callback, sleep_time=0.3)

    def start_hotword_detection(self, model, sensitivity):
        thread = threading.Thread(target=self.hotword_detector_thread, args=(model,), kwargs={'sensitivity': sensitivity})
        thread.start()

    def assistant_main_loop(self):
        while self.running:
            self.semaphore_assistant.acquire()

            if self.running is False:
                print("HomeAssistant::assistant_main_loop() Quitting")
                break

            print("HomeAssistant::assistant_main_loop() Assistant activated!")

            if self.on_assistant_activated_callback is not None:
                self.on_assistant_activated_callback()

            self.hotword_detected = False
            self.semaphore_hotword.release()

    def start(self, on_assistant_activated_callback, hotword_model='resources/alexa.umdl', hotword_sensivity=0.5):
        self.running = True
        self.play_audio('resources/audio/hotword_detected.mp3')
        self.speak("Ciao!")

        self.on_assistant_activated_callback = on_assistant_activated_callback
        self.start_hotword_detection(hotword_model, hotword_sensivity)

        thread = threading.Thread(target=self.assistant_main_loop)
        thread.start()

    def stop(self):
        self.running = False
        self.semaphore_assistant.release()
        self.semaphore_hotword.release()
        self.detector.terminate()

assistant = HomeAssistant('it')


def intent(f):
    assistant.add_intent_callback(f)


@intent
def weather_forecast(self, entities):
    location = self.current_city

    if 'location' in entities:
        location = entities['location'][0]['value']

    forecast = weather.getForecast(location, "")

    today = False
    if 'datetime' in entities:
        date = entities['datetime']

        if date[0]['type'] == 'value':  # Single day
            value = date[0]['value'].split('T')[0]
            today_date = datetime.date.today().strftime("%Y-%m-%d")

            if value == today_date:
                today = True  # Outer if

            else:
                offset = int(datetime.datetime.strptime(value, "%Y-%m-%d").strftime("%d")) - \
                         int(datetime.date.today().strftime("%d"))

                print("Offset: {0}".format(offset))
                print("Forecast for offset: {0}".format(forecast.forecast[offset]))

                speech_date = datetime.datetime.strptime(value, "%Y-%m-%d").strftime("%d %m %Y")

                self.speak("Le previsioni di " + forecast.forecast[offset]['date'] + " " + speech_date + " a " + location +
                           " sono: " + forecast.forecast[offset]["text"] + ", con massime e minime di " +
                           forecast.forecast[offset]['high'] + " e " + forecast.forecast[offset]['low'] + "°")

        else:
            # Week forecast
            string = "Le previsioni per i prossimi 7 giorni a " + location + " sono: "
            for i in range(0, 7):
                string = string + forecast.forecast[i]['date'] + ": " + forecast.forecast[i]['text'] + ", "
            string = string[:-2]
            string = string + "."
            self.speak(string)

    if 'datetime' not in entities or today is True:
        self.speak("Per oggi le previsioni a " + location + " sono: " + forecast.forecast[0]["text"] + " con massime di " + forecast.forecast[0]['high'] +
                   "°, e minime di " + forecast.forecast[0]['low'] + "°. La condizione attuale è:" + forecast.item['condition']['text'] +
                   ", con una temperatura di " + forecast.item['condition']['temp'] + "°, umidità di " +
                   forecast.atmosphere['humidity'] + "/100 e la velocità del vento è " + forecast.wind['speed'] + " km/h")


@intent
def time_current_get(self, entities):
    now = datetime.datetime.now()
    if now.hour > 1:
        self.speak("Sono le " + str(now.hour) + " e " + str(now.minute))
    if now.hour == 1:
        self.speak("è l'una e " + str(now.minute))
    if now.hour == 0:
        self.speak("è mezzanotte e " + str(now.minute))


@intent
def phrase_translation(self, entities):
    language = None
    phrase = None

    if 'language' in entities:
        language = entities['language'][0]['value']

    if 'phrase_to_translate' in entities:
        phrase = entities['phrase_to_translate'][0]['value']

    if language is None or phrase is None:
        return

    language = translator.translate(self.default_language, 'en', language).lower().strip()[0:2]

    print("Translating to {0}".format(language))
    translated_phrase = translator.translate(self.default_language, language, phrase)

    self.speak(translated_phrase, lang=language)


@intent
def latest_news(self, entities):
    None


@intent
def search_query(self, entities):

    if 'wikipedia_search_query' in entities:
        query = entities['wikipedia_search_query'][0]['value']

        try:
            result = knowledge.wiki_search(query, self.default_language)
            self.speak(result)

        except Exception as e:
            pprint.pprint(e)
            # self.speak("Spiacente, non ho trovato risultati")

            try:
                result = knowledge.wolfram_search(query, self.default_language)
                self.speak(result)

            except Exception as e:
                pprint.pprint(e)
                self.speak("Spiacente, non ho trovato risultati")

