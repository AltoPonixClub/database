import json
import time
import cv2
import requests
import base64
import numpy as np
import threading

feed_buffer = []
buffer_size = 3


def fetch_img():
    while True:
        data = requests.get(
            'https://altoponix-database.herokuapp.com/api/v1/monitors/get?monitor_id=672ef79b4d0a4805bc529d1ae44bc26b')
        feed_encoded = json.loads(data.text)["data"]["foliage_feed"]
        img = cv2.resize(
            cv2.imdecode(
                np.frombuffer(
                    base64.b64decode(feed_encoded),
                    dtype=np.uint8),
                flags=1),
            (480,
             360))
        feed_buffer.append(img)
        if len(feed_buffer) > buffer_size:
            del feed_buffer[0]
        time.sleep(0.01)


def view():
    while True:
        try:
            cv2.imshow('Stream', feed_buffer[-1])
            cv2.waitKey(1)
        except Exception as e:
            pass


threading.Thread(target=fetch_img).start()
threading.Thread(target=view).start()
