import base64
import cv2
import json
import requests
import time
import numpy as np
import threading
import os
import constants

url = "https://altoponix-database.herokuapp.com/api/v1/monitors/update"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
feed_buffer = []
buffer_size = 3
prefix_path = 'vids/frag/'

def frag_maker():
    try:
        cap = cv2.VideoCapture(-1)
        assert (cap.read()[1] is not None)
    except Exception as e:
        cap = cv2.VideoCapture(os.environ['VIDEO'])
    # fourcc = cv2.VideoWriter_fourcc(*'H264')
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    tot = cv2.VideoWriter('vids/tot.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), constants.img_size)
    tot_frames_per_vid = 1
    frag_length = 6
    counter = 0
    while True:
        start_time = counter / cap.get(cv2.CAP_PROP_FPS)
        frag = cv2.VideoWriter(os.path.join(prefix_path, 'frag.mp4'), fourcc, cap.get(cv2.CAP_PROP_FPS), constants.img_size)
        while (counter / cap.get(cv2.CAP_PROP_FPS) - start_time) < frag_length:
            print(counter / cap.get(cv2.CAP_PROP_FPS))
            ret, frame = cap.read()
            frame = cv2.resize(frame, constants.img_size)
            frag.write(frame)
            if counter % tot_frames_per_vid == 0:
                tot.write(frame)
            cv2.imshow('frame', frame)
            counter += 1
            time.sleep(1 / cap.get(cv2.CAP_PROP_FPS))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        frag.release()
        for path in [path for path in os.listdir(prefix_path) if constants.finished_identifier in path and '.mp4' in path]:
            os.remove(os.path.join(prefix_path, path))
        os.rename(os.path.join(prefix_path, 'frag.mp4'), os.path.join(prefix_path, 'frag_done_%s.mp4' % round(time.time())))


def json_updater():
    last_uploaded_mp4 = None
    while True:
        # TODO: finish this
        for path in [path for path in os.listdir(prefix_path) if constants.finished_identifier in path and '.mp4' in path]:
            if last_uploaded_mp4 != path:
                last_uploaded_mp4 = path
                with open(os.path.join(prefix_path, path), 'rb') as f:
                    data = {
                        "id": "672ef79b4d0a4805bc529d1ae44bc26b",
                        "foliage_feed": str(f.read())}
                    # data["foliage_feed"] = "None"
                    feed_buffer.append(json.dumps(data))
                    if len(feed_buffer) > buffer_size:
                        del feed_buffer[0]
        # time.sleep(1 / cap.get(cv2.CAP_PROP_FPS))
        # print(len(data["foliage_feed"]))


def uploader(fps=1):
    counter = 0
    while len(feed_buffer) == 0:
        continue
    while True:
        requests.post(url, data=feed_buffer[-1], headers=headers)
        time.sleep(1 / fps)
        print(counter := counter + 1)


threading.Thread(target=frag_maker).start()
time.sleep(1)
threading.Thread(target=json_updater).start()
time.sleep(1)
threading.Thread(target=uploader, args=(10,)).start()
