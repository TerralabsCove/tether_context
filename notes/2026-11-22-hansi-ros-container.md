---
status: draft
owner: Hansi Lee
last_reviewed: 2026-11-22
---

# ROS 2 container for the ESP-NOW link (2026-11-22)

Written by Hansi's AI agent on 2026-11-22. Not authoritative. Summary only: the code and how to run it are in
[TerralabsCove/tether_ros](https://github.com/TerralabsCove/tether_ros) (private, commit `1f65b66`), starting at its
README. This is the "ROS: write modules and connect the sim" item for Monday 11/23 in the
[final push schedule](../plans/final-push-schedule.md), and a first answer to
[open question 13](../truth/open-questions.md) (the 3 modules acting as one arm in ROS).

## What it is

- A ROS 2 Jazzy Docker image that runs on a Mac (Apple Silicon) or Linux laptop. To ROS, the wireless link
  looks like a cable: joint states out, joint targets in. **[as built]**
- Motors: speaks the tethersmall USB-gateway protocol
  ([PROTOCOL.md](https://github.com/TerralabsCove/tethersmall/blob/main/deploy/PROTOCOL.md)), the link measured in the
  [C5 range test](2026-10-28-hansi-c5-range-test.md). Not the tether_controls Wi-Fi/UDP firmware, which the
  [10-20 run logs](2026-10-20-hansi-straightline-run-logs.md) measured as much slower.
- End camera: reads tether_camera's `pc_master` C5 ([11-21 note](2026-11-21-hansi-camera-c5-tags-on-master.md)) and
  publishes tag poses and TF frames.
- Docker on macOS cannot pass USB devices in, so a small relay on the Mac exposes each C5's serial port over TCP.
- The sim can use the same topics (`/tether/joint_command` in, `/joint_states` out), so ROS code works with the sim or
  the arm unchanged.
- The arm boots limp. Enable is refused until the joint calibration is confirmed and every joint reports fresh state
  with no fault. Any fault or stale joint drops it back to limp. The firmware's own limits still apply.

## Tested

- Against a fake gateway and fake camera only: joints followed commands, tags and TF arrived, estop and the
  stale-link cut-off worked. **[verified]** in software only (2026-11-22). No hardware yet.

## Still to do

- Run it on the real gateway and the straight-line arm. Re-run tethersmall `deploy/calibrate.py` first: the joint zeros
  in its config are from 10-19, before the C5 swap.
- The full 7-motor arm config is a placeholder. Which motor drives which URDF joint, and the signs and zeros, are
  unknown. D-026 puts three motors on each side module's CAN bus, and tethersmall's node firmware drives one joint
  motor per board, so the module firmware needs to settle first (open question 13).
- A second end camera needs its own `pc_master` C5 and a second camera node.
