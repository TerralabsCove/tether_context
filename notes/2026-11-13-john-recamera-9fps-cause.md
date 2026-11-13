---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera 9 fps cap: cause and fix options (2026-11-13)

Written by John's AI agent from a working session with John on 2026-11-13. Not authoritative. It follows the
[GC2053 bring-up note](2026-11-13-john-recamera-gc2053-bringup.md), which measured the cap. Raw counters and frame
times are in [2026-11-13-john-recamera-9fps-cause/](2026-11-13-john-recamera-9fps-cause/). Nothing here changes
`truth/`. Nothing on the cameras was changed.

## Bottom line

- **The cap is a buffer shortage in Seeed's streaming service, `sscma-node`.** The service gives the video pipeline
  4 frame buffers. The H.264 encoder holds 3. The scaler refuses two sensor frames in three. **[verified]** on
  camera 2 for the counters; mechanism from two outside sources.
- **It is fixable.** A bigger buffer pool is reported to give 28–30 fps. **[assumed]**: not tested on our cameras.
- **The values are compiled in.** No Node-RED or config-file setting changes them. **[source code]**
- **John's plan:** stay at 9 fps for now. See [Plan](#plan).

## Viewing the stream

The quick way to see the field of view from the Mac, with the camera on USB:

```bash
ffplay -rtsp_transport tcp -fflags nobuffer -flags low_delay -framedrop -x 960 -y 720 rtsp://192.168.42.1:554/live
```

Camera 2's 640 × 480 stream is letterboxed. The picture fills about 640 × 360, with grey bars above and below
(background colour `0x727272` in the scaler settings). So the frame is the 16:9 sensor image scaled down, not a 4:3
crop. **[verified]** from one frame; the frame itself was not saved.

## What was measured

Camera 2 (GC2053 + fisheye, OS 0.2.4), 640 × 480, read on 2026-11-13 while streaming. The on-camera tag loop and
one Mac viewer were connected. **[verified]**,
[counters](2026-11-13-john-recamera-9fps-cause/pipeline_counters_camera2.txt),
[frame times](2026-11-13-john-recamera-9fps-cause/stream_frame_times.txt)

| Counter | Value | Meaning |
|---|---|---|
| Stream rate at the Mac | 9.3 fps (168 frames in 18.0 s, median gap 112 ms) | Same cap as 11-12 |
| `VIDevFPS` | 27 | Sensor delivers 27 fps |
| `VIFPS` | 9 | One frame in three is processed |
| `VIDropCnt` | 0 | The input stage drops nothing |
| Scaler driver `TrigCnt` | 40,175 | One trigger per sensor frame |
| Scaler driver `FailCnt` | 26,761 (66.6%) | Two triggers in three are refused |
| Scaler driver `IrqCnt` | 13,411 | One in three completes |
| Buffer pool 2 | 4 blocks of 460,800 bytes, `Free 0`, `MinFree 0` | The pool has never had a free block |
| Pool 2 blocks held | VPSS 4, VENC 3 | The encoder holds 3 of the 4 |
| Scaler channel 2 | `Depth 3`, bound to the encoder | |
| CPU | 0% idle: `tagstream` 40%, `ffmpeg` 33% | The tag loop uses the whole core |

The kernel log has no buffer error messages. They are likely below the log level. **[assumed]**

## Cause

The sensor sends 27 frames a second. Each frame needs a free output buffer before the scaler (VPSS) can start.
`sscma-node` makes a pool of 4 buffers per video channel. The encoder keeps 3 in flight. One is left, so the
scaler can only accept every third frame. 27 fps becomes 9. The 112 ms "scaler time" in the bring-up note is this
wait, not real work.

Two outside sources report the same mechanism and the same fix on this chip:

- **Open pull request**
  [Seeed-Studio/sscma-example-sg200x#45](https://github.com/Seeed-Studio/sscma-example-sg200x/pull/45), "fix 10fps
  stream limit", opened 2026-11-09, last updated 2026-11-11. It raises the pool to 6 blocks for encoded channels.
  The author reports 30.0 fps in the description and 28.1 fps in a later comment, on an OV5647. The author is an
  outside contributor. No review yet.
- **Community write-up**
  [ROOT_CAUSE.md](https://github.com/xr686/recamera-rtsp30/blob/main/docs/ROOT_CAUSE.md). Same program, only the
  buffer settings changed: 4 blocks with depth 3 gave 10 fps; 8 blocks gave 30 fps; 4 blocks with depth 1 gave
  30 fps. Their counters match ours: `FailCnt` at two thirds of `TrigCnt`, pool `Free 0`.

The two sources explain the detail differently. The pull request blames the encoder's 3 held frames. The write-up
blames the scaler's depth-3 queue. Both agree that 4 blocks is too few. Which detail is right is not settled here.

**Where the values come from.** **[source code]**

- `vb_blk_num = 4` and `u32Depth = 3` in
  [video_paramparse.c](https://github.com/Seeed-Studio/sscma-example-sg200x/blob/main/components/sophgo/video/src/video_paramparse.c),
  lines 11 and 98.
- Seeed set them in September 2025: pool 2 → 4 in commit `3f4e9d9` (2025-09-08), depth 0 → 3 in commit `c7d4ca3`
  (2025-09-12, "perf: increase FIFO depth"). Whether older OS versions ran faster was not checked.
- Newer source has a per-channel `blkcnt` override in `video.h`, added in September 2026. Whether the camera node
  exposes it to the user was not checked.
- OS 0.2.5 (2026-10-26) and 0.2.6 (2026-11-02) are out. Our cameras run 0.2.1 and 0.2.4. Their
  [release notes](https://github.com/Seeed-Studio/reCamera-OS/releases) do not mention an fps fix. Not tested.

**Correction to the bring-up note.** It says our cameras show `StartFailCnt 0` where the write-up reports
thousands of failures. That compared the wrong counter. The write-up's counter is the driver's `FailCnt`, and ours
matches it (table above).

## Fix options

| Option | Work | Notes |
|---|---|---|
| 1. Rebuild `sscma-node` with a bigger pool | A few hours **[assumed]** | Source is open. Seeed's [README](https://github.com/Seeed-Studio/sscma-example-sg200x#readme) documents the build: prebuilt SDK, `cmake`, a `.deb` installed with `opkg`. The toolchain is x86-64 Linux only. John's Mac is Apple Silicon with no Docker, so it needs a Linux machine or a cloud build. Tag `0.2.4` matches camera 2's OS. Keep the stock binary as a backup. |
| 2. Wait for Seeed | None | The pull request may merge and ship in an OS update. No date. |
| 3. Our own capture program | Most | Reads frames from the video hardware and sets its own pool. Also removes the 640 × 480 decode limit from the bring-up note. |

The third-party publisher from the write-up is a fourth route. The bring-up note already covers it: unlicensed,
replaces Seeed's services.

## What to expect from a fix

All **[assumed]** until tested on our cameras.

- **About 27–28 fps, not 30.** Our sensor reports 27.
- **More video memory at 1080p.** A 1080p buffer is 3.1 MB, so 6 or 8 blocks add 6–12 MB. The camera's video
  memory budget was not read. At 640 × 480 a buffer is 0.46 MB and the cost is small.
- **On-camera detection may not gain, and could lose.** Camera 2's one core is already full. `ffmpeg` spends a
  third of it decoding 9 fps. At 27 fps the decode would want about three times that. The gain is for viewing and
  for anything that processes the stream off the camera.

## Plan

John, 2026-11-13:

1. Continue at 9 fps.
2. Do the camera calibration and try AprilTags.
3. If there is still trouble, "rewrite the Seeed service". John did not say whether that means option 1 or
   option 3.

This is John's working plan, not a team decision. No D-number.
