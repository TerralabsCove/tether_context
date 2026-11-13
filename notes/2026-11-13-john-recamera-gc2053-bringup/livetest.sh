#!/bin/sh
# Live detection test: camera RTSP -> ffmpeg decode -> tagstream, for SECS seconds.
# Usage: livetest.sh W H DECIMATE SECS
W=$1; H=$2; D=$3; SECS=$4
cd /userdata/atbench || exit 1
for p in $(pidof tagstream) $(pidof ffmpeg); do kill -9 $p 2>/dev/null; done
FX=$((W / 2))
timeout $SECS sh -c "ffmpeg -nostdin -loglevel error -rtsp_transport tcp -fflags nobuffer -flags low_delay -an -threads 1 -vsync passthrough \
  -i rtsp://127.0.0.1:554/live -f rawvideo -pix_fmt yuv420p - | ./tagstream $W $H $FX $FX $((W/2)) $((H/2)) $D 5005"
for p in $(pidof tagstream) $(pidof ffmpeg); do kill -9 $p 2>/dev/null; done
