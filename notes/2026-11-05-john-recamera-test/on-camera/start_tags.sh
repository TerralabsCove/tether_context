#!/bin/sh
# Keeps the tag sender running: camera RTSP stream -> ffmpeg decode -> tagstream -> UDP broadcast on port 5005.
# fx and fy below are estimates for 640x480 until that mode is calibrated.
cd /userdata/atbench || exit 1
[ -f /tmp/tags.pid ] && kill "$(cat /tmp/tags.pid)" 2>/dev/null
echo $$ > /tmp/tags.pid
for pid in $(pidof tagstream); do kill "$pid"; done
while true; do
    ffmpeg -nostdin -loglevel error -rtsp_transport tcp -fflags nobuffer -flags low_delay -an -threads 1 \
        -i rtsp://127.0.0.1:554/live -f rawvideo - 2>>/tmp/tags.log \
        | ./tagstream 640 480 586 586 320 240 2 5005 >>/tmp/tags.log 2>&1
    sleep 3
done
