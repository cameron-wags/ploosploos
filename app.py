#! /usr/bin/env python3
import os
import json
import re

from flask import Flask, request, jsonify

app = Flask(__name__)
THE_REGEX = re.compile(r'@(\w)+ *([+]{2}|[-]{2})')

@app.route('/test')
def test():
    return 'Sic \'em Bears!'

@app.route('/something_stupid', methods=['POST'])
def main_thingy():
    thing = json.loads(request.data)

    print(thing)

    if 'challenge' in thing:
        return jsonify({'challenge': thing['challenge']})

    if THE_REGEX.findall(thing['text']):
        print('yes!')

    return ''

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app.run('0.0.0.0', port=port, debug=True)
