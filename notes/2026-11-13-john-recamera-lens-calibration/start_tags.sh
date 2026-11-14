#!/bin/sh
# Keeps the tag sender running: camera RTSP stream -> ffmpeg decode -> tagstream -> UDP broadcast on port 5005.
# The camera node must be set to 640x480: the camera ffmpeg decodes nothing at 720p or 1080p (2026-11-13).
# -vsync passthrough stops ffmpeg repeating frames to fill the nominal 30 fps (the real stream is 9 fps).
# fx fy cx cy are from the 2026-11-13 calibration of camera 2 (GC2053 stock lens) at 1080p, scaled to the 640x480 letterboxed stream.
cd /userdata/atbench || exit 1
[ -f /tmp/tags.pid ] && kill "$(cat /tmp/tags.pid)" 2>/dev/null
echo $$ > /tmp/tags.pid
for pid in $(pidof tagstream); do kill "$pid"; done
while true; do
    ffmpeg -nostdin -loglevel error -rtsp_transport tcp -fflags nobuffer -flags low_delay -an -threads 1 -vsync passthrough \
        -i rtsp://127.0.0.1:554/live -f rawvideo -pix_fmt yuv420p - 2>>/tmp/tags.log \
        | ./tagstream 640 480 355.0 354.5 321.7 243.7 2 5005 >>/tmp/tags.log 2>&1
    sleep 3
done
