---
status: draft
owner: John Peng
last_reviewed: 2026-11-14
---

# reCamera Step 2: tag detection on frames straight from the scaler (2026-11-14)

Written by John's AI agent from a working session with John on 2026-11-14. Not authoritative. It follows the
[tag tracking note](2026-11-13-john-recamera-tag-tracking.md). Nothing here changes `truth/`.

The code, raw results and the full write-up are in the camera repo,
[TerralabsCove/tether_camera](https://github.com/TerralabsCove/tether_camera). Full write-up:
`docs/2026-11-14-vpss-capture.md` there. This note is the summary only.

Step 2 was: stop decoding the camera's own video stream with `ffmpeg`, and read frames straight from the video
hardware. The camera could not be aimed at a tag during this session, so tests with tags used saved clips.

## Bottom line

- **It works on camera 2, beside the stock service, with no patch.** `tagstream` can take frames from the
  camera's scaler (VPSS). `ffmpeg` is out of the path. **[verified]**
- **Reading the scaler lifts the camera from 9 to 27 frames a second.** The stock service leaves finished frames
  in a queue nobody reads, which starves it. A reader that empties the queue removes the cap, for the video
  stream too. The [27 fps patch](2026-11-13-john-recamera-27fps-patch.md) is not needed for this. This also
  settles the detail the [9 fps cause note](2026-11-13-john-recamera-9fps-cause.md) left open. **[verified]**
- **A frame reaches the tag program 5 ms after its time stamp.** **[verified]** for the time. What the stamp marks
  inside the camera was not checked.
- **One tag: 21.6 reports a second, sent 14 ms after the frame's stamp. Eight tags: 11.7 reports a second each.**
  Through `ffmpeg` on 11-13 it was 9 and 8.0. **[verified]** for timing, with saved clips standing in for the
  picture.
- **No real tag has been seen through this path yet.** That is the first thing to do when the camera can be aimed.
- **Hazard: never `kill -9` a program that reads the scaler.** If it dies while holding a frame, one of the
  camera's four frame buffers stays busy. Two lost buffers stall the stream. This happened in testing. The
  programs now shut down cleanly on a plain `kill`, and a script on the camera gives stuck buffers back. A reboot
  also clears it.

## Camera 2 state

Stock state: 640 × 480, stock service, 9 fps with nothing reading the scaler, no stuck buffers, boot tag loop off.
New test files are in `/userdata/atbench/`. Nothing is installed to run at boot. Camera 1 is untouched.

## Next

1. Aim camera 2 at the eight-tag screen target and repeat the 11-13 live test with the scaler source.
2. Move the once-a-second whole-picture search to a background thread. At 27 fps it is the main thing between
   one tag and the full frame rate.
3. Decide whether the scaler path becomes camera 2's boot tag loop.
