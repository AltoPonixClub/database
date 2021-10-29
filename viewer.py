import json
import time
import cv2
import requests
import numpy as np
import threading
import os

feed_buffer = []

def fetch_frag():
    # TODO: clean up var naming
    last_feed_encoded = None
    while True:
        data = requests.get(
            'https://altoponix-database.herokuapp.com/api/v1/monitors/get?monitor_id=672ef79b4d0a4805bc529d1ae44bc26b')
        feed_encoded = json.loads(data.text)["data"]["foliage_feed"]
        if feed_encoded != last_feed_encoded:
            last_feed_encoded = feed_encoded
            for path in os.listdir("client_vids"):
                os.remove(os.path.join("client_vids", path))
            frag_path = "client_vids/frag%s.mp4" % round(time.time())
            with open(frag_path, "wb") as f:
                vid = bytes.fromhex(feed_encoded)
                f.write(vid) # TODO convert from str to bytes
                feed_buffer.clear()
                feed_buffer.append(frag_path)
        time.sleep(0.1)

def view():
    print(feed_buffer)
    time.sleep(1)
    running_vid = None
    while True:
        try:
            cv2.imshow('Stream', feed_buffer[-1])
            cv2.waitKey(1)
        except Exception as e:
            pass


threading.Thread(target=fetch_frag).start()
# threading.Thread(target=view).start()
