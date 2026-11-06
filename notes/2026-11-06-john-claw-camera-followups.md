---
status: draft
owner: John Peng
last_reviewed: 2026-11-06
---

# Claw camera follow-ups: reCamera lenses, Pico, stereo (2026-11-06)

Written by John's AI agent from a working session on 2026-11-02 to 11-06. It follows the
[claw camera picks note](2026-11-02-john-claw-camera-picks.md). This is analysis, not a decision. Nothing here
goes into `truth/` yet. Using onboard camera compute still reverses [D-013](../truth/decisions.md) and needs a new
decision row.

Prices were checked on seeedstudio.com and by web search. Stereo prices from third-party listings need rechecking
before anyone orders.

## Where we are

1. **The reCamera 2002w 64GB detects tags on its own.** See the first test below. Wireless is still untested.
2. **Don't buy a fisheye yet.** First check whether the stock lens keeps the tag in view from the offset camera
   position, at the start and end of docking.
3. **A Pi Pico can't replace the reCamera.** It can't hold a full frame in memory.
4. **Stereo may not be needed for docking.** A single camera gets depth from a tag of known size. If we need depth
   on untagged things, the arm can move the camera we already have, for $0.

## First reCamera test (2026-11-05)

Printed tag36h11 sheet, camera connected to a Mac over USB. The camera ran detection, and the Mac only displayed
the results. All values are from one handheld run.

| Check | Result |
|---|---|
| Tags read | IDs 0, 1 and 2, including two in one frame |
| Smallest tag read | 3 cm tag, about 70 px wide |
| Agreement between tags on one sheet | `z` of 25.2 and 25.1 cm |
| Steadiness | `z` within about 0.2 cm; `x` and `y` drifted a few mm |
| Angles | Yaw and pitch wobbled a few degrees per frame, so they are noisier than position |
| Spacing between tags 0 and 1 | Reported 1.1 and 5.6 cm; sheet is about 1.0 and 5.5 cm |
| Detection time | Mostly 100–150 ms, with spikes to about 320 ms |
| Update rate | About 3–8 detections per second |

Not proven yet:

- **Absolute distance.** The focal length was a guess, so `z` isn't confirmed. Next check: hold the 5 cm tag at a
  tape-measured 30 cm and compare.
- **Wireless.** This run came over USB.

The camera also restarted once for an unknown reason. Its apps don't start on their own after a restart.

The test files are local at `notes/2026-11-05-john-recamera-test/` and are not in this push.

## reCamera 2002w fisheye

The M12 lenses do not fit the 2002w 64GB as shipped. The stock board is the S101 with an OV5647, and the wiki lists
no M12 mount. Seeed's fisheye page says the 2002 series, including SKU 102991897, needs sensor board 100041077 for
lens replacement.

| Part | Price | Details |
|---|---|---|
| [GC2053 sensor board](https://www.seeedstudio.com/reCamera-2002-Sensor-Board-GC2053-p-6556.html) | $29.90 | 1/2.9", 2 MP, 84° horizontal stock lens. Seeed says it can be installed on a finished 2002w |
| [M12 fisheye](https://www.seeedstudio.com/J0018027B-p-6647.html) | $9.90 | 1.8 mm, F1.8, 160° horizontal, manual focus, minimum object distance 0.2 m, 7 g |
| [M12 140° lens](https://www.seeedstudio.com/JY-127A025FB-3MP-p-6644.html) (alternative) | $7.90 | 2.5 mm, F2.2, minimum object distance 0.2 m. Stock not checked |

The fisheye setup is $39.80 plus shipping. On 11-02 both main parts showed stock only in the China warehouse.

What the swap changes:

- **White LEDs may be lost.** They are listed on the stock board, and the HQ PoE, which uses the GC2053, lists no
  fill light. This is inferred, not confirmed. The mic may be affected too. Plan on a separate LED.
- **Resolution drops** from 5 MP to 2 MP. Both do 1080p at 30 fps.
- **The camera needs calibrating again.** Software may also need changes. We found no install steps from Seeed.
- **The minimum object distance is 0.2 m.** That could matter at the end of docking.

Estimated pixels across a 5 cm tag at the image center with the fisheye. Calculated, not measured. Pixels fall
toward the edges.

| Image width | 20 cm | 50 cm | 1 m |
|---|---|---|---|
| 1920 px | 165 | 65 | 35 |
| 640 px | 55 | 20 | 10 |
| 320 px | 27 | 10 | 5 |

## Pi Pico instead of the reCamera

Not a useful swap. The fisheye only changes the view. The Pico would have to do the detection.

| | reCamera 2002w | Pi Pico | Pi Pico 2 |
|---|---|---|---|
| Processor | About 1 GHz, Linux | 133 MHz | 150 MHz |
| RAM | About 256 MB | 264 KB | 520 KB |
| Fits a 1080p grayscale frame (about 2 MB) | Yes | No | No |
| Camera connection | Built in | No standard port | No standard port |

These specs are from memory and were not rechecked. **[assumed]**

A 640 px grayscale frame is 307 KB, so the Pico is limited to about 320 px. With a fisheye, that leaves a 5 cm tag
readable to about 20 cm. We expect it to be at least 10 times slower than the reCamera, but nobody has measured it.

If we need more compute, the small option is a Pi Zero 2 W. If we need a smaller camera, it's the OpenMV AE3.

## Cheapest way to get stereo

The cheapest way is to move one camera with the arm. Take a shot, move a known distance, hold still, take another.
The scene must not move between shots.

Spinning the gripper joint is the best move to try. The camera sits off the dock's center line, so the spin swings
it in a circle. A 90° spin moves it about 1.4 times its offset. It relies on one joint rather than the whole arm,
which matters because encoders [drifted last time](../truth/open-questions.md). Mech hasn't given us the offset yet.

The spin also rotates the image, so plan on matching individual points rather than building a full depth map.

Estimated error for a 5 cm move, using the stock 65° lens at 1920 px wide. Calculated, not measured.

| Source of error | At 30 cm | At 1 m |
|---|---|---|
| 1 px when matching points | ~1 mm | ~13 mm |
| 1 mm in the length of the move | ~6 mm | ~20 mm |

Knowing the move matters most up close. Calibrate it with a tag at a known position.

| Option | Price | Catch |
|---|---|---|
| **One camera moved by the arm** | $0 | Scene and arm must be still, so about one reading per move |
| [ELP dual-lens USB module](https://summet.com/blog/2023/11/17/elp-synchronized-stereo-camera-module-elp-usb960p2cam-v90) | About $45–90, third-party listings | Synced pair, but needs a USB computer at the claw, since ESP-NOW can't carry the video |
| Second reCamera | $89.90, backordered on 11-02 | 66 g each. No known way to sync them, so they would need to hold still too |
| [Arducam OV9281 stereo kit](https://www.robotshop.com/en/arducam-stereoscopic-camera-kit-w-1mp-ov9281-2x-camarray-stereo-camera-hat.html) | $173.62 | Synced global shutter, but needs a Pi or Jetson |
| [OAK-D Lite](https://checkout.luxonis.com/products/oak-d-lite-1) | $269 | Calculates depth itself, but is 91 mm wide, and its [ideal range starts at 40 cm](https://cdn.shopify.com/s/files/1/0630/8950/8583/files/OAK-D-Lite_Spec_Sheet.pdf) |

A pair of ESP32-CAMs is not worth trying. They aren't synced and have the focus problem below.

## ESP32-CAM findings

- **Close focus is a problem.** The minimum focus distance on our units is too far, and the lens on the unit we
  checked isn't threaded, so it can't be turned. Don't force it. This weakens the picks note's view that the
  ESP32-CAM is probably good enough at docking range.
- **It has no USB port.** To flash it, connect IO0 to GND, then reset. Use one of these:
  - An FTDI or CP2102 adapter, or an ESP32-CAM-MB.
  - An Uno R3 with RESET tied to GND and a voltage divider on its TX.
  - An ESP32 dev board with EN tied to GND.
  - A XIAO running a UART relay sketch, with esptool's `--before no-reset`. This one is untested.
- **The radio doesn't match.** The ESP32-CAM, S3 and C6 are 2.4 GHz only. Tether's C5 radios are planned for 5 GHz
  ESP-NOW ([D-029](../truth/decisions.md), band still open). A XIAO C6 could flash a camera, but any camera should
  still reach the network over UART through its module's C5.
