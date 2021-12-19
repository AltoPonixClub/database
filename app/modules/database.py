from .. import app
from flask import request
from pymongo import MongoClient
import threading
import os
import time
import certifi

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

# Connect to MongoDB
client = MongoClient("mongodb+srv://altoponix-db:" + os.environ['DB_PSWD'] + "@altoponix.nej4q.mongodb.net", tlsCAFile=certifi.where())
db = client.database
monitors = db.get_collection("monitors")
users = db.get_collection("users")

# ALL IDS SHOULD BE 32 CHARS LONG, AND IN HEX FORMAT
def isValidID(id):
  return not (id is None or not isinstance(id,str) or len(id) != 32 or not id.isalnum())

# Get Method: Returns the monitor with the specified monitor_id
# Argument Input:
#  "monitor_id": string
# If a monitor_id isn't passed, then returns all monitors
@app.route('/api/v1/monitors/get', methods=['GET'])
def get_monitor():
  try: 
    # Return All
    if request.args.get('monitor_id') is None:
      data = monitors.find({}, {"_id": 0, "owner": 0})
      dat = {}
      for doc in data:
        dat[doc["monitor_id"]] = doc
      return {"success": True, "data": dat}
    # Safety Checking
    if not isValidID(request.args.get('monitor_id')):
      return {"success": False, "cause": "Invalid monitor_id"}, 400
    data = monitors.find({"monitor_id": {'$eq': request.args.get('monitor_id')}}, {"_id": 0, "monitor_id": 0, "owner": 0})
    for doc in data:
      return {"success": True, "data": doc}
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "Bad Request"}, 400

# Update Method: Updates the monitor with the specified monitor_id
# JSON Input:
# {
#  "monitor_id": string (required)
#  "atmospheric_temp": number
#  "reservoir_temp":
#  etc ...
# }
@app.route('/api/v1/monitors/update', methods=['POST'])
def update_monitor():
  try:
    # Get the current time
    t = round(time.time() * 1000)
    # Safety Checking
    args = request.get_json()
    if "monitor_id" not in args or args["monitor_id"] is None:
      return {"success": False,
            "cause": "Missing one or more fields: [monitor_id]"}, 400
    if not isValidID(args["monitor_id"]):
      return {"success": False, "cause": "Invalid monitor_id"}, 400
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
        return {"success": False, "cause": "Couldn't update any fields"}, 400
      else:
        monitors.update_one({"monitor_id": {'$eq': args["monitor_id"]}}, {"$set": upd})
      return {"success": True}
    # If monitor_id isn't found
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "Bad Request"}, 400

# Add Method: Adds a monitor with the specified monitor_id to the specified user_id
# JSON Input:
# {
#  "monitor_id": string (required)
#  "user_id": string (required)
# }
@app.route('/api/v1/monitors/add', methods=['POST'])
def add_monitor():
  try:
    args = request.get_json()
    # Safety Checking
    if "user_id" not in args or args["user_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [user_id]"}, 400
    if "monitor_id" not in args or args["monitor_id"] is None:
      return {"success": False,
              "cause": "Missing one or more fields: [monitor_id]"}, 400
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
        "owner": args["user_id"]
      })
      dat = doc['monitor_ids']
      dat.append(args["monitor_id"])
      users.update_one({"user_id": {'$eq': args["user_id"]}}, {"$set": {"monitor_ids": dat}})
      return {"success": True}
    # If user isn't found
    return {"success": False, "cause": "Invalid user_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "Bad Request"}, 400

# Reset Method: Reset a monitor's data with the specified monitor_id
# JSON Input:
# {
#  "monitor_id": string (required)
# }
@app.route('/api/v1/monitors/reset', methods=['POST'])
def reset_monitor():
  try:
    args = request.get_json()
    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None:
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
    return {"success": False, "cause": "Bad Request"}, 400

# Delete Method: Deletes a monitor with the specified monitor_id. Also removes it from its owner's monitor list
# JSON Input:
# {
#  "monitor_id": string (required)
# }
@app.route('/api/v1/monitors/delete', methods=['POST'])
def delete_monitor():
  try:
    args = request.get_json()
    # Safety Checking
    if "monitor_id" not in args or args["monitor_id"] is None:
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
        return {"success": False, "cause": "An unkown error occured. Please try again in a few minutes"}, 500
      # Find the owner record with the owner_id
      for user in users.find({"user_id": {'$eq': owner_id}}):
        # Delete
        ids = user["monitor_ids"]
        ids.remove(args["monitor_id"])
        monitors.delete_one({"monitor_id": {'$eq': args["monitor_id"]}})
        users.update_one({"user_id": {'$eq': owner_id}}, {"$set": {"monitor_ids": ids}})
        return {"success": True}
      # If the owner record wasn't found???? (shouldn't happen)
      return {"success": False, "cause": "An unkown error occured. Please try again in a few minutes"}, 500
    # If monitor isn't found
    return {"success": False, "cause": "Invalid monitor_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "Bad Request"}, 400

# OWNER METHODS

# Get Method: Gets the owner given the specified user_id
# Argument Input:
#  "user_id": string
# If a user_id isn't passed, return all
@app.route('/api/v1/owners/get', methods=['GET'])
def get_users():
  try:
    user_id = request.args.get('user_id')
    if user_id is None:
      dat = {}
      data = users.find({}, {"_id": 0})
      for doc in data:
        dat[doc["user_id"]] = doc
      return {"success": True, "data": dat}
    # Safety Checking
    if not isValidID(user_id):
      return {"success": False,
              "cause": "Invalid user_id"}, 400
    for doc in users.find({"user_id": {'$eq': user_id}},{"_id": 0, "user_id": 0}):
      return {"success": True, "data": doc}
    return {"success": False, "cause": "Invalid user_id"}, 400
  except Exception as e:
    print(e)
    return {"success": False, "cause": "Bad Request"}, 400

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