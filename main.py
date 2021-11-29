from flask import Flask, redirect, url_for, request, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import sqlite3
import pandas as pd
import utils
import os
import time

database_path = "./database.db"
vid_path_prefix = "./assets"
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
app.config['JSON_SORT_KEYS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
lock = threading.Lock()
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["300 per minute"]
)

clients = {}
devices = {}
monitordevice = {}

def setup_app(app):
    with sqlite3.connect(database_path) as conn:
        utils.init(conn)

setup_app(app)

@app.route('/api/v1/assets/<frag>', methods=['GET'])
def get_frag(frag):
    try:
        with open(os.path.join(vid_path_prefix, frag), 'rb') as f:
            return f.read()
    except Exception as e:
        return "Frag Doesn't Exist"

    # return str(sorted(os.listdir(vid_path_prefix)))

@app.route('/api/v1/monitors/get', methods=['GET'])
def get_monitor():
    with sqlite3.connect(database_path) as conn:
        monitor_id = request.args.get('monitor_id')
        j = utils.get_monitors(conn, monitor_id)
        if j == {}:
            return {"success": False, "cause": "Invalid monitor_id"}, 400
        return {"success": True, "data": j}

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


@app.route('/api/v1/monitors/update', methods=['POST'])
def update_monitor():
    with sqlite3.connect(database_path) as conn:
        content = utils.isolate_updatable(request.get_json())
        content["foliage_feed"] = fetch_frag(content) # Key to access vid on filesystem
        if "id" not in content or content["id"] is None:
            return {"success": False,
                    "cause": "Missing one or more fields: [id]"}, 400
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
        if "user_id" not in content or content["user_id"] is None:
            return {"success": False,
                    "cause": "Missing one or more fields: [user_id]"}, 400
        if "monitor_id" not in content or content["monitor_id"] is None:
            return {"success": False,
                    "cause": "Missing one or more fields: [monitor_id]"}, 400
        d = utils.add_monitor(
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
        d = utils.reset_monitor(conn, content["monitor_id"])
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
        d = utils.delete_monitor(conn, content["monitor_id"])
        if d is not None:
            return d
        return redirect(url_for('home'))


@app.route('/api/v1/owners/get', methods=['GET'])
def get_owners():
    with sqlite3.connect(database_path) as conn:
        user_id = request.args.get('user_id')
        j = utils.get_owners(conn, user_id)
        if j == {}:
            return {"success": False, "cause": "Invalid user_id"}, 400
        return {"success": True, "data": j}

@app.route('/', methods=['GET'])
def home():
  return 200

@socketio.on('query')                    
def query(content):      
  if "monitor_id" not in content or content["monitor_id"] is None or type(content["monitor_id"]) != str or len(content["monitor_id"]) != 32:
    emit('query failed', {'reason': 'Invalid monitor_id'}, room=request.sid) 
    return
  clients[request.sid] = content["monitor_id"]
  emit('query ok', {'reason': 'Query ok'}, room=request.sid) 

@socketio.on('con')                    
def query(content):      
  if "monitor_id" not in content or content["monitor_id"] is None or type(content["monitor_id"]) != str or len(content["monitor_id"]) != 32:
    emit('con failed', {'reason': 'Invalid monitor_id'}, room=request.sid) 
    return
  if content["monitor_id"] in monitordevice:
    emit('con failed', {'reason': 'monitor_id already registered'}, room=request.sid) 
    return
  devices[request.sid] = content["monitor_id"]
  monitordevice[content["monitor_id"]] = True
  emit('con ok', {'reason': 'Connection ok'}, room=request.sid) 

@socketio.on('command send')                    
def send(content):      
  if "command" not in content or content["command"] is None or type(content["command"]) != str or len(content["command"]) == 0:
    emit('command failed', {'reason': 'Invalid command'}, room=request.sid) 
    return
  if clients[request.sid] in monitordevice:
    for sid, m in devices.items():
      if m == clients[request.sid]:
        emit('command do', {'command': content["command"]}, room=sid) 
  emit('command ok', {'reason': 'Command ok'}, room=request.sid) 


@socketio.on('command done')                    
def done(content):
  for sid, m in clients.items():
    if m == devices[request.sid]:
      emit('command finish', {'reason': 'Command finish'}, room=sid) 

@socketio.on('command error')                    
def done(content):
  for sid, m in clients.items():
    if m == clients[request.sid]:
      emit('command failed', {'reason': content.reason}, room=sid) 

@socketio.on('disconnect')  
def handle_disc():
  if request.sid in devices:
    mon = devices[request.sid]
    monitordevice.pop(mon, None)
  clients.pop(request.sid, None)
  devices.pop(request.sid, None)

@app.errorhandler(404)
def fallback(_):
  return {"success": False,
          "cause": "The specified URI was not found on this server"}, 404


if __name__ == "__main__":
   socketio.run(app)

