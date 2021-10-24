import base64
import cv2
import json
import requests
import time

cap = cv2.VideoCapture(0)
url = "https://altoponix-database.herokuapp.com/set"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
counter = 0
while True:
    data = {
        "key": "672ef79b4d0a4805bc529d1ae44bc26b",
        "foliage_feed": base64.b64encode(
            cv2.imencode(
                ".JPG",
                cv2.resize(
                    cap.read()[1],
                    (10,10)))[1]).decode("utf-8"),
        "atmospheric_temp": 8}
    requests.post(url, data=json.dumps(data), headers=headers)
    time.sleep(0.1)
    print(counter := counter + 1)
