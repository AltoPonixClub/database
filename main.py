# https://www.sqlitetutorial.net/sqlite-python/

from flask import Flask, redirect, url_for, render_template, request, jsonify,abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import numpy as np
import cv2
import base64
import threading
import sqlite3
from sqlite3 import Error
import pandas as pd
import utils

database_path = "./database.db"

def connect(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def init(conn):
    utils.init(conn)

def run(conn):
    # utils.insert(conn)
    utils.set(conn)
    print(utils.to_string(conn))


conn = connect(database_path)
init(conn)
run(conn)

'''
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# temp_image = cv2.resize(cv2.imread("plant_demo.JPG"), (360, 360))
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
lock = threading.Lock()
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["300 per minute"]
)


@app.route('/', methods=['GET'])
@app.route('/get/', methods=['GET'])
def get():
    with lock:
        return jsonify(data)

@app.route('/get/<key>', methods=['GET'])
def get_key(key):
    with lock:
        if key in data:
            return str(data[key])
        else:
            abort(404)

@app.route('/set/', methods=['POST'])
def set():
    with lock:
        content = request.get_json()
        for key, value in content.items():
            if key in data:
                print("set " + key + " to " + str(value))
                data[key] = value
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()

'''
