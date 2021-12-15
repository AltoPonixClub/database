from .. import socketio
from flask import request
from flask_socketio import emit

# Socket Variables
clients = {}
devices = {}
monitordevice = {}

# Socket Handling

# query: event sent by client to start sending commands.
# JSON data:
# {
#    "monitor_id": string, the monitor_id to start sending to (REQUIRED)
# }
# emits "query ok" if connection succeeded, "query failed" if connection didn't (and closes the connection)
@socketio.on('query')                    
def query(content):      
  if "monitor_id" not in content or content["monitor_id"] is None or type(content["monitor_id"]) != str or len(content["monitor_id"]) != 32:
    emit('query failed', {'reason': 'Invalid monitor_id'}, room=request.sid) 
    return
  clients[request.sid] = content["monitor_id"]
  emit('query ok', {'reason': 'Query ok'}, room=request.sid) 

# con: event sent by device to start listening commands.
# JSON data:
# {
#    "monitor_id": string, the monitor_id of this device (REQUIRED)
# }
# the monitor_id given must be a unique one that is currently not connected to a websocket
# emits "con ok" if connection succeeded, "con failed" if connection didn't (and closes the connection)
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

# command send: event sent by client to send a command to the device.
# JSON data:
# {
#    "command": string, the command to send (REQUIRED)
# }
# emits "command failed" to the client if the command was invalid
# emits "command ok" to the client
# emits "command do" to the device with the same json data given
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

# command done: event sent by device to signal when a command finishes
# emits command finish to the client
@socketio.on('command done')                    
def done(content):
  for sid, m in clients.items():
    if m == devices[request.sid]:
      emit('command finish', {'reason': 'Command finish'}, room=sid) 

# command error: event sent by device to signal when a command fails
# JSON data:
# {
#    "reason": string, the reason to send
# }
# emits command failed to the client
@socketio.on('command error')                    
def done(content):
  for sid, m in clients.items():
    if m == clients[request.sid]:
      emit('command failed', {'reason': content.reason}, room=sid) 

# Remove devices
@socketio.on('disconnect')  
def handle_disc():
  if request.sid in devices:
    mon = devices[request.sid]
    monitordevice.pop(mon, None)
  clients.pop(request.sid, None)
  devices.pop(request.sid, None)