#!/bin/sh
# Unattended Wi-Fi run. Start it, then join the Mac to the camera's own Wi-Fi network (reCamera_XXXXXX).
# It waits up to 30 minutes for the camera at 192.168.16.1, measures (60 s by default), and saves into camera2/.
# Usage: run_wifi_test.sh [label] [seconds]
# The USB cable can stay in for power; the video goes over Wi-Fi because it is asked for at the Wi-Fi address.
cd "$(dirname "$0")" || exit 1
LABEL=${1:-wifi_1080p}
python3 latency_test.py --out=camera2 --label="$LABEL" --url=rtsp://192.168.16.1:554/live --wait=1800 --need-local-prefix=192.168.16. --seconds="${2:-60}" --giveup=180 > "camera2/$LABEL.log" 2>&1
# Radio details as the camera sees them (signal, link rate), read over the USB cable.
ssh -o BatchMode=yes -o ConnectTimeout=5 recamera@192.168.42.1 'sudo iw dev wlan1 station dump; iw dev wlan1 info' > "camera2/${LABEL}_radio.txt" 2>&1
route -n get 192.168.16.1 > "camera2/${LABEL}_route.txt" 2>&1
