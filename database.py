from __main__ import app
from flask import Flask, redirect, url_for, request, abort
import threading
import sqlite3
import database_utils
import os
import time

database_path = "./database.db"
vid_path_prefix = "./assets"

# Initialize Database
def setup_app(app):
  with sqlite3.connect(database_path) as conn:
    database_utils.init(conn)

setup_app(app)

# Get Fragment Video 
# will be deprecated once sftp starts working
@app.route('/api/v1/assets/<frag>', methods=['GET'])
def get_frag(frag):
  try:
    with open(os.path.join(vid_path_prefix, frag), 'rb') as f:
      return f.read()
  except Exception as e:
    return "Frag Doesn't Exist"
  # return str(sorted(os.listdir(vid_path_prefix)))

def fetch_frag(content):
  feed = content["foliage_feed"]
  vid_name = "frag%s.mp4" % round(time.time())
  frag_path = os.path.join(vid_path_prefix, vid_name)
  with open(frag_path, "wb") as f:
    vid = bytes.fromhex(feed)
    f.write(vid)
  for path in sorted([path for path in os.listdir(vid_path_prefix) if '.mp4' in path])[:-2]:
    os.remove(os.path.join(vid_path_prefix, path))
  return vid_name

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
    content["foliage_feed"] = fetch_frag(content) # Key to access vid on filesystem
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
