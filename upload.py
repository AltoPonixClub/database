import base64
import cv2
import json
import requests
import time
import numpy as np
import threading
import os

url = "https://altoponix-database.herokuapp.com/set"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
counter = 0
feed_buffer = []
buffer_size = 3

def feed_encode():
    try:
        cap = cv2.VideoCapture(-1)
    except Exception as e:
        cap = cv2.VideoCapture(os.environ['VIDEO'])
    start_time = time.time()
    while True:

        raw_image = cap.read()[1]
        size = (raw_image.shape[0]//8, raw_image.shape[1]//8)
        print(size)
        data = {
            "key": "672ef79b4d0a4805bc529d1ae44bc26b",
            "foliage_feed": base64.b64encode(
                cv2.imencode(
                    ".JPEG",
                    cv2.resize(
                        raw_image,
                        size), [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality:=60])[1]).decode("utf-8"),
            "atmospheric_temp": np.random.randint(0, 5)}
        feed_buffer.append(json.dumps(data))
        if len(feed_buffer) > buffer_size:
            del feed_buffer[0]
        time.sleep(1/cap.get(cv2.CAP_PROP_FPS))
        # print(len(data["foliage_feed"]))

def upload(fps=1):
    counter = 0
    while len(feed_buffer) == 0:
        continue
    while True:
        requests.post(url, data=feed_buffer[-1], headers=headers)
        time.sleep(1/fps)
        print(counter:=counter+1)

threading.Thread(target=feed_encode).start()
time.sleep(1)
threading.Thread(target=upload, args=(10,)).start()

# print(counter := counter + 1)
