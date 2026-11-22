---
status: draft
owner: Hansi Lee
last_reviewed: 2026-11-22
---

# Camera tag data reaches the master C5 over ESP-NOW (2026-11-21)

Written by Hansi's AI agent on 2026-11-22. Not authoritative. Summary only: the write-up, code and raw results are in
tether_camera, [docs/2026-11-21-espnow-link.md](https://github.com/TerralabsCove/tether_camera/blob/main/docs/2026-11-21-espnow-link.md)
(commit `38c63f0`). Touches [open question 7](../truth/open-questions.md) (camera data path) and follows the
[USB host note](2026-11-20-john-recamera-usb-host-c5.md).

## Result

- AprilTags detected on the camera reached the master C5 on the laptop over ESP-NOW, using the USB-first plan
  ([D-049](../truth/decisions.md)): the camera acts as USB host to its C5. The UART fallback was not needed. **[verified]**
  (tether_camera write-up).
- Camera 2 only. A tag 36 cm out gave 24–29 reports a second with nothing lost once running. Object messages ran at
  12–14 a second. Cold start to data on the laptop took about 2.5 min with nothing done by hand. **[verified]**
- C5s about 1 m apart on a bench. No motors, no other radios.

## Differences from the arm setup

- **Radio channel.** This link ran on 2.4 GHz channel 1. The arm link was measured on 5 GHz channel 36
  ([C5 range test](2026-10-28-hansi-c5-range-test.md)), and tethersmall measured channel 1 as lossy near Wi-Fi.
  Which channel the end-effector link uses on the arm is not decided.
- **Power.** The camera and its C5 were powered from a USB-C splitter. The camera's one USB-C is also its power input,
  and it reboots if unplugged. On the arm, both run from the end effector's 3S pack and LM2596 buck
  ([robot.md](../truth/robot.md)). Not tested on that supply.
- Camera 2 dropped off USB and Wi-Fi twice about 26 s after boot and needed a power cycle. Not explained. A power or
  cable glitch is the likeliest cause **[assumed]**.

## Still to do

- Install the bridge on camera 1. Nothing is on it yet.
- Run the link on end-effector power, with the servos moving, and measure the voltage at the camera
  ([open question 20](../truth/open-questions.md)).
- Run it with the module radios live and check the tag rate at the master.
