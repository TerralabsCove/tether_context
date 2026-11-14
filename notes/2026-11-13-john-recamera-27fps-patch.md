---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera 27 fps: patched stream service tested on camera 2 (2026-11-13)

Written by John's AI agent from a working session with John on 2026-11-13. Not authoritative. It follows the
[9 fps cause note](2026-11-13-john-recamera-9fps-cause.md). Patch script and counters are in
[2026-11-13-john-recamera-27fps-patch/](2026-11-13-john-recamera-27fps-patch/). Nothing here changes `truth/`.

## Bottom line

- **The cap is gone on camera 2.** With a patched copy of Seeed's `sscma-node`, the stream runs at 26.6–27 fps at
  640 × 480 and at 1080p. **[verified]** It is 27 and not 30 because the sensor delivers 27.
- **This confirms the cause** in the 9 fps note on our own hardware. **[verified]**
- **The on-camera tag loop cannot use it.** It decodes the stream on the camera's one core and cannot keep up
  with 27 fps. Detection gets slower and less even, and the stream stalled once. **[verified]** for the rates;
  the stall was seen once and its cause is not proven.
- **The patch is not permanent.** It is mounted over the service for this boot only. A reboot puts the stock
  service back. John has not yet chosen whether to keep it.

## What was changed

Seeed's service sets the scaler's output queue depth to 3 for each video channel. With a 4-buffer pool that
starves the scaler ([9 fps note](2026-11-13-john-recamera-9fps-cause.md)). The patch sets the depth to 1. The pool
stays at 4 buffers, so memory use is unchanged.

- No build toolchain was needed. The change is 6 bytes in the OS 0.2.4 binary: three store instructions switched
  to a register that holds 1.
  [patch_sscma_node_depth.py](2026-11-13-john-recamera-27fps-patch/patch_sscma_node_depth.py) reproduces it and
  refuses any other binary.
- Depth 1 with 4 buffers is one of the configurations the
  [community write-up](https://github.com/xr686/recamera-rtsp30/blob/main/docs/ROOT_CAUSE.md) reported at 30 fps.
- The patched copy is on camera 2 at `/userdata/sscma-test/sscma-node-depth1`. It is bind-mounted over
  `/usr/local/bin/sscma-node`. The stock file is untouched.
- Camera 1 runs OS 0.2.1, which has a different binary. It was not patched or tested.

## Results

Camera 2, tag loop off. **[verified]**,
[patched counters](2026-11-13-john-recamera-27fps-patch/pipeline_counters_camera2_patched.txt),
[stock counters](2026-11-13-john-recamera-9fps-cause/pipeline_counters_camera2.txt)

| | Stock | Patched |
|---|---|---|
| Sensor rate (`VIDevFPS`) | 27 | 26–27 |
| Processed rate (`VIFPS`) | 9 | 26–27 |
| Scaler triggers refused | 26,761 of 40,175 (66.6%) | 1 of 1,536 |
| Scaler time per frame (`CostTime`) | 112 ms | 37 ms |
| Buffer pool 2, least free | 0 of 4 | 1 of 4 |
| Encoded frames per second, 640 × 480 | 9 | 26.6–26.8 |
| Encoded frames per second, 1080p | 9 | 26.6 |
| Frames per second at the Mac, 640 × 480 | 9.3 | 26–27 every second for 40 s |
| CPU idle, no stream client | 81% (11-12) | 66–80% |
| Temperature | 44 °C (11-12) | 34–39 °C |

The camera node's fps setting still does nothing. Set to 10 and to 15, the stream stayed at 26.6 fps.
**[verified]** So there is no way to slow the stream from Node-RED on OS 0.2.4.

## The on-camera tag loop at 27 fps

The loop decodes the H.264 stream with `ffmpeg` on the camera, then runs `tagstream`. H.264 has to decode every
frame, so it cannot skip frames to catch up.

Measured over 50 s with the tag loop and one Mac client. **[verified]**

| | Stock, 9 fps ([bring-up note](2026-11-13-john-recamera-gc2053-bringup.md)) | Patched, 27 fps |
|---|---|---|
| Frames reaching `tagstream` per second | 9–11 | 3.4–11 |
| Detections per second | 5.8 | 2.4–5.9 |
| Stream at the Mac | 9 fps | 27 fps, held for 44 s |
| CPU idle | 0% | 0% |
| Data queued for the on-camera `ffmpeg` | Not measured | 308 KB after 50 s |

The queue means the tag loop is working on old frames. At the stream's bitrate that is seconds of delay, not
milliseconds. **[calculated]**

**One stall.** In the first test the tag loop was running without the agent noticing. The Mac received 212 frames
and then nothing. Three more attempts to open the stream got no frames. The Mac's connections sat unread on the
camera, while the encoder kept running. Restarting the service cleared it. The slow on-camera client is the
likely cause. That is **[assumed]**: it happened once and was not reproduced.

## Options

1. **Keep 27 fps and detect off the camera.** The laptop decodes 27 fps easily. This sends video off the camera,
   which D-037 rules out for the final robot. Fine for bench work.
2. **Go back to stock for the tag loop.** 9 fps and 5–6 detections per second, as before.
3. **Read frames straight from the video hardware.** No H.264 decode on the camera, so `ffmpeg`'s share of the
   core (about a third) goes to detection, and frames are 75 ms fresher. This is the real fix for on-camera
   detection. It needs the cross-compile toolchain, which is not on John's Mac.

## Camera 2 state

| | Now |
|---|---|
| Stream service | Patched copy, mounted for this boot only |
| Stream | 640 × 480, 26.6 fps, no login, port 554 |
| Tag loop | Off. The boot inject node in the flow is disabled, and that survives a reboot |
| `start_tags.sh` | Unchanged since the calibration update |

After a reboot the camera would run the stock service at 9 fps with no tag loop, until the inject node is enabled.

**To undo by hand:** `sudo umount /usr/local/bin/sscma-node`, then `sudo kill $(pidof sscma-node)`. The service
comes back by itself in about 7 s. Then enable the `start tag sender at boot` inject node and deploy.

Something on the camera restarts `sscma-node` within about 7 s of it stopping, and Node-RED restarts its flow
then. What does this was not identified.
