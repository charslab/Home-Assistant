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

import pprint
import auth
import time
import audiorecorder

from wit import Wit
from homeassistant import assistant

client = Wit(access_token=auth.WIT_KEY)
recorder = audiorecorder.AudioRecorder()


def assistant_callback():
    global recorder

    start_time = time.time()
    # recorder.record_to_file()

    # with open('recorded.wav', 'rb') as f:
    #    resp = client.speech(f, None, {'Content-Type': 'audio/wav'})
    resp = recorder.record_and_stream()

    pprint.pprint(resp)
    elapsed_time = time.time() - start_time
    print("Took {0}".format(elapsed_time))

    assistant.handle_response(resp)


if __name__ == '__main__':
    recorder.adjust_noise_level()
    recorder.set_silence_timeout(15)

    assistant.start(assistant_callback, hotword_sensivity=0.8)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        assistant.stop()

