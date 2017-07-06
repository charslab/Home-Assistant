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

import time
import wave
from array import array

import pyaudio
import requests

import auth
from homeassistant import assistant


class AudioRecorder:

    def __init__(self, format=pyaudio.paInt16, rate=8000, chunk_size=1024, threshold=500):
        self.device = pyaudio.PyAudio()

        self.FORMAT = format
        self.RATE   = rate
        self.CHUNK_SIZE = chunk_size
        self.THRESHOLD  = threshold

    def get_default_stream_in(self):
        return self.device.open(format=self.FORMAT, channels=1, rate=self.RATE,
                                input=True, output=False, frames_per_buffer=self.CHUNK_SIZE)

    def adjust_noise_level(self):
        print('AudioRecorder::adjust_noise_level() A moment of silence, please')

        stream = self.get_default_stream_in()

        start_time = time.time()
        while time.time() < start_time + 2:
            data = stream.read(self.CHUNK_SIZE)
            arr = array('h', data)

            if max(arr) > self.THRESHOLD:
                self.THRESHOLD = max(arr)

        stream.stop_stream()
        stream.close()

        print("AudioRecorder::adjust_noise_level() Threshold set to {0}".format(self.THRESHOLD))

    def is_silent(self, data):
        arr = array('h', data)
        return int(max(arr)) < self.THRESHOLD

    def record(self, timeout=10):

        stream = self.get_default_stream_in()

        silence_timeout = 20
        num_silence = 0
        phrase_started = False
        frames = []

        seconds_per_buffer = self.CHUNK_SIZE / self.RATE
        elapsed_time = 0

        print('AudioRecord::record() Starting recording')

        while elapsed_time < timeout:
            data = stream.read(self.CHUNK_SIZE)

            if len(data) == 0:
                break

            if phrase_started is True:
                frames.append(data)

            if not self.is_silent(data):
                phrase_started = True

            else:
                if phrase_started is True:
                    num_silence += 1

            if num_silence >= silence_timeout and phrase_started is True:
                print('AudioRecord::record() Detected phrase end')
                break

            elapsed_time += seconds_per_buffer

        stream.stop_stream()
        stream.close()

        assistant.play_audio('resources/audio/hotword_detected.mp3', async=True)

        return frames

    def record_to_file(self, timeout=10, path='recorded.wav'):
        frames = self.record(timeout)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.device.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print('AudioRecord::record() Recording finished')

    def yield_audio_bytes(self, timeout=10):
        stream = self.get_default_stream_in()

        frames = []
        silence_timeout = 20
        num_silence = 0
        phrase_started = False

        print('AudioRecord::yield_audio_byte() Starting recording')

        start_time = time.time()
        while time.time() < start_time + timeout:
            data = stream.read(self.CHUNK_SIZE)

            if not self.is_silent(data):
                phrase_started = True
                frames.append(data)

            else:
                if phrase_started is True:
                    num_silence += 1

            if num_silence >= silence_timeout and phrase_started is True:
                print('AudioRecord::yield_audio_byte() Detected phrase end')
                break

        stream.stop_stream()
        stream.close()

        yield b''.join(frames)

    def record_and_stream(self, timeout=10):
        frames = self.record(timeout) #TODO: Fix yield for speed

        wit_url = 'https://api.wit.ai/speech'
        headers = {'Authorization': 'Bearer ' + auth.WIT_KEY,
                   'Content-Type': 'audio/raw; encoding=signed-integer; bits=16; rate=8000; endian=little' }
                   # 'Transfer-Encoding': 'chunked'}
        # r = requests.post(wit_url, headers=headers, data=self.yield_audio_bytes(timeout))
        r = requests.post(wit_url, headers=headers, data=b''.join(frames))

        # print(r.text)
        return r.json()
