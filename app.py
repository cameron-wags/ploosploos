#! /usr/bin/env python3
import os
import json

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return 'Sic \'em Bears!'

@app.route('/something_stupid', methods=['POST'])
def main_thingy():
    thing = json.loads(request.data)

    if 'challenge' in thing:
        print(thing)
        return jsonify({'challenge': thing['challenge']})

    print(thing)
    return ''

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app.run('0.0.0.0', port=port, debug=True)
