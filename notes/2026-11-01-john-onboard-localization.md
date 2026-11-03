---
status: draft
owner: John Peng
last_reviewed: 2026-11-01
---

# On-robot vision for docking and building (2026-11-01)

Written by John's AI agent from a chat between Steve Lu and John Peng on 2026-11-01. Analysis, not a
decision. Nothing here is measured. Everything is **[assumed]** unless it links to a source.

## The question

The end-effector camera needs a way to get its picture to the computer.
[Open question 7](../truth/open-questions.md) says ESP bandwidth is too low. Steve proposed putting a Raspberry
Pi on the center module to do localization and AprilTag docking on the robot, so nothing has to stream. His
proposed chain was Pi → wired master ESP → ESP-NOW → slave ESPs, with the Pi as a "middle level"
deterministic layer and the laptop doing heavy work. He was not sure the middle layer is needed for demos.
Steve then pointed out that once Tether picks up blocks and builds, one end will be somewhere other than a
known dock.

## Conclusion

Send the answer, not the pixels. Put a camera and a small vision board on the same module, wired locally.
Each board sends tag sightings of about 30–40 bytes over ESP-NOW. The laptop keeps the world map and the
planner. The tested USB gateway and control path stay as they are. This reverses
[D-013](../truth/decisions.md) (all compute offboard), so it needs a new decision before anyone builds it.

| Where | Hardware | Job |
|---|---|---|
| Center module | Pi + wide camera + IR flood light | Watch the workspace: the block pile and the placed blocks |
| Each end module | OpenMV or Pi Zero 2 W + claw camera | Line up the claw to lock onto a dock or a block top |
| Laptop | Planner + world map | Combine tag sightings with encoder positions, plan moves |
| ESPs | Unchanged | Motor control and safety |

The center camera is only needed once building is in scope. A walking-only first demo needs just the
claw cameras.

## Why

### A center Pi cannot see the claw cameras

- The claws are on the end modules ([D-005](../truth/decisions.md), [D-026](../truth/decisions.md)). The
  center module has the single master motor.
- No wire crosses a joint, because every joint spins 360° ([D-006](../truth/decisions.md),
  [one-pager](2026-10-16-john-mvp-one-pager.md)). A center Pi would still need the claw video sent to it
  wirelessly. That is the original problem over a shorter distance.
- So the claw cameras need their own vision board in the same end module, wired to that module's slave ESP
  over UART.

### Keep the USB gateway

- The all-C5 arm runs a gateway on the laptop's USB, with three slaves on 5 GHz channel 36
  ([tethersmall C5_SLAVES.md](https://github.com/TerralabsCove/tethersmall/blob/main/docs/C5_SLAVES.md)).
- Steve's chain moves the master back onto the robot. tethersmall measured that layout as worse: command
  round trip p50 of 12–55 ms and 3/5 runs passed, against 10–15 ms and 10/11 for the USB gateway. Source:
  John's local, uncommitted `wifi-latency-findings.md` in tethersmall, computed from Hansi's
  `straightline-run-logs`.
- A Pi with its own Wi-Fi would remove part of that cause, because the ESP radio would no longer run a SoftAP
  as well. But the laptop-to-robot hop would still be Wi-Fi. That only suits traffic that can wait, such as
  whole planned trajectories, not 100 Hz setpoints.
- Instead, the vision boards send tag sightings into the existing ESP-NOW link. An ESP-NOW frame holds 250
  bytes, so several sightings fit in one frame. The master location conflict in open questions is unaffected.

### Walking: position mostly comes from docking

- Tether moves like an inchworm, so one end is always anchored. If every dock has an AprilTag at a surveyed
  spot, the robot's position is that dock plus forward kinematics from the encoders.
- Each successful dock resets any error. That removes most of the "encoders drift" fallback risk in
  [D-018](../truth/decisions.md).
- This could replace the external IR camera rig from the
  [one-pager](2026-10-16-john-mvp-one-pager.md), and with it the dependence on mocap access and on the
  unknown set geometry (open questions 1 and 2). It conflicts with D-012, which made mocap primary.

### Building: blocks move, and the claw cameras go blind (Steve's point)

From the [construction concept](2026-11-01-john-construction-concept.md):

- In the tower and wall clips, one end stays in a floor dock while the other carries a block. So the robot
  still knows where it is. What it does not know is where the blocks are: the pile before pickup, and each
  block after placement.
- If Tether later anchors on a block it placed, it also loses its own position. Its anchor is then only as
  accurate as that placement.
- The carrying claw locks into the top of the block, so its camera looks into the block. The anchored claw's
  camera looks into its floor dock. Neither sees where the block is going.

What follows:

- **A workspace camera on the center module.** It is wired to a Pi on the same module, so no wire crosses a
  joint. During building the center module is up between the anchor and the load. It may have the best view
  of the pile and the tower; check this in the sim poses. It reads tags on the sides of the blocks. The Pi
  connects to the center slave ESP (`0x04`) over UART. The master does not move.
- **Claw cameras for the close-up steps.** These are locking onto a floor dock and locking onto a block top
  before lifting. The view is clear at those moments.
- **Mechanical self-alignment.** A chamfered pocket under each block slides itself over the dock below.
  Vision then only has to get the block within the chamfer's reach. That distance needs a bench measurement.
- **Look after each placement.** After releasing a block, observe it and record where it actually landed. The
  next block goes onto the block as it really sits, so errors do not stack up the tower.
- **Map on the laptop.** Each sighting carries the tag ID, the pose, which camera saw it, and a timestamp.

## Constraints to design around

- **Dim light** ([open question 3](../truth/open-questions.md)). Each camera needs its own light. Use white
  LEDs, or an IR LED with a NoIR camera and retroreflective tags. A wide workspace view is harder to light
  than a claw close-up.
- **Power cuts.** There is no BMS. The motors shut off at low voltage ([D-008](../truth/decisions.md)). A
  Pi's SD card can corrupt on a hard power cut, so run it with a read-only root file system. OpenMV has no SD
  card to corrupt.
- **Radio bands.** ESP-NOW is on 5 GHz channel 36. Analog FPV video, if used, is on 5.8 GHz. Keep any Pi
  Wi-Fi on 2.4 GHz.
- **Power and mass vs D-013's reason.** D-013 says compute stays offboard because the robot runs on batteries.
  Two small boards at about 2 W for 2 h use about 8 Wh. A 6S 5,000 mAh pack holds about 110 Wh. Two boards add
  about 20 g to a 14.35 kg arm ([robot.md](../truth/robot.md)). A Pi 5 draws 5–10 W.

## Board options

| Board | Good | Watch out |
|---|---|---|
| Pi Zero 2 W + Camera Module 3 (NoIR, wide) | 10 g, about 2 W, Linux and OpenCV | About 30 s boot; SD card risk; one camera port; 2.4 GHz Wi-Fi only |
| OpenMV H7 Plus | Finds AprilTags itself, instant boot, no SD risk | Lower resolution, MicroPython |
| Pi 5 | Fast, two camera ports | Heavier, 5–10 W; the two ports don't help at the ends, because the cameras are at opposite ends of the robot |

## Fallback: analog FPV video to the laptop

This applies if the team keeps all compute offboard. A tiny analog camera with a 5.8 GHz transmitter at
25 mW goes on each claw. A receiver and a USB capture dongle by the laptop make the feed show up as a
webcam. The delay estimate is about 40–80 ms. The picture is roughly 640×480 and noisy. Prices are from
Amazon on 2026-11-01.

**Combo 1: starter (about $98)**
- AKK BA3 camera and transmitter in one ($26.99): https://www.amazon.com/dp/B06Y5D8SPZ
- AKK TS832+RC832 kit ($54.99); only the RC832 receiver is used: https://www.amazon.com/dp/B01FXGQ2KC
- AV-to-USB-C capture dongle, driver-free UVC ($15.99): https://www.amazon.com/dp/B0CYC12J53

**Alternative A: not bright enough (about $74 more).** Replaces the BA3 and keeps the RC832 and the dongle.
- Caddx Ratel 2 starlight camera ($45.99): https://www.amazon.com/dp/B0GKT1Z48Z
- AKK X2-Ultimate transmitter ($27.99): https://www.amazon.com/dp/B07DPG5H1T

**Alternative B: one-piece receiver ($130).** Replaces the RC832 and the dongle.
- EWRF 5.8G UVC receiver: https://www.amazon.com/dp/B0GGHQ3L2M

Onboard boards seen on Amazon the same day: XIAO ESP32-S3 Sense ($23.99,
https://www.amazon.com/dp/B0C69FFVHH), SingTown OpenMV H7 Plus ($109, https://www.amazon.com/dp/B09WYQMDX2).
The Amazon Pi Zero 2 W listing was $85, against a $15 list price; buy from an authorized reseller instead.

## Next steps

1. Decide between onboard vision and the analog fallback. Onboard reverses D-013 and needs a new decision row.
2. Bench test: one Pi Zero 2 W with a NoIR camera, or one OpenMV, in dim light. Measure AprilTag frames per
   second, and the delay from a tag appearing to its pose arriving at the laptop over ESP-NOW. Compare with
   the analog estimate.
3. Decide whether the center workspace camera is in scope for the first demo, or only once building starts.
4. Mech: chamfered block pocket, and how much misalignment it can absorb.
