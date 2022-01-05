from .. import app
from flask import request
from pymongo import MongoClient
from argon2 import PasswordHasher
import os
import time
import certifi
import random
import copy

# Documentation for the API is located in apidocs.md!

# Token TTL: how long until a token expires (ms)
TOKEN_MAX_AGE = 1000 * 60 * 60 * 4

# Update typing checks
TYPINGS = {
  'atmospheric_temp': float,
  'reservoir_temp': float,
  'light_intensity': float,
  'soil_moisture': float,
  'electrical_conductivity': float,
  'ph': float,
  'dissolved_oxygen': float,
  'air_flow': float,
  'foliage_feed': str,
  'root_stream': str,
}

# Password Validater
ph = PasswordHasher()

# Sessions
sessions = {}
sessions_monitors = {}

# Connect to MongoDB
client = MongoClient("mongodb+srv://altoponix-db:" + os.environ['DB_PSWD'] + "@altoponix.nej4q.mongodb.net", tlsCAFile=certifi.where())
db = client.database
monitors = db.get_collection("monitors")
users = db.get_collection("users")

# Helper functions

# ALL IDS SHOULD BE 32 CHARS LONG, AND IN HEX FORMAT
def isValidID(id):
  return not (id is None or not isinstance(id,str) or len(id) != 32 or not id.isalnum())

# Generate a hexadecimal string of a given lenght
def generateToken(length):
  ALPHABET = "0123456789abcdef"
  chars = ""
  for _ in range(length):
    chars = chars + random.choice(ALPHABET)
  while (chars in sessions or len([v for v in sessions_monitors if v["token"] == chars]) > 0):
    chars = ""
    for _ in range(length):
      chars = chars + random.choice(ALPHABET)
  return chars

def getUserCredentials(token, request):
  if token == "" or token is None or token not in sessions:
    return ""
  if round(time.time() * 1000) > sessions[token]["expire_date"] or sessions[token]["ip"] != request.remote_addr:
    return ""
  for doc in users.find({"user_id": {'$eq': sessions[token]["user_id"]}}, {"_id": 0}):
    return doc["type"]
  return ""

def getMonitorCredentials(token, monitor_id, request):
  if token == "" or token is None or monitor_id not in sessions_monitors:
    return False
  if round(time.time() * 1000) > sessions_monitors[monitor_id]["expire_date"] or sessions_monitors[monitor_id]["ip"] != request.remote_addr:
    return False
  return True


# LOGIN METHODS
@app.route('/api/v1/login/user', methods=['POST'])
def request_login_user():
  try:
    args = request.get_json()
    # Safety Checking
    if "username" not in args or args["username"] is None or args["username"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [username]"}, 400
    if "password" not in args or args["password"] is None or args["password"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [password]"}, 400
    # Get the hash associated with the username
    for doc in users.find({"username": {'$eq': args["username"]}},{"_id": 0}):
      # Check if the password matches the hash
      try:
        ph.verify(doc["hash"], args["password"])
      except:
        return {"success": False, "cause": "Invalid Credentials"}, 401
      # Generate token
      token = generateToken(32)
      sessions[token] = {
        "user_id": doc["user_id"],
        "expire_date": round(time.time() * 1000) + TOKEN_MAX_AGE,
        "ip": request.remote_addr
      }
      return {"success": True, "data": {"token": token, "username": doc["username"], "user_id": doc["user_id"]}}
    return {"success": False, "cause": "Invalid Credentials"}, 401
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/login/monitor', methods=['POST'])
def request_login_monitor():
  try:
    args = request.get_json()
    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None or args["monitor_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    if "password" not in args or args["password"] is None or args["password"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [password]"}, 400
    # Get the has associated with the monitor_id
    for doc in monitors.find({"monitor_id": {'$eq': args["monitor_id"]}},{"_id": 0}):
      # Check if the password matches the hash
      try:
        ph.verify(doc["hash"], args["password"])
      except:
        return {"success": False, "cause": "Invalid Credentials"}, 401
      # Generate token
      token = generateToken(32)
      sessions_monitors[args["monitor_id"]] = {
        "token": token,
        "expire_date": round(time.time() * 1000) + TOKEN_MAX_AGE,
        "ip": request.remote_addr
      }
      return {"success": True, "data": {"token": token}}
    return {"success": False, "cause": "Invalid Credentials"}, 401
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

# MONITOR METHODS
@app.route('/api/v1/monitors/get', methods=['GET'])
def get_monitor():
  try: 
    # Safety Checking
    if request.args.get("token") == "" or request.args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(request.args.get("token"), request)
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401
      
    # Argument processing
    startTime = request.args.get("startTime")
    endTime = request.args.get("endTime")
    if isinstance(startTime, str) and not startTime.isnumeric():
      startTime = None
    if isinstance(endTime, str) and not endTime.isnumeric():
      endTime = None
    # Return all monitors if monitor_id isn't provided
    if request.args.get('monitor_id') is None:
      if creds == "user":
        return {"success": False, "cause": "Forbidden"}, 403
      dat = {}
      for doc in monitors.find({}, {"_id": 0, "hash": 0}):
        if startTime is not None or endTime is not None:
          if startTime is None: 
            startTime = 0
          if endTime is None: 
            endTime = 9999999999999
          for key in doc.keys():
            if not isinstance(doc[key], dict):
              continue
            doc[key] = ({k: v for k,v in doc[key]["history"].items() if int(k) > int(startTime) and int(k) < int(endTime)})
        dat[doc["monitor_id"]] = doc
        doc.pop("monitor_id", None)
      return {"success": True, "data": dat}
    # If monitor_id is provided, get the monitor
    if not isValidID(request.args.get('monitor_id')):
      return {"success": False, "cause": "Invalid monitor_id"}, 400
    data = monitors.find({"monitor_id": {'$eq': request.args.get('monitor_id')}}, {"_id": 0, "monitor_id": 0, "hash": 0})
    for doc in data:
      # Check credentials
      if creds == "user" and doc["owner"] != sessions[request.args.get("token")]["user_id"]:
        return {"success": False, "cause": "Forbidden"}, 403
      doc.pop('owner', None)
      return {"success": True, "data": doc}
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/monitors/update', methods=['POST'])
def update_monitor():
  try:
    args = request.get_json()
    # Get the current time
    t = round(time.time() * 1000)
    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None or args["monitor_id"] == "":
      return {"success": False,
            "cause": "Missing one or more fields: [monitor_id]"}, 400
    if not isValidID(args["monitor_id"]):
      return {"success": False, "cause": "Invalid monitor_id"}, 400

    # Credential Check
    if args.get("token") == "" or args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getMonitorCredentials(args.get("token"), args.get("monitor_id"), request)
    if getUserCredentials(args.get("token"), request) != "admin":
      if not creds:
        return {"success": False, "cause": "Invalid token"}, 401
      if sessions_monitors[args.get("monitor_id")]["token"] != args.get("token"):
        return {"success": False, "cause": "Forbidden"}, 403

    for doc in monitors.find({"monitor_id": {'$eq': args["monitor_id"]}}, {"_id": 0, "monitor_id": 0, "owner": 0}):
      upd = {}
      keys = doc.keys()
      # For every value to update
      for arg in args.items():
        arg = list(arg)
        # Is the value empty?
        if arg[1] is None or arg[1] == "":
          continue
        # Is the key a valid key?
        if arg[0] not in TYPINGS: 
          continue
        # Convert numbers to float to fix TYPINGS
        if isinstance(arg[1], int):
          arg[1] = float(arg[1])
        # If the type check fails, do not update
        if not isinstance(arg[1],TYPINGS[arg[0]]):
          continue
        # Update the value
        curval = doc[arg[0]]
        if isinstance(curval, dict):
          curval["value"] = arg[1]
          curval["history"][str(t)] = arg[1]
          upd[arg[0]] = curval
        else:
          upd[arg[0]] = arg[1]
      if upd == {}:
        return {"success": False, "cause": "Couldn't update any measurements"}, 400
      else:
        monitors.update_one({"monitor_id": {'$eq': args["monitor_id"]}}, {"$set": upd})
      return {"success": True}
    # If monitor_id isn't found
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/monitors/add', methods=['POST'])
def add_monitor():
  try:
    args = request.get_json()

    # Credential Check
    if args.get("token") == "" or args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(args.get("token"), request)
    if creds == "user":
      return {"success": False, "cause": "Forbidden"}, 403
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401

    # Safety Checking
    if "user_id" not in args or args["user_id"] is None or args["user_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [user_id]"}, 400
    if "monitor_id" not in args or args["monitor_id"] is None or args["monitor_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    if "password" not in args or args["password"] is None or args["password"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [password]"}, 400
    if not isValidID(args["user_id"]):
      return {"success": False,
              "cause": "Invalid user_id"}, 400
    if not isValidID(args["monitor_id"]):
      return {"success": False,
              "cause": "Invalid monitor_id"}, 400
    if monitors.count_documents({"monitor_id": {'$eq': args["monitor_id"]}}) > 0:
      return {"success": False,
              "cause": "Duplicate monitor_id"}, 400
    
    for doc in users.find({"user_id": {'$eq': args["user_id"]}}, {"_id": 0, "user_id": 0}):
      monitors.insert_one({
        "atmospheric_temp": {"value": None, "history": {}},
        "reservoir_temp": {"value": None, "history": {}},
        "light_intensity": {"value": None, "history": {}},
        "soil_moisture": {"value": None, "history": {}},
        "electrical_conductivity": {"value": None, "history": {}},
        "ph": {"value": None, "history": {}},
        "dissolved_oxygen": {"value": None, "history": {}},
        "air_flow": {"value": None, "history": {}},
        "foliage_feed": "",
        "root_stream": "",
        "monitor_id": args["monitor_id"],
        "owner": args["user_id"], 
        "hash": ph.hash(args["password"])
      })
      dat = doc['monitor_ids']
      dat.append(args["monitor_id"])
      users.update_one({"user_id": {'$eq': args["user_id"]}}, {"$set": {"monitor_ids": dat}})
      return {"success": True}
    # If user isn't found
    return {"success": False, "cause": "Invalid user_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/monitors/reset', methods=['POST'])
def reset_monitor():
  try:
    args = request.get_json()

    # Credential Check
    if args.get("token") == "" or args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(args.get("token"), request)
    if creds == "user":
      return {"success": False, "cause": "Forbidden"}, 403
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401

    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None or args["monitor_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    if not isValidID(args["monitor_id"]):
      return {"success": False,
              "cause": "Invalid monitor_id"}, 400

    result = monitors.update_one({"monitor_id": {'$eq': args["monitor_id"]}}, {"$set": {
      "atmospheric_temp": {"value": None, "history": {}},
      "reservoir_temp": {"value": None, "history": {}},
      "light_intensity": {"value": None, "history": {}},
      "soil_moisture": {"value": None, "history": {}},
      "electrical_conductivity": {"value": None, "history": {}},
      "ph": {"value": None, "history": {}},
      "dissolved_oxygen": {"value": None, "history": {}},
      "air_flow": {"value": None, "history": {}},
      "foliage_feed": "",
      "root_stream": "",
    }})
    # If monitor isn't found
    if result.modified_count == 1:
      return {"success": True}
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/monitors/delete', methods=['POST'])
def delete_monitor():
  try:
    args = request.get_json()

    # Credential Check
    if args.get("token") == "" or args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(args.get("token"), request)
    if creds == "user":
      return {"success": False, "cause": "Forbidden"}, 403
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401

    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None or args["monitor_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
    if not isValidID(args["monitor_id"]):
      return {"success": False,
              "cause": "Invalid monitor_id"}, 400
    for doc in monitors.find({"monitor_id": {'$eq': args["monitor_id"]}}, {"_id": 0, "monitor_id": 0}):
      # Get the owner given the monitor (hidden tag)
      owner_id = doc["owner"]
      # If the owner id associated with the monitor is invalid somehow????? then abort
      if owner_id is None or not isValidID(owner_id):
        return {"success": False, "cause": "An unkown error occured."}, 500
      # Find the owner record with the owner_id
      for user in users.find({"user_id": {'$eq': owner_id}}):
        # Delete
        ids = user["monitor_ids"]
        ids.remove(args["monitor_id"])
        monitors.delete_one({"monitor_id": {'$eq': args["monitor_id"]}})
        users.update_one({"user_id": {'$eq': owner_id}}, {"$set": {"monitor_ids": ids}})
        return {"success": True}
      # If the owner record wasn't found???? (shouldn't happen)
      return {"success": False, "cause": "An unkown error occured."}, 500
    # If monitor isn't found
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

# USER METHODS
@app.route('/api/v1/owners/get', methods=['GET'])
def get_users():
  try:
    # Credential Check
    if request.args.get("token") == "" or request.args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(request.args.get("token"), request)
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401
    user_id = request.args.get('user_id')
    if creds == "user" and user_id != sessions[request.args.get("token")]["user_id"]:
      return {"success": False, "cause": "Forbidden"}, 403

    # Return all users if user_id isn't given
    if user_id is None:
      # Credential Check
      if creds == "user":
        return {"success": False, "cause": "Forbidden"}, 403
      dat = {}
      data = users.find({}, {"_id": 0, "hash": 0})
      for doc in data:
        dat[doc["user_id"]] = doc
        doc.pop("user_id", None)
      return {"success": True, "data": dat}
    
    # If user_id is given, return the user's data
    if not isValidID(user_id):
      return {"success": False,
              "cause": "Invalid user_id"}, 400
    for doc in users.find({"user_id": {'$eq': user_id}},{"_id": 0, "user_id": 0, "hash": 0}):
      return {"success": True, "data": doc}
    return {"success": False, "cause": "Invalid user_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

@app.route('/api/v1/owners/resetpassword', methods=['POST'])
def reset_user_password():
  try:
    args = request.get_json()

    # Credential Check
    if args.get("token") == "" or args.get("token") is None:
      return {"success": False, "cause": "Missing one or more fields: [token]"}, 400
    creds = getUserCredentials(args.get("token"), request)
    if creds == "":
      return {"success": False, "cause": "Invalid token"}, 401

    # Safety Checking
    if "user_id" not in args or args["user_id"] is None or args["user_id"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [user_id]"}, 400
    if creds != "admin" and ("old_password" not in args or args["old_password"] is None or args["old_password"] == ""):
      return {"success": False,
              "cause": "Missing one or more fields: [old_password]"}, 400
    if "new_password" not in args or args["new_password"] is None or args["new_password"] == "":
      return {"success": False,
              "cause": "Missing one or more fields: [new_password]"}, 400
    if not isValidID(args["user_id"]):
      return {"success": False,
              "cause": "Invalid user_id"}, 400

    if creds == "user" and args.get("user_id") != sessions[args.get("token")]["user_id"]:
      return {"success": False, "cause": "Forbidden"}, 403

    for doc in users.find({"user_id": {'$eq': args["user_id"]}}, {"_id": 0, "user_id": 0}):
      if creds != "admin":
        try:
          ph.verify(doc["hash"], args["old_password"])
        except:
          return {"success": False, "cause": "Invalid Credentials"}, 401
      users.update_one({"user_id": {'$eq': args["user_id"]}}, {"$set": {"hash": ph.hash(args["new_password"])}})
      # Log out any sessions related to that user
      for session in copy.deepcopy(sessions):
        if sessions[session]["user_id"] == args["user_id"]:
            sessions.pop(session, None)
      return {"success": True}
    # If user isn't found
    return {"success": False, "cause": "Invalid Credentials"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "An unexpected error occured"}, 500

# Disabled for now
# @app.route('/api/v1/owners/add', methods=['POST'])
# def add_owner():
#   try: 
#     args = request.get_json()
#     if "user_id" not in args or args["user_id"] is None:
#       return {"success": False,
#               "cause": "Missing one or more fields: [user_id]"}, 400
#     if not isValidID(args["user_id"]):
#       return {"success": False,
#               "cause": "Invalid user_id"}, 400
#     if users.count_documents({"user_id": {'$eq': args["user_id"]}}) > 0:
#       return {"success": False,
#               "cause": "Duplicate user_id"}, 400
#     users.insert_one({
#       "user_id": args["user_id"],
#       "monitor_ids": []
#     })
#     return {"success": True}
#   except Exception as e:
#     print(e)
#     return {"success": False, "cause": "Bad Request"}, 400


