from flask import Flask, redirect, url_for, render_template, request, jsonify,abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import numpy as np
import cv2
import base64
import threading

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
temp_image = cv2.resize(cv2.imread("plant_demo.JPG"), (360, 360))
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
data = {"atmospheric_temp": 30, "reservoir_temp": 25, "foliage_feed": base64.b64encode(cv2.imencode(".JPG", temp_image)[1]).decode("utf-8")}
lock = threading.Lock()
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["300 per minute"]
)

 
@app.route('/', methods=['GET'])
def home():
	return ""

@app.route('/get/', methods=['GET'])
def get():
	with lock:
		return jsonify(data)

@app.route('/get/<key>', methods=['GET'])
def getkey(key):
	with lock:
		if key in data:
			return str(data[key])
		else:
			abort(404)

@app.route('/set/', methods=['POST'])
def set():
	with lock:
		content = request.get_json()
		for key, value in content.items():
			if key in data:
				print("set " + key + " to " + str(value))
				data[key] = value
		return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()
	