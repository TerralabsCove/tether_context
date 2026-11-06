---
status: draft
owner: John Peng
last_reviewed: 2026-11-06
---

# Claw camera picks for AprilTag reading (2026-11-02)

**Update 2026-11-06:** Later findings changed some of this. See the [follow-up note](2026-11-06-john-claw-camera-followups.md),
which covers the first reCamera test, the 2002w lens limits, Pico and stereo.

Written by John's AI agent after the 2026-11-02 evening Tether meeting with Ming
([Granola](https://notes.granola.ai/d/11b7f3e3-c2cb-4bcb-ac16-ff8f1832d989)). This is analysis, not a decision.
Nothing here is measured, so everything is **[assumed]** unless it links to a source. Prices were checked on
Amazon and seeedstudio.com on 2026-11-02.

## What the meeting settled on

- Each claw gets a camera with its own compute. It reads AprilTags itself and sends only the tag ID and pose (XYZ
  plus roll, pitch, yaw) over ESP-NOW. No video is streamed.
- Analog FPV is out because the picture is too poor for AprilTags. This replaces the 11-01 plan to send video
  through a wireless module ([Granola](https://notes.granola.ai/d/ee61c251-9192-42b7-b526-e4bd42065316)).
- The camera sits off the dock's center line, because there is no room in the middle. The tags go beside the port.
- Localization comes from a known dock plus joint states. No external localization sensor is planned.
- Plan: test the ESP32-CAMs already on hand after Wednesday 11-05, and Ming's reCamera 2002. In parallel, buy a
  camera that will definitely work. Add an LED at the claw.
- Open: this reverses [D-013](../truth/decisions.md) (all compute offboard). It needs a new decision row before
  anyone builds it. See also the [on-robot vision note](2026-11-01-john-onboard-localization.md).

## Short answer

1. **The ESP32-CAM is probably good enough at docking range.** Its limits are light, motion blur and frame rate,
   not resolution. Test it this week as planned.
2. **Order one OpenMV AE3 now ($159, arrives 11-05) as the camera that will definitely work.** It reads AprilTags
   and returns their pose with one built-in call. It is tiny and has a global shutter.
3. **Make the tags bigger before buying a higher-resolution camera.** Tag size and field of view matter more than
   megapixels.
4. **Avoid fisheye lenses at low resolution.** Very wide lenses spread a 640 px image too thin to read tags. At
   1920 px they are workable; see the [follow-up note](2026-11-06-john-claw-camera-followups.md).
5. **Wire the camera to its module's C5 over UART.** Don't run a second radio network for the cameras.

## Will the ESP32-CAM see the tags? It mostly depends on distance

The camera needs about 25 px across the tag's black square to decode it reliably, and about 40 px for a steady
pose. This is a common rule of thumb for tag36h11, not something we measured. The table shows pixels across the
tag:

| Camera setup | Tag | 10 cm | 20 cm | 30 cm | 50 cm | 1 m |
|---|---|---|---|---|---|---|
| 320 px wide, 65° (stock ESP32-CAM at QVGA) | 5 cm | 126 | 63 | 42 | 25 | 13 |
| 640 px wide, 65° (ESP32-CAM at VGA) | 5 cm | 251 | 126 | 84 | 50 | 25 |
| 320 px wide, 65° | 3 cm | 75 | 38 | 25 | 15 | 8 |
| 640 px wide, 120° (wide lens) | 5 cm | 92 | 46 | 31 | 18 | 9 |

Formula: `px = image_width × tag_size / (2 × distance × tan(HFOV/2))`.

What this means:

- Close up, at 10–30 cm during docking, even QVGA reads a 5 cm tag. So "too low quality" is unlikely to be the
  problem.
- Beyond about 50 cm, or with tags of 3 cm or less, the ESP32-CAM runs out of pixels. The fix is a bigger tag, or
  several tags around the port.
- The ESP32-CAM's real risks:
  - Frame rate: expect a few frames per second for AprilTag detection on an ESP32.
  - Rolling-shutter blur while the claw moves.
  - Noise in dim light.
  - The fix for all three is to pause the claw briefly before each reading and add an LED.
- The 120° row shows the cost of a wide lens at 640 px. It cuts the pixels on the tag to about a third of the 65° lens.

## Candidates

| Option | Price | Good | Bad | Use it for |
|---|---|---|---|---|
| ESP32-CAM (on hand) | $0 | Free; test this week | Weak camera, low frame rate, rolling shutter. Its Wi-Fi is 2.4 GHz only, so it can't join the C5 network on 5 GHz ([D-029](../truth/decisions.md)) | Bench test of the whole pipeline |
| [XIAO ESP32S3 Sense](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html) (teammate link) | $13.99 at Seeed ($23.99 on [Amazon](https://www.amazon.com/dp/B0C69FFVHH)) | 21×18 mm, 8 MB PSRAM, so VGA grayscale fits. Now ships with an OV5640 or OV3660 (up to 5 MP) | Same ESP32 compute limits and rolling shutter. The OV5640 has autofocus; lock the focus, because refocusing breaks the calibration. 2.4 GHz only | Cheap upgrade if the ESP32-CAM only fails on image quality |
| **[OpenMV AE3](https://www.amazon.com/dp/B0H8YWMRLY)** | **$159, arrives Thu 11-05** | 25×25 mm and 8 g. Color global shutter, so no motion blur. `find_apriltags()` returns pose directly. Also has a ToF distance sensor, an IMU and an NPU | MicroPython. Needs its own LED. Minimum focus distance not checked. The team called OpenMV "old"; that was the H7, and the AE3 and N6 are new boards | **Claw camera: buy now** |
| [OpenMV N6](https://www.amazon.com/dp/B0H8SSNBYK) | $225, arrives 11-04 | Faster than the AE3, global shutter, Ethernet | Bigger; more than the claw needs | Only if the AE3 is too slow |
| [OpenMV H7 Plus](https://www.amazon.com/dp/B09WYQMDX2) | $109 | Proven AprilTag support | Older and slower; rolling shutter | Not worth it now that the AE3 exists |
| [reCamera 2002](https://www.seeedstudio.com/catalogsearch/result?q=recamera%202002) (teammate link; Ming has one) | $79.90 (2002 8GB); the 2002w with Wi-Fi is $89.90, backordered to 11-25 | Four 0.3 W white LEDs built in. Linux, 1 TOPS NPU. M12 lenses need the separate GC2053 board. Its 4×0.3 W LED setup is a good model to copy for the claw light | 40×40×36.5 mm and 66 g. The OV5647 version is listed as unable to focus closer than 39 cm, yet the 11-05 test read tags at a reported 25 cm, so check this. AprilTags aren't a built-in model, so we would write C++/OpenCV on RISC-V Linux | Under test; see the [follow-up note](2026-11-06-john-claw-camera-followups.md) |
| Pi Zero 2 W + [Arducam IMX708 102° fixed focus](https://www.amazon.com/dp/B0D2QK3QXQ) | $35.99 camera + Pi | Full OpenCV, 12 MP, fixed focus (good for calibration) | About 30 s boot, SD card can corrupt on power cuts, bigger. See the [11-01 note](2026-11-01-john-onboard-localization.md) | Fallback if the team wants Linux at the claw |
| ZED stereo | $$$ | Depth | Needs a Jetson-class host. Jetson was already ruled out as too heavy ([open question 7](../truth/open-questions.md)) | No |

## How it connects

- Camera board → UART → that module's XIAO ESP32-C5 → the existing ESP-NOW link → laptop. A sighting is about
  30–40 bytes, and an ESP-NOW frame holds 250. Small sightings fit alongside the control traffic.
- The meeting floated a second ESP master-and-slave network just for camera data. That adds a radio and doubles
  the channel planning ([open questions 14 and 15](../truth/open-questions.md)). It is only worth it if the bench
  shows that sightings delay motor commands.
- Power: the camera runs from the module's 5 V buck. The AE3 and the ESP boards draw under 1 W; check the LED
  separately.

## What to measure on the bench (after 11-05)

1. Tag size and distance at which each camera stops decoding, using a printed tag36h11 at 3, 5 and 8 cm.
2. Frames per second with AprilTag detection on: ESP32-CAM, then AE3, then Ming's reCamera.
3. Pose accuracy: put the tag at a known offset and compare the reported XYZ. Calibrate each camera first, using
   the OpenCV checkerboard.
4. Dim light with and without the LED.
5. Delay from a tag appearing to its pose arriving at the laptop over ESP-NOW.

## Questions for mech

- How far is the claw camera from the tag at the moment it must read it, and what is its offset from the dock
  axis?
- How big can the tag beside the port be? From the table, 5 cm or larger keeps the ESP32-CAM viable.
