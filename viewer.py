import json
import time
import cv2
import requests
import numpy as np
import threading
import os

feed_buffer = []

def fetch_frag():
    last_feed_encoded = None
    while True:
        data = requests.get(
            'https://altoponix-database.herokuapp.com/api/v1/monitors/get?monitor_id=672ef79b4d0a4805bc529d1ae44bc26b')
        feed_encoded = json.loads(data.text)["data"]["foliage_feed"]
        if feed_encoded != last_feed_encoded:
            last_feed_encoded = feed_encoded
            frag_to_remove = os.listdir("client_vids")
            frag_path = "client_vids/frag%s.mp4" % round(time.time())
            with open(frag_path, "wb") as f:
                vid = bytes.fromhex(feed_encoded)
                f.write(vid) # TODO convert from str to bytes
                feed_buffer.clear()
                feed_buffer.append(frag_path)
            for path in frag_to_remove:
                os.remove(os.path.join("client_vids", path))
        time.sleep(0.1)

def view():
    last_vid_path = None
    while True:
        frags = os.listdir("client_vids")
        if len(frags) > 0:
            vid_path = os.path.join("client_vids", frags[0])
            if vid_path != last_vid_path:
                last_vid_path = vid_path
                vid = cv2.VideoCapture(vid_path)
                while True:
                    ret, frame = vid.read()
                    if not ret:
                        break
                    cv2.imshow("Stream", frame)
                    cv2.waitKey(1)
                    time.sleep(1/vid.get(cv2.CAP_PROP_FPS))

threading.Thread(target=fetch_frag).start()
threading.Thread(target=view).start()
