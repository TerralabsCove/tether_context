---
status: draft
owner: John Peng
last_reviewed: 2026-11-13
---

# reCamera camera 2 lens calibration at 1080p (2026-11-13)

Written by John's AI agent from a working session with John on 2026-11-13. Not authoritative. Script, result and
views are in [2026-11-13-john-recamera-lens-calibration/](2026-11-13-john-recamera-lens-calibration/). At John's
request the same session updated `truth/`: D-046, the end camera row in `robot.md`, `project.md` and
`open-questions.md`.

## Bottom line

- **Camera 2 is calibrated at 1920 × 1080.** Focal length 1065 px, principal point (966, 552), almost no
  distortion. **[verified]**, [calibration.json](2026-11-13-john-recamera-lens-calibration/camera2-1080p/calibration.json)
- **Field of view: 84.6° H × 53.9° V, 92.5° diagonal.** **[verified]** for V. H and diagonal are extrapolated a few
  degrees past the outermost board corners.
- **The lens is the GC2053 board's stock lens, not the fisheye.** The numbers match its spec (84° H / 54° V /
  93° D), and John confirmed it. The team keeps it: **[decided]** [D-046](../truth/decisions.md). See [Lens](#lens).
- **Camera 2's tag loop now uses the calibrated values.** Before, its distances read about 1.65 times too far.
  **[calculated]** Distance against a measured range is not yet checked.

## Result

Camera 2 (GC2053 board, OS 0.2.4), 1920 × 1080 stream, 40 views, 1,102 board corners. **[verified]**

| Value | Result | Spread across resampled views |
|---|---|---|
| fx, fy | 1065.0, 1063.6 px | ± 4.2 px (0.4%) |
| cx, cy | 966.1, 552.1 px | ± 3.1, ± 2.7 px |
| Distortion k1, k2, p1, p2, k3 | −0.0067, −0.0139, −0.0001, 0.0003, 0.0101 | Not resampled |
| Fit error | 1.34 px RMS, worst view 2.5 px | |
| HFOV / VFOV / DFOV | 84.6° / 53.9° / 92.5° | |

Model: OpenCV pinhole. The fisheye model gave the same error (1.344 px), so the tie goes to the simpler one. A
model with no distortion at all fits almost as well (1.37 px).

**The values hold up.** Fits on halves and on the best 20 or 30 views keep fx within 1063–1066 px and the
principal point within about 5 px in x and 10 px in y. There is no pattern in the error by distance from the image
centre, so the lens model is not the limit.

**Derived values for the other stream sizes.** The scaler shrinks the whole 1080p picture, and adds 60 px grey bars
top and bottom at 640 × 480. **[assumed]**: calculated from the 1080p result, not measured.

| Stream | fx | fy | cx | cy |
|---|---|---|---|---|
| 1280 × 720 | 710.0 | 709.1 | 643.9 | 367.9 |
| 640 × 480 (letterboxed) | 355.0 | 354.5 | 321.7 | 243.7 |

## Limits

- **Fit error is 1.34 px.** The 11-05 run on the old sensor got 0.30 px. The error is larger on close, blurry
  views (correlation −0.67 with distance, −0.52 with sharpness) and not on shaky ones (0.08 with hand movement).
  So the cause is focus, not motion. **[verified]**
- **The lens is focused far.** Board sharpness rises steadily from 20 cm to 45 cm. That fits the stock lens's
  factory focus of 39–69.5 cm ([11-12 note](2026-11-12-john-recamera-gc2053-swap.md)). Tags closer than about
  30 cm will be soft.
- **Edges are thin.** No corners in the top 100 rows, the bottom 185 rows, the left 118 columns or the right 218
  columns. Corners reach 38.9° off axis. The image corners are at about 46°.
  [coverage.png](2026-11-13-john-recamera-lens-calibration/camera2-1080p/coverage.png)
- **Few tilted views.** Median tilt 6.9°, maximum 36.9°. No views from above or below, and none closer than 24 cm.
- **Square size is from the screen's reported size, not a ruler** (27.49 mm). This does not affect the lens values.
  It would scale distances in a pose test.
- **One camera, one focus setting.** Camera 1 is not calibrated. Refocusing the lens voids this.

## Lens

Before this run, `truth/robot.md` (end camera row) and the
[bring-up note](2026-11-13-john-recamera-gc2053-bringup.md) said both cameras had the M12 fisheye fitted. Camera 2's
measured view is 84.6° H with almost no distortion.

| Lens | Focal length | HFOV on the GC2053 |
|---|---|---|
| Stock S401 lens | 2.9 mm | 84° (module drawing, cited in the [11-12 note](2026-11-12-john-recamera-gc2053-swap.md)) |
| Seeed 1.8 mm fisheye | 1.8 mm | 160° advertised, about 135° calculated ([11-12 note](2026-11-12-john-recamera-gc2053-swap.md)) |
| Camera 2, measured | 2.98 mm at 2.8 µm pixels **[calculated]** | 84.6° |

**John, 2026-11-13, after the run:** the cameras have the default lens that came with the GC2053 board. The
board still has the M12 mount. The agent took this to cover both cameras. Only camera 2 was measured.

**John, same day:** the current lens works. Its field of view is enough, and the team did calculations for it.
The agent has not seen those calculations, and they are not linked here. John confirmed again that this is the
GC2053 board's stock lens, on the board the team fitted to the camera.

John then said the team agrees the stock lens is enough, and asked for `truth/` to be updated:

- [D-046](../truth/decisions.md) logs it and supersedes the "must be fisheye" part of D-037. The rest of D-037
  stands.
- The end camera row in `truth/robot.md` now says stock lens, with camera 2's measured field of view.
- `truth/project.md` no longer says fisheye.
- The "Is the reCamera fisheye?" conflict is removed from `truth/open-questions.md`.

The fisheye claims in the bring-up note and the 9 fps note are wrong. Both are now corrected.
The range estimates in the bring-up note that assume the fisheye do not apply to the lens as fitted.

## Tag loop

`start_tags.sh` on camera 2 ran `tagstream 640 480 586 586 320 240`. The 586 was the old OV5647 estimate. Reported
distance scales with focal length, so those readings were about 586 / 355 = 1.65 times too far. **[calculated]**

At John's request it now runs `tagstream 640 480 355.0 354.5 321.7 243.7`, the calibrated values at 640 × 480.
**[as built]**, [start_tags.sh](2026-11-13-john-recamera-lens-calibration/start_tags.sh). The old script is kept on
the camera as `start_tags.sh.2026-11-13-before-calibration`. After the restart the Mac received its heartbeat on
UDP port 5005, at 4–8 detections per second, with no tag in view. No distance was checked.

`tagstream` takes no distortion values. The measured distortion is small enough to ignore for now. **[assumed]**

Expected pixels across a 5 cm tag at 640 px wide, from fx = 355: 59 px at 30 cm, 36 px at 50 cm, 18 px at 1 m.
**[calculated]**

## Distance check: not done yet

John started a check of reported distance against a tape and stopped it. No ruler was to hand, and no distance was
recorded. To be done later.

- [distance_check.py](2026-11-13-john-recamera-lens-calibration/distance_check.py) is ready. It draws tags 2, 1 and
  0 on the Mac screen at 79.9, 50.0 and 29.9 mm, with a 100 mm bar to check with a ruler. It asks for 30, 50, 75,
  100 and 150 cm, lens front to screen, and records 2 seconds of readings when `1` is pressed.
- The on-screen tag sizes come from the Mac's reported screen size. **[assumed]** until the bar is measured.
- One thing seen in passing: with the camera roughly square to the screen, the three tags reported 35.4, 34.8 and
  35.2 cm. They agree with each other. The true distance was not measured, so this does not check the calibration.
  [raw log](2026-11-13-john-recamera-lens-calibration/camera2-distance-check/raw_second_run_nothing_recorded.jsonl)
- Handheld, each tag's distance wobbled about 0.5 cm at about 33 cm. **[verified]** from the same log.

## How it was done

The 40 view images (`view_000.png` to `view_039.png`, 31 MB) are not in git. They are on John's Mac in the
`camera2-1080p/` folder. `--analyze-only` needs them to refit.

- [calibrate_lens.py](2026-11-13-john-recamera-lens-calibration/calibrate_lens.py), adapted from the 11-05
  [calibrate_screen.py](2026-11-05-john-recamera-test/calibrate_screen.py). It draws a 10 × 6 ChArUco board full
  screen on the Mac, fits a pinhole and a fisheye model, and reports which fits. `--selftest` renders both lens
  types with known values and checks they are recovered. It passes at 1920 and 640 px wide.
- First try stalled at 1 view in several minutes. The "hold still" test (1 px over four frames) was too strict
  for a handheld camera. It was loosened to 3 px between frames. The second try saved 40 views in 8.4 minutes.
  Even then, 1,644 frames were turned away for movement and 1,498 had no board in view
  ([capture_log.csv](2026-11-13-john-recamera-lens-calibration/camera2-1080p/capture_log.csv)).
- The one view from the first try is kept as `first_try_view.png`. It is not in the fit.

## Camera state

Camera 2 was switched to 1080p for the run, with the boot tag loop off. Both were put back from a backup of the
flow. Checked after: 640 × 480 stream, `start_tags.sh` running, camera node option `2`. The camera did not reboot.

## Next

1. Link the team's field of view calculations from D-046. If the lens is ever changed or refocused, calibrate
   again.
2. Run the distance check with a ruler and a tape: `python3 distance_check.py --out=camera2-distance-check`.
3. Check the derived 640 × 480 values with a short run at that size.
4. For a tighter fit: add views at the top and bottom edges and from above and below, at 35–50 cm where the lens
   is sharp.
