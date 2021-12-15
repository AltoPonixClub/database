from flask import Flask, redirect, url_for, request, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask Application
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
app.config['JSON_SORT_KEYS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
limiter = Limiter(
  app,
  key_func=get_remote_address,
  default_limits=["300 per minute"]
)

@app.route('/', methods=['GET'])
def home():
  return

# import functions
import database
import websocket

# 404 handler
@app.errorhandler(404)
def fallback(_):
  return {"success": False,
          "cause": "The specified URI was not found on this server"}, 404

# run the app
if __name__ == "__main__":
   socketio.run(app)

