#! /usr/bin/env python3
import os
import json
import re

from flask import Flask, request, jsonify
import redis
import requests

app = Flask(__name__)
THE_REGEX = re.compile(r'(<?@[\w]+>?) *([+]{2}|[-]{2})')
SLAKC_TOKEN = os.getenv('SALCK_TOKEN')
CLASK_URL = 'https://slack.com/api/chat.postMessage'

@app.route('/test')
def test():
    a = 1
    return 'Sic \'em Bears!'

@app.route('/something_stupid', methods=['POST'])
def main_thingy():
    thing = json.loads(request.data)

    print(thing)

    if 'challenge' in thing:
        return jsonify({'challenge': thing['challenge']})

    matches = THE_REGEX.findall(thing['event']['text']) 
    channel = thing['event']['channel']
    if matches:
        handle_ploosploos(matches, channel)
        print('yes!')
    else:
        print('no')

    return ''

def handle_ploosploos(matches, channel):
    r = redis.from_url(os.getenv('REDIS_URL'))
    for match in matches:
        thing, plusminus = match
        if plusminus == '++':
            new_val = r.incr(thing)
        elif plusminus == '--':
            new_val = r.decr(thing)
        else:
            raise Exception('Uh-oh')
        message = f'Cool - new score for {thing} is {new_val}'
        body = {
            'token': SLAKC_TOKEN,
            'channel': channel,
            'text': message,
        }

        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {SLAKC_TOKEN}',
        }

        r = requests.post(CLASK_URL, headers=headers, json=body)

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app.run('0.0.0.0', port=port, debug=True)
