---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera GC2053 bring-up: 9 fps cap and on-camera detection speed (2026-11-12 to 11-13)

Written by John's AI agent from a working session with John on 2026-11-12 and 11-13. Not authoritative. It follows the
[GC2053 swap research note](2026-11-12-john-recamera-gc2053-swap.md). Raw logs and counters are in
[2026-11-13-john-recamera-gc2053-bringup/](2026-11-13-john-recamera-gc2053-bringup/). Nothing here changes `truth/`.

## Bottom line

- **The swap works.** Both 2002w cameras detect the GC2053 board. **[verified]** John fitted the fisheye M12 lenses,
  and the first frames show strong barrel distortion. **[as built]**
- **The camera stream runs at 9 fps whatever it is set to.** This is a known limit of Seeed's stock pipeline, not the
  GC2053. Our 11-05 OV5647 test ran at the same rate. **[verified]** for our cameras; cause from Seeed's wiki and a
  community write-up.
- **Detection, not the camera, is the bottleneck.** On the camera, detection takes about 146 ms per 640 × 480 frame
  live, so about 5–6 detections per second. At 1280 and 1920 px it takes 0.45 s and 1.2 s on clean test images.
  **[verified]**
- **The 11-05 pipeline only works at 640 × 480.** The camera's `ffmpeg` decodes no frames at 720p or 1080p.
  **[verified]**
- **So the fisheye is held back by resolution.** At 640 px a 5 cm tag stays readable only to about 30 cm
  ([calculated in the 11-12 note](2026-11-12-john-recamera-gc2053-swap.md)). Range needs bigger dock tags, or a new
  pipeline that reads frames from the video hardware instead of decoding the stream.

## The two cameras

| | Camera 1 | Camera 2 |
|---|---|---|
| OS | reCamera 0.2.1 | reCamera 0.2.4 |
| Web UI device info | Basic WiFi 64G (GC2053) | Basic WiFi 64G (GC2053) |
| `i2cdetect -y -r 2` | `3f`, no `36` | not run |
| History | Factory reset on 11-12 | Not reset. It still has the 11-05 kit in `/userdata/atbench` |

Both report GC2053, so OS 0.2.1 and later detect the board with no change, as the
[11-12 note](2026-11-12-john-recamera-gc2053-swap.md) predicted from source. **[verified]**

## Starting the stream after a reset

A factory reset removes the stream. The default Node-RED flow has a camera node feeding Seeed's demo AI model, and no
stream node. What made `rtsp://192.168.42.1:554/live` work again:

1. Add a `stream` node (RTSP, port 554, session `live`) wired from the camera node.
2. Clear the stream node's username and password. It defaults to admin/admin, and our scripts connect without a login.
3. Do a full flow restart. A per-node deploy reported "running" but sent no video.
4. Disable the demo `model` node, so the camera's one CPU core is free for tag detection.

Seeed's wiki also documents the stream node and the admin/admin default
([RTSP to WebRTC guide](https://wiki.seeedstudio.com/rtsp_to_webrtc_with_recamera/)).

## The 9 fps cap

**Measured.** Both cameras stream 9.0 fps at 1080p, 720p and 480p. Setting the camera node to 30, 15 or 10 fps
changes nothing. The sensor runs at 27 fps (`VIDevFPS 27`), but the video input stage processes only one frame in
three (`VIFPS 9`). The scaler (VPSS) takes about 112 ms per frame, which is the limit. **[verified]**,
[counters](2026-11-13-john-recamera-gc2053-bringup/pipeline_counters.txt)

**Ruled out.** **[verified]**

- USB bandwidth: the stream uses 1.7 Mbit/s.
- CPU: 81% idle while streaming.
- Heat: 44 °C, throttling off.
- Output resolution and the fps setting: both tried.
- OS version: 0.2.1 and 0.2.4 behave the same.
- Lighting: a 40 s bright-light test kept `VIFPS` at 8–9. The agent did not see the camera during it.

**It was there before the swap.** The 11-05 OV5647 test log has a median of 110 ms between processed frames,
9.1 fps, and never more than 10 fps over any 5 s window ([tag_log.csv](2026-11-05-john-recamera-test/tag_log.csv)).
That log measures the Mac script's rate, so it is a strong hint, not proof. **[calculated from team file]**

**Cause, per the docs.** Seeed's own wiki says the stock pipeline has a "10 fps limitation" and puts the
Node-RED streaming ceiling at 1080p 15 fps ([Frigate guide](https://wiki.seeedstudio.com/recamera_firgate/)).
The wiki links a community publisher whose
[root-cause write-up](https://github.com/xr686/recamera-rtsp30/blob/main/docs/ROOT_CAUSE.md) blames the frame buffer
pool. Seeed's camera code gives it 4 buffers (`vb_blk_num = 4`) and lets the scaler's queue hold 3 of them
(`u32Depth = 3`). The scaler starves for buffers, and the image processor handles one frame in three. Our cameras
show the same values: pool 2 count 4, scaler channel 2 depth 3. Seeed's source has them at
[video_paramparse.c](https://github.com/Seeed-Studio/sscma-example-sg200x/blob/main/components/sophgo/video/src/video_paramparse.c)
lines 11 and 98. **[source code]** One counter differs: the write-up reports thousands of scaler start failures,
and ours shows `StartFailCnt 0`.

**Fix, not applied.** The write-up says 8 buffers or a queue depth of 1 gives 30 fps. Their publisher replaces
Seeed's Node-RED and sscma services and streams on port 8554. It is third-party, unlicensed, and tested only on the
OV5647. The SG2002 itself is rated 5 MP at 30 fps ([Milk-V SG2002](https://milkv.io/chips/sg2002)).

**Does it matter?** Not yet. Detection is slower than 9 fps at every useful resolution (below). The cap matters only
if detection gets faster or docking steers on the camera while moving. No docking rate requirement exists in `truth/`.

## On-camera detection speed

**Benchmark.** The 11-05 `atbench` build on synthetic tag36h11 images, 10 runs each, median per detection. Pose
estimation adds about 20 ms. Linux sees one CPU core. **[verified]**,
[raw output](2026-11-13-john-recamera-gc2053-bringup/atbench.txt)

| Width | Decimate 1 | Decimate 2 | Decimate 3 | Decimate 4 |
|---|---|---|---|---|
| 320 px | 116 ms | 39 ms | | |
| 640 px | 567 ms | 120 ms | | |
| 1280 px | 2.3 s | 453 ms | 193 ms | 106 ms |
| 1920 px | 6.2 s | 1.16 s | 471 ms | 296 ms |

The test image's tag is large and clean. Higher decimation searches at a quarter of the resolution or less, so small
or distant tags will be missed. Treat the decimate 3–4 times as best case.

`atbench` takes six arguments: image, family, decimate, repeats, then two numbers that only change the reported
distance. We used 586 and 0.05, which look like focal length and tag size. **[assumed]**

**Live.** Camera 2 with the fisheye, a tag36h11 (ID 0) shown on the Mac screen at about 30 cm, 640 × 480,
decimate 2. Stream decoded on the camera by `ffmpeg` into `tagstream`. **[verified]**,
[script](2026-11-13-john-recamera-gc2053-bringup/livetest.sh) and logs

| Run | Real frames in | Detections/s | ms per detection | Tag width |
|---|---|---|---|---|
| [60 s](2026-11-13-john-recamera-gc2053-bringup/live_640_with_duplicates.jsonl) | 9 fps | 4.7 | 181 | about 136 px |
| [30 s, `-vsync passthrough`](2026-11-13-john-recamera-gc2053-bringup/live_640_passthrough.jsonl) | 9–11 fps | 5.8 | 146 | about 128 px |

In the first run `ffmpeg` padded the 9 fps stream to its nominal 30 fps with repeated frames, so `tagstream`
reported 28–88 frames in. Turning that off freed about 25% of detection time. `livetest.sh` now keeps it off.
The 11-06 note's "3–8 detections per second" fits these numbers.

**Only 480p decodes on the camera.** `ffmpeg` 4.4 on camera 2 decoded 160 frames in 25 s at 640 × 480, and none at
720p or 1080p. The Mac decodes the same streams fine. The cause is not known. **[verified]**

## What this changes

- **Open question 7** (camera compute and data path): on-camera detection works at about 5–6 Hz at 640 × 480. It
  does not work above 480p with the current pipeline.
- **[11-12 note](2026-11-12-john-recamera-gc2053-swap.md), test plan:** steps 1, 2 and the detection-rate step are
  done for 640 px. 1280 and 1920 px could not be tested live.
- **[truth/robot.md](../truth/robot.md)** still says the stock lens is 65° and the lens path is open. The cameras
  now have the GC2053 board and the fisheye. That needs a person to update.

## Options to get range

1. **Bigger tags on the dock.** Works with today's pipeline. Cheapest.
2. **Read frames from the video hardware**, not the RTSP stream, and detect only near the last known tag position.
   Removes the decode limit. Real development work.
3. **Apply the buffer fix** only if detection ever beats 9 Hz, and report it to Seeed on
   [sscma-example-sg200x](https://github.com/Seeed-Studio/sscma-example-sg200x).
4. **Decide stop-and-look vs continuous docking.** That sets the real rate requirement, and it is not written down.

## State left on the cameras

| | Camera 1 | Camera 2 |
|---|---|---|
| Stream | 1080p, no login, port 554 | 480p, no login, port 554 |
| Demo AI model | Disabled | Not present |
| SSH key | John's key installed | John's key installed |
| Passwordless sudo | **On**, `/etc/sudoers.d/zz-recamera-nopasswd`. Remove before the robot or a shared network | Off |
| Old tag loop flow | n/a | **Disabled** (`start tag sender at boot`). It still runs 640 × 480 without passthrough |

Both cameras use 192.168.42.1 over USB, so SSH warns about a changed host key whenever they are swapped. Clear it
with `ssh-keygen -R 192.168.42.1`.
