#!/bin/bash

# # create a folder in shared memory
# mkdir -p /dev/shm/streaming
#
# # link it to current folder
# if [[ -L hls && -d $(readlink hls) ]]; then
#     echo ""
# else
#     ln -s /dev/shm/streaming streaming
# fi

# create video segments for HLS and DASH
# ffmpeg -y \
#     -input_format h264 \
#     -f video4linux2 \
#     -framerate 25 \
#     -use_wallclock_as_timestamps 1 \
#     -i 0 \
#     -c:v copy \
#     -f dash \
#     -ldash 1 \
#     -seg_duration 1 \
#     -frag_duration 1 \
#     -streaming 1 \
#     -window_size 30 -remove_at_exit 1 \
#     -strict experimental -lhls 1 \
#     -hls_playlist 1 -hls_master_name live.m3u8 \
#     -utc_timing_url https://time.akamai.com/?iso \
#     -write_prft 1 \
#     -target_latency 1 \
#     /dev/shm/streaming/live.mpd &
   
ffmpeg \
    -f v4l2 -video_size 640x480 \
    -i /dev/video0 \
    -c:v libx264 -crf 21 -preset veryfast \
    -b:v 100M -b:a 128k \
    -f hls \
    -hls_list_size 2 \
    -hls_flags independent_segments -hls_flags delete_segments \
    -hls_segment_type mpegts \
    -hls_segment_filename data%02d.ts \
    -master_pl_name master.m3u8 out1
