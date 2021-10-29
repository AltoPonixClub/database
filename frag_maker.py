# install: sudo apt-get install ffmpeg x264 libx264-dev

import numpy as np
import cv2
import os
import time

cap = cv2.VideoCapture(os.environ.get('VIDEO'))
size = (480, 360)
prefix_path = 'vids/frag/'
# fourcc = cv2.VideoWriter_fourcc(*'H264')
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
tot = cv2.VideoWriter('vids/tot.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), size)
tot_frames_per_vid = 1
frag_length = 5
counter, tick = 0, 0
finished_identifier = 'done'
while True:
    start_time = counter / cap.get(cv2.CAP_PROP_FPS)
    frag = cv2.VideoWriter(os.path.join(prefix_path, 'frag.mp4'), fourcc, cap.get(cv2.CAP_PROP_FPS), size)
    while (counter / cap.get(cv2.CAP_PROP_FPS) - start_time) < frag_length:
        print(counter / cap.get(cv2.CAP_PROP_FPS))
        ret, frame = cap.read()
        frame = cv2.resize(frame, size)
        frag.write(frame)
        if counter % tot_frames_per_vid == 0:
            tot.write(frame)
        cv2.imshow('frame', frame)
        counter += 1
        time.sleep(1 / cap.get(cv2.CAP_PROP_FPS))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    frag.release()
    for path in [path for path in os.listdir(prefix_path) if finished_identifier in path and '.mp4' in path]:
        os.remove(os.path.join(prefix_path, path))
    os.rename(os.path.join(prefix_path, 'frag.mp4'), os.path.join(prefix_path, 'frag_done_%s.mp4' % round(time.time())))
    # tick += 1
    # if tick == 2:
        # exit(0)
