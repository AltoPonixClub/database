from flask import Flask, redirect, url_for, render_template, request, jsonify
import numpy as np
import cv2
import base64
import threading

app = Flask(__name__)
temp_image = cv2.resize(cv2.imread("plant_demo.JPG"), (360, 360))
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
data = {"atmospheric_temp": 30, "reservoir_temp": 25, "foliage_feed": base64.b64encode(cv2.imencode(".JPG", temp_image)[1]).decode("utf-8")}
# data = {"atmospheric_temp": 30, "reservoir_temp": 25, "foliage_feed": 3}
lock = threading.Lock()
@app.route("/", methods = ['POST', 'GET'])
def home():
    return jsonify(data)


@app.route('/get/<key>', methods=['GET'])
def get(key):
    with lock:
        return data[key]

@app.route('/set/<key>/<val>', methods=['GET', 'POST'])
def set(key, val):
    with lock:
        data[key]=val
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()

