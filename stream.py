import json
import time
import cv2
import requests
import base64
import numpy as np

while True:
    data = requests.get('https://altoponix-database.herokuapp.com/get/?key=672ef79b4d0a4805bc529d1ae44bc26b')
    feed_encoded = json.loads(data.text)["data"]["foliage_feed"]
    image = cv2.imdecode(np.frombuffer(base64.b64decode(feed_encoded), dtype=np.uint8), flags=1)
    cv2.imshow('Stream', cv2.resize(image, (480, 360)))
    cv2.waitKey(1)

