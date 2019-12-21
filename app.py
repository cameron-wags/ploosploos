#! /usr/bin/env python3
import os
import json
import re
from threading import Thread, Lock

from flask import Flask, request, jsonify
import redis
import requests
import random

app = Flask(__name__)
THE_REGEX = re.compile(r'(<?@[\w:+-]+>?) *([+]{2}|[-]{2})')
# Maybe don't hardcode the bot's id later on
LEADERBROAD_REXEG = re.compile(r'(<@UDPR09T7E>|ploosploos) *(scores?|leaderboard|count|top|list) *(-?\d+)?', flags=re.IGNORECASE)
SLAKC_TOKEN = os.getenv('SALCK_TOKEN')
CLASK_URL = 'https://slack.com/api/chat.postMessage'
# It actually doesn't matter if someone ++'s this, they'd have to be fast.
SOMETHING_NO_ONE_WILL_EVER_SAY = 'last_event_id'
pp_lock = Lock()

@app.route('/test')
def test():
    return 'Sic \'em Bears!'

@app.route('/something_stupid', methods=['POST'])
def main_thingy():
    thing = json.loads(request.data)

    print(thing)

    if 'challenge' in thing:
        return jsonify({'challenge': thing['challenge']})

    matches = THE_REGEX.findall(thing['event']['text']) 
    channel = thing['event']['channel']
    msg_id = thing['event']['client_msg_id']
    if matches:
        t = Thread(group=None, target=handle_ploosploos, args=(matches, channel, msg_id))
        t.start()
        print('yes!')
    else:
        scoreMatch = LEADERBROAD_REXEG.match(thing['event']['text'])
        if scoreMatch:
            t = Thread(group=None, target=handle_leaderboard, args=(scoreMatch, channel, msg_id))
            t.start()
            print('leaderboard!')
        else:
            print('no')

    return ''

def handle_leaderboard(match, channel, msg_id):
    r = redis.from_url(os.getenv('REDIS_URL'))

    if msg_id == str(r.get(SOMETHING_NO_ONE_WILL_EVER_SAY), encoding='utf8'):
        return
    r.set(SOMETHING_NO_ONE_WILL_EVER_SAY, msg_id)

    # this is a bad idea
    keys = [ str(key, encoding='utf8') for key in r.keys() ]
    keys.remove(SOMETHING_NO_ONE_WILL_EVER_SAY)
    print(keys)

    requested_count = int(match.group(3)) if match.lastindex == 3 else 5
    top = requested_count > 0
    count = abs(requested_count) if abs(requested_count) <= len(keys) else keys.count


    pairs = { key:int(str(r.get(key), encoding='utf8')) for key in keys }
    print(pairs)

    if count == 0:
        message = f'{uncool_synonym().capitalize()}!'
    else:
        high_low = 'Top' if top else 'Bottom'
        message = f'{cool_synonym().capitalize()}! {high_low} *{count}* scores:\n'

    for key in sorted(pairs, key=pairs.get, reverse=top)[:count]:
        message += f'{key}: *{pairs[key]}*\n'
        print(f'{key} -> {pairs[key]}')

    body = {
            'token': SLAKC_TOKEN,
            'channel': channel,
            'text': message,
    }

    headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {SLAKC_TOKEN}',
    }

    response = requests.post(CLASK_URL, headers=headers, json=body)
    response.raise_for_status()


def handle_ploosploos(matches, channel, msg_id):
    global pp_lock

    pp_lock.acquire()
    r = redis.from_url(os.getenv('REDIS_URL'))

    if msg_id == str(r.get(SOMETHING_NO_ONE_WILL_EVER_SAY), encoding='utf8'):
        pp_lock.release()
        return
    r.set(SOMETHING_NO_ONE_WILL_EVER_SAY, msg_id)
    pp_lock.release()

    for match in matches:
        thing, plusminus = match
        if thing.startswith('@'):
            thing = thing.lstrip('@')

        print(f'do a {plusminus} on {thing}')
        if plusminus == '++':
            new_val = r.incr(thing)
            word = cool_synonym()
        elif plusminus == '--':
            new_val = r.decr(thing)
            word = uncool_synonym()
        else:
            raise Exception('Uh-oh')

        message = f'{word.capitalize()}! New score for {thing} is {new_val}.'
        body = {
            'token': SLAKC_TOKEN,
            'channel': channel,
            'text': message,
        }

        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {SLAKC_TOKEN}',
        }

        response = requests.post(CLASK_URL, headers=headers, json=body)
        response.raise_for_status()

def cool_synonym():
    return random.choice(['Acceptable', 'Cool', 'excellent', 'exceptional', 'favorable', 'great', 'marvelous', 'positive', 'satisfactory', 'satisfying', 'superb', 'valuable', 'wonderful', 'ace', 'boss', 'bully', 'capital', 'choice', 'crack', 'nice', 'pleasing', 'prime', 'rad', 'sound', 'spanking', 'sterling', 'super', 'superior', 'welcome', 'worthy', 'admirable', 'agreeable', 'commendable', 'congenial', 'deluxe', 'first-class', 'first-rate', 'gnarly', 'gratifying', 'honorable', 'neat', 'precious', 'recherché', 'reputable', 'select', 'shipshape', 'splendid', 'stupendous', 'super-eminent', 'super-excellent', 'tip-top', 'up to snuff'])

def uncool_synonym():
    return random.choice(['abhorrent', 'abominable', 'beastly', 'bitchy', 'creepy', 'deplorable', 'detestable', 'disgusting', 'execrable', 'gross', 'hideous', 'horrible', 'invidious', 'lousy', 'nasty', 'nauseating', 'obnoxious', 'odious', 'offensive', 'pesky', 'pestiferous', 'repellent', 'repugnant', 'repulsive', 'revolting', 'sleazy', 'slimy', 'uncool', 'vile'])

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app.run('0.0.0.0', port=port, debug=True)
