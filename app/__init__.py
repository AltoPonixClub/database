from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
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
  return ""

from .modules import main as main_blueprint
app.register_blueprint(main_blueprint)

