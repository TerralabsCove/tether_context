---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera stream delay over USB and Wi-Fi, camera 2 (2026-11-13)

Written by John's AI agent from a working session with John on 2026-11-13. Not authoritative. Tool and results are in
[2026-11-13-john-recamera-stream-latency/](2026-11-13-john-recamera-stream-latency/). Nothing here changes `truth/`.

The question: if video is streamed to the laptop and tags are found there, what frame rate and delay do we get?
This bears on [open question 7](../truth/open-questions.md) and on D-037, which says no video leaves the robot.

## Bottom line

- **Over USB the stream is about 143 ms behind real time at 26.7 fps, with no stalls.** **[verified]**
- **Over the camera's own Wi-Fi it is about 169 ms behind when it flows, and it does not always flow.** One
  60 s run at point-blank range had a 15 s outage and a second short hiccup. **[verified]**, one run.
- **The cause of the outage is not known.** The Mac stayed joined to the camera and the camera logged no radio
  error. One run cannot say how often it happens.
- **A laptop-side reader must decode on one thread.** With the default, the Mac's decoder adds about 480 ms.
  **[verified]**

## Setup

- Camera 2, GC2053 with its stock lens, OS 0.2.4, with the
  [27 fps patch](2026-11-13-john-recamera-27fps-patch.md) on. 1920 × 1080 H.264, RTSP over TCP. Tag loop off.
- The Mac draws a moving time code full screen. The camera looks at the screen from about 40–50 cm. The Mac reads
  the code back out of each frame and compares it with its clock.
  [latency_test.py](2026-11-13-john-recamera-stream-latency/latency_test.py). Its self-test reads simulated frames
  to within 12 ms, typically under 1 ms.
- The delay includes the Mac screen's own lag, about one or two refreshes at 60 Hz. **[assumed]** So the camera
  and stream alone are somewhat less than the figures here. The USB to Wi-Fi difference is not affected.
- Wi-Fi: the camera's own access point, `reCamera_02DE69`, 2.4 GHz channel 6, 20 MHz. The Mac was the only
  client, at −21 dBm and 72.2 Mbit/s. USB stayed plugged in for power.

## Results

| Run | Frames per second | Delay, median | Delay, 5th–95th percentile | Stalls over 200 ms | Longest gap |
|---|---|---|---|---|---|
| [USB, decoder on 1 thread](2026-11-13-john-recamera-stream-latency/camera2/usb_1080p_threads1.json), 15 s | 26.7 | 142 ms | 119–162 ms | 0 | 51 ms |
| [USB again](2026-11-13-john-recamera-stream-latency/camera2/usb_1080p_60s_asked_at_wifi_address.json), 55 s | 26.7 | 144 ms | 120–201 ms | 0 | 58 ms |
| [USB, decoder on all 14 cores](2026-11-13-john-recamera-stream-latency/camera2/usb_1080p_threads0.json), 15 s | 26.7 | 623 ms | 602–643 ms | 0 | 49 ms |
| [Wi-Fi](2026-11-13-john-recamera-stream-latency/camera2/wifi_1080p.json), 60 s | 20.1 average, 27 when flowing | 169 ms | 125–284 ms | 8 | 8.6 s |

All **[verified]**. The second USB run has 112 misread samples of 1,556 in its tail figures. Without them its
range is 123–169 ms.

**The Wi-Fi run, second by second.** It took two tries and about 17 s to open the stream after the Mac joined.
Then:

| Time | What happened |
|---|---|
| 0–20 s | Steady, 24–30 frames each second, delay 161–173 ms |
| 20–35 s | Outage. Gaps of 0.9 s, 0.3 s, 5.1 s and 8.6 s. The reader timed out and reconnected |
| 35–60 s | Steady again. One hiccup at about 43 s: two gaps of 0.2–0.35 s, delay up to 850 ms |

During the outage the camera's log shows the Mac associated the whole time (from 00:40:59 to 00:42:56 camera
clock) and no kernel messages. Suspects, none tested: the Mac scanning for other networks while on one with no
internet, the camera's Wi-Fi driver (Seeed's OS 0.2.5 notes list a fix for long-run Wi-Fi drop-outs, and camera 2
is on 0.2.4), or the stream server. RTSP over TCP also turns a short break into a long one, because the reader
waits 5 s before reconnecting.

## The decoder thread finding

The first USB run read 635 ms. OpenCV's ffmpeg reader decodes on every core by default and holds back about one
frame per thread: 13 frames × 37 ms ≈ 480 ms on this 14-core Mac. Opening the stream with
`cv2.CAP_PROP_N_THREADS = 1` brought it to 142 ms. Run both ways twice, same result each time. Passing `threads;1`
through `OPENCV_FFMPEG_CAPTURE_OPTIONS` did not work.

## A run that was not Wi-Fi

The first "Wi-Fi" attempt was really USB. The Mac failed to join the camera's network and dropped its normal
Wi-Fi. Its second default route is the camera over the USB cable, so the camera's Wi-Fi address answered through
the cable. The camera showed no Wi-Fi client and no Wi-Fi DHCP lease. John spotted it. That run is kept as a USB
run, and the tool now refuses to start unless the Mac has an address on the camera's Wi-Fi network.

## What this does and does not show

- Wi-Fi adds about 26 ms to the typical delay and widens the spread. That part looks fine.
- Stalls are the open risk. One outage in one minute, at 40–50 cm, is not a rate.
- Nothing was measured at range, through walls, with the robot's 5 GHz motor link running, or with two cameras.
- For comparison, the stock on-camera loop gives 5–6 detections per second. Its delay has not been measured.

## Next

1. A 5-minute Wi-Fi run with the ping log the tool now keeps alongside the video. If pings stop during an outage,
   it is the radio. If they keep going, it is the stream.
   `./run_wifi_test.sh wifi_1080p_5min 300`
2. If outages repeat, try RTSP over UDP and a shorter reconnect time.
3. A range run with the camera on a battery, measuring frame rate and stalls only.
