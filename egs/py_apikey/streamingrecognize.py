#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2018 Róbert Kjaran <robert@kjaran.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import base64
import os
import json
from time import sleep
from threading import Thread
import wave
from collections import OrderedDict

from ws4py.client.threadedclient import WebSocketClient

class StreamingRecognizeClient(WebSocketClient):
    def __init__(self, wav_path, *args, **kwargs):
        self.wav_path = wav_path
        self.transcripts = OrderedDict()
        super(StreamingRecognizeClient, self).__init__(*args, **kwargs)

    def opened(self):
        def run():
            with wave.open(self.wav_path, 'r') as wav:
                sample_rate = wav.getframerate()
                nframes = wav.getnframes()
                chunk_width = 800

                self.send(json.dumps(
                    {'streamingConfig': {'config': {'sampleRate': sample_rate,
                                                    'wordAlignment': False},
                                         'interimResults': True}}))


                while True:
                    chunk = wav.readframes(chunk_width)
                    if not chunk:
                        break
                    b64chunk = base64.b64encode(chunk)
                    self.send(json.dumps(
                        {'audioContent': b64chunk.decode('utf-8')}))

                self.send(json.dumps({'audioContent': ''}))
        Thread(target=run).start()

    def closed(self, code, reason=None):
        print('')

    def received_message(self, m):
        try:
            response = json.loads(m.data.decode('utf-8'))
            transcript = response['result']['results'][0]['alternatives'][0]['transcript']
            result_index = response['result'].get('resultIndex', 0)
            is_final = response['result']['results'][0].get('isFinal', False)
            self.transcripts[result_index] = transcript
        except KeyError as e:
            pass

        print('\r{}'.format(''.join(val for key, val in self.transcripts.items())),
              end='', flush=True)


def parse_args():
    po = ArgumentParser(
        description="""Example usage of the Speech::StreamingRecognize API.  Set
        the environment variable TALA_API_KEY to the API key you generated at
        https://tal.ru.is/stjori
        """,
        formatter_class=ArgumentDefaultsHelpFormatter)
    po.add_argument('--uri',
                    default='wss://tal.ru.is/v1/speech:streamingrecognize',
                    help='URI of Speech::StreamingRecognize API endpoint.')
    po.add_argument('wav_path', type=str, help='WAV file to recognize.')
    args = po.parse_args()
    args.api_key = os.environ['TALA_API_KEY']

    return args


def main(args):
    try:
        ws = StreamingRecognizeClient(
            args.wav_path, '{}?token={}'.format(args.uri, args.api_key))
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()


if __name__ == '__main__':
    args = parse_args()
    main(args)
