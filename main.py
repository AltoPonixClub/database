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

@app.route('/api/v1/monitors/get', methods=['GET'])
def get_monitor():
    with sqlite3.connect(database_path) as conn:
        monitor_id = request.args.get('monitor_id')
        j = utils.get_monitors(conn, monitor_id)
        if j == {}:
            return {"success": False, "cause": "Invalid monitor_id"}, 400
        return {"success": True, "data": j}


@app.route('/api/v1/monitors/update', methods=['POST'])
def update_monitor():
    with sqlite3.connect(database_path) as conn:
        content = utils.isolate_updatable(request.get_json())
        if "id" not in content or content["id"] == None:
            return {"success": False, "cause": "Missing one or more fields: [id]"}, 400
        if len(content) < 2:
            return {"success": False, "cause": "Couldn't update any fields"}, 400
        d = utils.update_monitor(conn, content)
        if d is not None:
            return d
        return redirect(url_for('home'))


@app.route('/api/v1/monitors/add', methods=['POST'])
def add_monitor():
    with sqlite3.connect(database_path) as conn:
        content = request.get_json()
        if "user_id" not in content or content["user_id"] == None:
            return {"success": False,
                    "cause": "Missing one or more fields: [user_id]"}, 400
        if "monitor_id" not in content or content["monitor_id"] == None:
            return {"success": False,
                    "cause": "Missing one or more fields: [monitor_id]"}, 400
        d = utils.add_monitor(conn, (content["monitor_id"],content["user_id"]))
        if d is not None:
            return d
        return redirect(url_for('home'))

@app.route('/api/v1/monitors/reset', methods=['POST'])
def reset_monitor():
    with sqlite3.connect(database_path) as conn:
        content = request.get_json()
        if "monitor_id" not in content or content["monitor_id"] == None:
            return {"success": False,
                    "cause": "Missing one or more fields: [monitor_id]"}, 400
        d = utils.reset_monitor(conn,content["monitor_id"])
        if d is not None:
            return d
        return redirect(url_for('home'))

@app.route('/api/v1/monitors/delete', methods=['POST'])
def delete_monitor():
    with sqlite3.connect(database_path) as conn:
        content = request.get_json()
        if "monitor_id" not in content or content["monitor_id"] == None:
            return {"success": False,
                    "cause": "Missing one or more fields: [monitor_id]"}, 400
        d = utils.delete_monitor(conn,content["monitor_id"])
        if d is not None:
            return d
        return redirect(url_for('home'))

@app.route('/api/v1/users/monitors/get', methods=['GET'])
def get_user():
    with sqlite3.connect(database_path) as conn:
        user_id = request.args.get('user_id')
        j = utils.get_users(conn, user_id)
        if j == {}:
            return {"success": False, "cause": "Invalid user_id"}, 400
        return {"success": True, "data": j}

@app.route('/', methods=['GET'])
def home():
    return ""

@app.errorhandler(404)
def fallback(_):
    return {"success": False,
            "cause": "The specified URI was not found on this server"}, 404


if __name__ == "__main__":
    app.run()
