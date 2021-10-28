import base64
import cv2
import json
import requests
import time

cap = cv2.VideoCapture("../../python/blind-navigation/TurnSidewalk.mp4")
url = "https://altoponix-database.herokuapp.com/set"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
counter = 0
while True:
    raw_image = cap.read()[1]
    size = (raw_image.shape[0]//30, raw_image.shape[1]//30)
    print(size)
    data = {
        "key": "672ef79b4d0a4805bc529d1ae44bc26b",
        "foliage_feed": base64.b64encode(
            cv2.imencode(
                ".JPEG",
                cv2.resize(
                    raw_image,
                    size), [int(cv2.IMWRITE_JPEG_QUALITY), 95])[1]).decode("utf-8"),
        "atmospheric_temp": 8}
    # print(len(data["foliage_feed"]))
    requests.post(url, data=json.dumps(data), headers=headers)
    time.sleep(0.1)
    print(counter := counter + 1)
