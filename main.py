from flask import Flask, redirect, url_for, request, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import sqlite3
import pandas as pd
import utils

database_path = "./database.db"
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
cors = CORS(app, resources={r"/*": {"origins": "*"}})
lock = threading.Lock()
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["300 per minute"]
)

def setup_app(app):
    with sqlite3.connect(database_path) as conn:
        utils.init(conn)
setup_app(app)

@app.route('/get/', methods=['GET'])
def get():
    with sqlite3.connect(database_path) as conn:
        key = request.args.get('key')
        j = utils.get(conn, key)
        if j == {}:
            return {"success":False,"cause": "Invalid key"},400
        return {"success":True,"data": j}

@app.route('/set/', methods=['POST'])
def update():
    with sqlite3.connect(database_path) as conn:
        content = utils.isolate_updatable(request.get_json())
        if "key" not in content:
            return {"success":False,"cause": "Missing one or more fields: [key]"},400
        if len(content) < 2:
            return {"success":False,"cause": "Couldn't update any fields"},400
        d = utils.update(conn,content)
        if d is not None:
            return d
        return redirect(url_for('home'))

@app.route('/', methods=['GET'])
def home():
    return ""

@app.errorhandler(404)
def fallback(_):
    return {"success":False, "cause": "The specified URI was not found on this server"},404
    
if __name__ == "__main__":
    app.run()
