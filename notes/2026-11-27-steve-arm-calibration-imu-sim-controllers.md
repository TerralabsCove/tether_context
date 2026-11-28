---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-27
---

# Arm session: calibration poses, first driven take, battery frames, IMU-based sim model and controllers (2026-11-27)

Written by Steve's AI agent on 2026-11-27, from a session with Steve at the arm (night) and at the laptop (evening).
Not authoritative. Follows the [11-26 teleop note](2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md), John's
[on-arm IMU note](2026-11-26-john-imu-on-arm-bringup.md) and the
[IMU merge note](2026-11-27-steve-imu-merged-laptop-reader.md). Touches open questions
[25](../truth/open-questions.md) (battery protection) and [31](../truth/open-questions.md) (using the IMUs).

Code is merged: tether_ros `main` at `d54cb0f` (PRs 7 and 8), tethersim `main` at `27c365a` (PR 3). tethersmall
`steve/battery-telemetry` (`26bb68e`, draft PR 10) is on two boards and not merged.

**What was and was not done on the arm.** The arm was calibrated, mirrored and driven: one 11.5 min take with the
motors enabled, teleoperated through the sim with the stock controller. The full-rate log of that take was lost
(below). Everything about the sim's motor model and the new controllers is from the sim; none of it has run on
the arm.

## The arm as it stood

| | |
|---|---|
| Grounded end | EE_1, on the floor port disc, not locked. Board 13's motors (esc 0x03, 0x06, 0x05) are at that end. **[verified]** by Steve moving joints by hand and watching the sim |
| Free end | EE_2. Board 11's motors (esc 0x01, 0x02, 0x07) |
| Bridge mapping | `--flip-ends`, `--ground-end EE_1`; the two end pitch joints (`Revolute_22`, `Revolute_29`) run opposite to the sim and are reversed (`signs`). **[verified]** by hand for those two. The other five directions were not checked by hand |
| Boards 10 and 11 | tethersmall `steve/battery-telemetry` at `26bb68e`, flashed this session. **[as built]** |
| Boards 12 and 13 | unchanged, `45c56ff` |

The 11-26 note's table has board 11 at the base. In this session it was at the free end.

## Calibration

Zero is the straight-up stance of the sim's `single_ee` scene. Other poses are joint offsets from it in tether_ros
`tools/arm_calib_poses.json`; calibrating at a pose sets each motor's zero to its reading minus the offset, so the
arm can be calibrated lying down.

- `floor_rest`: EE_1 on the disc, its wrist turned so the arm lies square to the direction of the port's tag
  (−75°), grounded pitch 106°, middle 14°, free-end pitch −12°, free-end wrist −75°. Set by Steve with the sim's
  joint sliders against the arm and rounded. **[as built]**
- Readings survive a power cycle: after board 11 was powered off, reflashed and powered on, its pinned joints read
  the same to 0.1°. **[verified]** on two joints.
- Repeat calibrations at `floor_rest` moved the roll joints by about 180° and the middle joint by about 43°: the
  pose does not pin the rolls, the wrists or which way the arm is laid. Marks on those joints are still needed.

## Battery frames (open question 25)

Board 11 and the gateway run firmware that reads each motor's trip settings at boot and sends a `T_POWER` frame
(`0x08`) once a second. Through the gateway, 13 frames in 12 s: **[verified]**

| Motor | esc | Type | `UV_Value` | `OV_Value` | Bus voltage register (60) |
|---|---|---|---|---|---|
| 0 | 0x01 | DM-J4340P | 15.0 V | 32.0 V | answers 0.0 |
| 1 | 0x02 | DM-J10010L | 15.0 V | 54.0 V | answers 0.0 |
| 2 | 0x07 | DM-J4340P | 15.0 V | 32.0 V | answers 0.0 |

- **The undervoltage trip is 15.0 V on these three motors**, 2.5 V per cell: the motors do not protect the packs.
  Nothing was written to any motor.
- **No live voltage from the motors.** Register 60 is listed as bus voltage in Damiao's newer manuals; ours answer
  zero. The laptop ignores readings outside 12 to 30 V, so the battery panel is still an estimate.
- Motor control on board 11 was unaffected in a 12 s listen at rest and through the driven take (no fault status on
  any frame). **[verified]** for those two runs only.
- Boards 12 and 13 were not flashed; their motors' settings are unread.

## The driven take, and what was lost

One take, 691 s, motors enabled for about 674 s, driven from the sim with the stock controller (gains 150 / 4.5 big,
40 / 1.5 small, command slewed at 0.5 rad/s, gravity feedforward from the sim). From the log before it was lost:
all 7 motors at 195 to 198 Hz with 0.9 to 2.5 % of reports lost, no fault status, warmest motor 40 °C; three IMUs
at about 95 Hz with 3.8 to 4.9 % lost. **[verified]**, but the log is gone.

**The log was deleted.** tether_ros kept recordings in a git-ignored `logs/` folder in the repo. On the afternoon of
11-27 a clean-up of `~/git` on Steve's laptop removed it: every recording from the night, including this take's
200 Hz joint states and torques. Not in the Trash, no backup covering it. What survived is the sim's own 30 Hz
recording of the take (three IMUs, commanded targets, the simulated arm) and the bridge's text log. Recordings now
go to `~/Documents/tether-arm-logs/`.

## What the surviving IMU data gave

Method: the commanded joint motion run through the sim's kinematics, compared with each IMU's gyro and orientation
(tether_ros `tools/sim_fit/`). Everything here is **[inferred]** from one take, without encoders to check against.

- **Where the IMUs sit.** Each IMU's motion matches one body of the arm: IMU 13 the big motor at the grounded end
  (between the wrist and the pitch joint), IMU 12 the middle motor, IMU 11 the big motor at the free end. Not
  confirmed by eye.
- **Joint directions.** Of 64 combinations, the configured one fits best; flipping any pitch joint is clearly
  worse. A combination with the grounded wrist and both rolls reversed together fits equally and cannot be told
  apart this way.
- **Lag.** The arm follows its commands about 0.2 s late (including about 40 ms of IMU streaming).
- **Motion that was not commanded.** After fitting each IMU's mounting, the arm rebuilt from the IMUs deviates from
  its commands by 0.9 to 2.1° rms per joint (peaks 5 to 11°), and the grounded end rocks by 1.9° rms (up to 6.4°).
  Slow yaw, constant offsets and the free-end wrist are not observable.

## Sim: a motor model of the real arm

tethersim can run its arm through the real motor loop instead of its ideal controller (`motors: real`): the
bridge's gains, a command slewed at 0.5 rad/s and delayed 60 ms, gravity feedforward at 50 Hz. Scored as the rms
angle between the three IMU bodies in the sim and in the IMU reconstruction:

| | Ideal controller | Real motor model |
|---|---|---|
| Whole take | 6.7° | 3.5° |
| Four busiest 30 s windows | 14.0° | 5.0° |
| Four other windows | 5.2° | 3.2° |

About 3.5° is not explained; the commanded pose with no dynamics scores 3.8°. So the model reproduces the lag and
little of the swing or the rocking, or the reconstruction is that noisy: this data cannot say which. Fitting joint
friction, give at the dock and a gravity scale helped the windows they were fitted on (4.3°) and not the others
(3.3°), so none of that is in the sim.

## Controllers

On that model, standing, 30 to 60° moves:

| Controller | Speed | Easing | Worst overshoot | Grounded pitch settles | Free-end peak acceleration |
|---|---|---|---|---|---|
| Stock (as run) | 0.5 rad/s | none | 17.6 % | 5.8 s | 2.6 m/s² |
| Smooth | 0.5 rad/s | 0.3 rad/s² | 0.4 % | 2.3 s | 0.6 m/s² |
| Brisk | 0.5 rad/s | 0.5 rad/s² | 4.9 % | 4.7 s | 1.4 m/s² |
| Fine | 0.2 rad/s | 0.12 rad/s² | 0.6 % | | |

- The joint that rings is the grounded pitch: it swings the whole arm (5.5 kg m² standing) against a motor whose
  damping gain is at most 5 in the MIT frame. A command that stops dead leaves it ringing; easing the command in
  and out is what removes it. Smooth moves arrive about 1.2 s later.
- Extra damping sent from the laptop as feedforward torque, plain or scaled by inertia, made the model unstable at
  every setting tried (it arrives a tick and the link delay late). It is not offered.
- The controller is picked in the sim's Drive panel (or `C` while driving); the bridge follows it. Tested on the
  fake gateway only.

## Not tested

- Any controller but Stock on the arm, and the sim's motor model against full-rate encoder data.
- Directions of the wrists, rolls and middle joint by hand.
- Battery frames from boards 12 and 13; the resting-voltage correction of the battery percentage on real frames.
- IMU placement by eye; IMU mounting orientation other than as fitted per take.

## Open

- Raise `UV_Value` on the motors, or fit pack alarms: the 15 V trip does not protect a 6S pack (question 25).
- A real pack voltage: a divider into an ADC pin per module (the firmware path exists, off by default; the only
  free ADC pin is the IMU's INT), or another register if one exists.
- A fresh driven take with the full-rate log kept, to tune gains and to tell swing from reconstruction error.
- The viewer cannot hide the arm; the sim reports hidden parts far below the scene instead. A proper viewer build
  needs the machine that normally builds it: a from-scratch WebGL build of the tethersim checkout rendered black.
