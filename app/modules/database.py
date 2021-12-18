from .. import app
from . import database_utils
from flask import redirect, url_for, request
import threading
import sqlite3
import os
import time

database_path = "./database.db"
vid_path_prefix = "./assets"

# Initialize Database
def setup_app(app):
  with sqlite3.connect(database_path) as conn:
    database_utils.init(conn)

setup_app(app)

@app.route('/api/v1/monitors/get', methods=['GET'])
def get_monitor():
  with sqlite3.connect(database_path) as conn:
    monitor_id = request.args.get('monitor_id')
    data = database_utils.get_monitors(conn, monitor_id)
    if data == {}:
      return {"success": False, "cause": "Invalid monitor_id"}, 400
    return {"success": True, "data": data}

@app.route('/api/v1/monitors/update', methods=['POST'])
def update_monitor():
  with sqlite3.connect(database_path) as conn:
    content = database_utils.isolate_updatable(request.get_json())
    if "id" not in content or content["id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [id]"}, 400
    if len(content) < 2:
      return {"success": False, "cause": "Couldn't update any fields"}, 400
    data = database_utils.update_monitor(conn, content)
    if data is not None:
      return data
    return redirect(url_for('home'))

@app.route('/api/v1/monitors/add', methods=['POST'])
def add_monitor():
  with sqlite3.connect(database_path) as conn:
    content = request.get_json()
    if "user_id" not in content or content["user_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [user_id]"}, 400
    if "monitor_id" not in content or content["monitor_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    d = database_utils.add_monitor(
      conn, (content["monitor_id"], content["user_id"]))
    if d is not None:
      return d
    return redirect(url_for('home'))

@app.route('/api/v1/monitors/reset', methods=['POST'])
def reset_monitor():
  with sqlite3.connect(database_path) as conn:
    content = request.get_json()
    if "monitor_id" not in content or content["monitor_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    d = database_utils.reset_monitor(conn, content["monitor_id"])
    if d is not None:
        return d
    return redirect(url_for('home'))

@app.route('/api/v1/monitors/delete', methods=['POST'])
def delete_monitor():
  with sqlite3.connect(database_path) as conn:
    content = request.get_json()
    if "monitor_id" not in content or content["monitor_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    d = database_utils.delete_monitor(conn, content["monitor_id"])
    if d is not None:
      return d
    return redirect(url_for('home'))

@app.route('/api/v1/owners/get', methods=['GET'])
def get_owners():
  with sqlite3.connect(database_path) as conn:
    user_id = request.args.get('user_id')
    j = database_utils.get_owners(conn, user_id)
    if j == {}:
      return {"success": False, "cause": "Invalid user_id"}, 400
    return {"success": True, "data": j}
