#!/usr/bin/env python3
# MIT License

# Copyright (c) 2018 Róbert Kjaran <robert@kjaran.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import argparse
import base64
import json
import wave
import requests


def recognize_wav(api_endpoint, api_key, wav_file) -> str:
    payload = {'config': {'encoding': 'LINEAR16',
                          'languageCode': 'is-IS',
                          'sampleRate': wav_file.getframerate(),
                          'wordAlignment': False,
                          'maxAlternatives': 1},
               'audio': {'content': base64.b64encode(
                   wav_file.readframes(wav_file.getnframes())).decode() }}
    response = requests.post(api_endpoint,
                             headers={'authorization': 'Bearer ' + api_key},
                             json=payload)
    response.raise_for_status()
    transcript = response.json()['results'][0]['alternatives'][0]['transcript']
    return transcript


def parse_args():
    def open_wave(x):
        return wave.open(x, 'rb')

    po = argparse.ArgumentParser(
        description="""Example usage of the Speech::SyncRecognize API.  Set the
        environment variable TALA_API_KEY to the API key you generated at
        https://tal.ru.is/stjori
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    po.add_argument('--uri',
                    default='https://tal.ru.is/v1/speech:syncrecognize',
                    help='URI of Speech API endpoint.')
    po.add_argument('wav_path', type=open_wave, help='WAV file to recognize.')
    args = po.parse_args()
    args.api_key = os.environ['TALA_API_KEY']

    return args


def main(args):
    result = recognize_wav(args.uri, args.api_key, args.wav_path)
    print(result)


if __name__ == '__main__':
    args = parse_args()
    main(args)
