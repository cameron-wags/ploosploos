#! /usr/bin/env python3
import os
from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    return 'Sic \'em Bears!'

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app.run('0.0.0.0', port=port, debug=True)
