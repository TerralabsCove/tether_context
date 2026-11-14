---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera tag tracking: on-camera detection on every frame (2026-11-13)

Written by John's AI agent from a working session with John on 2026-11-13. Not authoritative. It follows the
[27 fps patch note](2026-11-13-john-recamera-27fps-patch.md) and the
[GC2053 bring-up note](2026-11-13-john-recamera-gc2053-bringup.md). Nothing here changes `truth/`.

The code, tests, raw results and the full write-up are in the camera repo,
[TerralabsCove/tether_camera](https://github.com/TerralabsCove/tether_camera). Full write-up:
[docs/2026-11-13-tag-tracking.md](https://github.com/TerralabsCove/tether_camera/blob/main/docs/2026-11-13-tag-tracking.md).
This note is the summary only.

This is step 1 of making on-camera AprilTag detection fast, so the camera sends tag positions only. Step 2,
reading frames straight from the video hardware, is not started.

## Bottom line

- **With tracking, camera 2 reports every tag on nearly every frame.** Live, stock 9 fps stream. One tag: 255 of
  258 frames and 275 of 275. Eight tags at once: all eight in 277 of 278 frames. **[verified]**
- **The old way gave 5.5 reports a second with one tag and 3.1 per tag with eight.** **[verified]**
- **The report leaves the camera about 24 ms after the frame arrives with one tag, and 42 ms for the last of
  eight.** The old way: 208 ms with one tag. **[verified]**
- **A new tag takes about 0.6 s to show up, 1.4 s at worst, and up to 1.9 s if it slides in blurred.** Tags are
  looked for across the whole picture once a second. **[verified]**
- **Once a second one report is late by about 100 ms**, because of that search. **[verified]**
- **Not tested:** tags beyond 40 cm, fast camera motion, more than eight tags. The distance check against a tape
  is still not done.
- **Not installed as the boot loop.** The new program is on camera 2 beside the old one.

## Camera 2 state

| | Now |
|---|---|
| Stream | 640 × 480, stock service, 9 fps. It was 1080p before this session |
| Tag loop at boot | Off, as before. The inject node is still disabled |
| New program | `/userdata/atbench/tagstream-track` |
| Old program and `start_tags.sh` | Untouched |
| Test clips | `/userdata/atbench/replay/`, 140 MB |

Camera 1 is untouched.

## Next

1. Step 2: read frames from the video hardware. That removes `ffmpeg`'s 35–45% of the core and its delay, and
   lets detection use the 27 fps stream. The first test and the open unknowns are in the full write-up.
2. Move the once-a-second search to the background.
3. A live run with printed tags at working distance, beyond 40 cm.

## Raised, not started: hand detection on the camera

John asked on 2026-11-13 whether the camera could also find a hand, for a fist-bump reach. Not tested.

- A hand model would run on the camera's NPU, which tag tracking does not use. Seeed reports YOLO11n detection at
  20 fps, 50 ms per frame, on this camera
  ([benchmark](https://wiki.seeedstudio.com/recamera_benchmarking/)). Not measured by us.
- Camera 2 has the stock YOLO11n detection, pose, segmentation and classification models in
  `/usr/share/supervisor/models/`. None has a hand class. A hand-trained model is needed.
- Seeed's [MediaPipe hand port](https://wiki.seeedstudio.com/recamera_hand_gesture/) logs about 290 ms per frame.
- One camera gives the direction to a hand, not its distance. A reach needs a stop rule.
- AprilTag detection itself cannot move to the NPU. It is ordinary code, not a neural network.
