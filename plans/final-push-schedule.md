---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-27
---

# Final push schedule: 11/22 to 12/3

**Demo day: Thursday 12/3, at Watt Hall B1. Be there from 5:00 PM.** (D-051)

**Goal for the end of Thanksgiving break (Sunday 11/29): the arm running on the setup.** Kept on 11/27 (John).

**Revised 2026-11-27.** The arm is assembled and wired, and it has been driven. It has not docked between two ports yet. **By the end of Friday 11/27, both end effectors are to be fully manufactured and working electrically (John, 11/27).** End effector 1 is complete mechanically. Its electronics wait on the servo buffer board, due around midday Friday. End effector 2's TAG-Mech-005 is machined and still has to be tapped. That waits on an M2.5 tap that arrives around midday Friday. The camera tags must reach the laptop by the end of Friday (John, 11/27). All 7 ports are mounted. Watt Hall B1 is open every day. The full run stays on Sunday 11/29, and the shell still goes on Monday 11/30 (John, 11/27). What is left before Sunday is under [Friday](#friday-1127) and [Saturday](#saturday-1128). The days those items land on were proposed on 11/27. Owners are not set. See [Changes](#changes).

Set at the [2026-11-21 planning meeting](../meetings/2026-11-21-final-push-planning.md) (D-050). The day lists below started as the whiteboard from that meeting: [11/22 to 11/25](../assets/2026-11-21-final-push-whiteboard-nov22-25.jpg), [11/26 to 11/29](../assets/2026-11-21-final-push-whiteboard-nov26-29.jpg). Indented lines add detail from the [transcript](../meetings/2026-11-21-final-push-planning-transcript.md). Items that moved say where they were.

This plan is tight on purpose. Things will spill over. When they do, move the item here and note it under [Changes](#changes). Tick items off as they finish.

- Both ends use Ming's end effector (D-052). See [risks](#risks-and-backups).
- People: JC is Jack Carpino. CK is Caroline Kim. "Castle" is Ming's house.

## Where things stand (11/27)

From John's answers on 11/27, the notes from 11/24 to 11/27, and the Tether Discord. Discord lines are unverified.

| Area | Status |
|---|---|
| Arm | Assembled. All three modules wired. All 7 motors streamed at about 200 Hz on 5 GHz channel 36 on 11/26 ([Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md)). Driven. Not docked between two ports yet (John, 11/27). |
| Firmware | Boards 10 to 13 run tethersmall `main`, merged 11/27 through tethersmall #9. It carries the IMU code and `COMMAND_FF` ([Steve's 11-27 note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md)). The `COMMAND_FF` limits (80 Nm big motors, 25 Nm small, kp 500) are still proposals. |
| IMUs | One BNO08X on each module, at 100 Hz, forwarded by the gateway. Tested with the arm at rest only ([on-arm note](../notes/2026-11-26-john-imu-on-arm-bringup.md)). tether_ros decodes them ([Steve's 11-27 note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md)). Getting the IMU data streaming was in progress at 1 AM Friday 11/27 (John). |
| Dock play | The arm test on Wednesday night, 11/25, showed the arm is far too wobbly, from play in the system (John, 11/27). The sim treats the dock as rigid. Not measured ([IMU wiring note](../notes/2026-11-26-john-imu-bno08x-module-wiring.md)). The plan: feed the IMU data into PID tuning and into policy training (John, 11/27). |
| End effector 1 | Complete mechanically (John, 11/27). Earlier tests with it worked. Electrical waits on the buffer board, due around midday Friday (John, 11/27). In Steve's 11/26 session the board marked EE1 sent no radio packets. Its firmware was not checked ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)). |
| End effector 2 | TAG-Mech-005 is machined and needs tapping, then full assembly. The M2.5 tap arrives around midday Friday (John, 11/27). Its servo moved over the radio, through a buffer board, on the bench on 11/26 ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)). |
| Servo bus | The STS3215 bus servos need a 74LS125 half-duplex buffer board between them and the C5, so the C5 does not get fried (John, 11/27). The board for the robot is a work in progress, due around midday Friday. The direct GPIO wiring that worked on the bench on 11/24 ([note](../notes/2026-11-24-john-sts3215-c5-bench.md)) is not what goes on the robot. |
| Camera tags | The reCamera sends tags to the EE C5 over USB. The EE servo firmware does not forward them. Board 10 got none ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)). The deterministic track needs them. Must reach the laptop by the end of Friday (John, 11/27). |
| Ports | All 7 mounted (John, 11/27). |
| Site | Watt Hall B1 is open every day (John, 11/27). |
| Shell | A direction sketch was posted on Discord on 11/24. Manufacturing has not started (John, 11/27). |
| ESPs | Three have died since 11/24 (Discord, 11/25). One died from running on the buck and USB at once ([note](../notes/2026-11-24-john-sts3215-c5-bench.md)). How many spare C5s are left is not recorded. |

## Day by day

### Saturday 11/21 (night of the meeting)

- [ ] Print docking boards at MakerZone, in PETG. About 2 per machine, about 6 boards. Not recorded.
  - PETG from Robo. If Robo has none, borrow from Makers.
- [ ] Send Jack CAD screenshots to confirm which end effector parts are made.
  - Jack answered during the meeting: one part is still missing, the one from Yang. See [parts](#parts-status-as-of-1127).

### Sunday 11/22

- [x] ROS nodes talk to the motors over ESP-NOW, all in ROS. Working on 11/22, ahead of Monday's ROS task (John, 11/22).
  - On the bench: motor 0x01 was turned and swept through ROS while two other motors held. Three motors, no load, not the arm ([Hansi's work, summary note](../notes/2026-11-22-john-tether-ros-bench-and-sim.md)).
- [x] Sim connected to ROS, in sim only. The sim speaks the robot's own protocols, and the tether_ros container and a ros2_control driver run against it ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). Nothing in that work has touched the robot. Was Monday.
- [x] Center module final wiring. Pretty much fully wired on 11/22 (John). All three modules streamed on 11/26.
- [ ] Train a policy. Test it with docking and human interaction. (Steve)
  - In sim. The policy should notice a person nearby and react.
- [ ] Talk through the end effector backup with Jack and Ming in the room. See [risks](#risks-and-backups).
- [ ] Ask JC how many days he has over Thanksgiving for the shell.
- Center spacer was on the CNC on 11/21. Assumed ready Sunday.

### Monday 11/23 (half speed)

- [ ] **Retap the rear holes on all four DM-J4340s to M4. Prepare the surfaces. Epoxy the motor bottoms to the mounts.**
  - The JB Weld arrived Tuesday, not Monday (Ming, on Discord 11/23). Epoxy was curing on the night of 11/24 (Discord). The arm was driven by 11/27. Not recorded whether all four were retapped and epoxied. Confirm.
  - Tap type, torque, epoxy and what to check: [rear mount loads note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) (draft, calculated, not measured).
- [x] **Go to IYA with CK. Drill all holes. At least 2 mounted ports. Bring to Ming's.** All 7 ports mounted by 11/27 (John).
  - Table port drawings and plywood circle sizes are in tethersim, `docs/drawings/table_ports.pdf` ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)).
- [x] Ming CAMs and cuts the pizza slices. Enough for end effector 1, which is complete mechanically (John, 11/27).
- [x] Tap TAG-Mech-003 with an M2.5 hand tap. Done, since end effector 1 is complete mechanically. Day not recorded.
- [x] Start machining the missing part, TAG-Mech-005, at the Castle. Machined by 11/27 (John). Tapping it is Friday.
- [ ] **ROS: act on what the sim found.** Where each item stands on 11/27:
  - Gains and feedforward: `COMMAND_FF` (per-motor gains plus a feedforward torque) is on tethersmall `main`. Steve's host script `robot_control.py` sends it with gravity feedforward. The ROS `gateway_node` does not carry it yet ([Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md)).
  - Two arm URDFs disagree: tethersim's (16.6 kg) and tether_controls' (14.35 kg). Not settled.
  - The 7-motor map, board by board, is in [Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md). Signs and zeros against the sim are not checked. Now Friday.
  - The camera link on 5 GHz channel 36 is not measured. The camera relay was not tested after the 11/26 reflash.
  - Hansi's end effector forwarding is on tethersmall `main` through #9.

### Tuesday 11/24 (half speed)

- [x] **1 end effector done mechanically.** By 11/27 (John). Day not recorded.
- [x] End effector test with a port. The motor tests in the port on 11/25 showed play in the dock ([IMU wiring note](../notes/2026-11-26-john-imu-bno08x-module-wiring.md)).
- [ ] Shell start: JC. A direction sketch was posted on Discord. Manufacturing not started (John, 11/27).
- Added: the STS3215s and the LED ring ran on a C5 on the bench. One C5 died on the buck and USB at once ([note](../notes/2026-11-24-john-sts3215-c5-bench.md)). Docking on the end effector servo worked at 50 steps/s ([note](../notes/2026-11-24-john-nano-c5-docking-endurance.md)).

### Wednesday 11/25

- [x] **Final wiring, both side modules.** All three modules streamed on 11/26.
- [ ] **End effector 1 fully complete, including electrical.** Needs the buffer board. Now Friday.
- [ ] **End effector 2 mechanically done.** Not done (John, 11/27). Now Friday.
- [x] **Lock end effector 1 in a port and swing the arm around on it.** Motor tests in the port on 11/25. Driven by 11/27 (John). On 11/26 Discord said the arm moved and nothing snapped. This was the first load on the epoxied mounts.
- Added: a third ESP died (Discord).

### Thursday 11/26 (Thanksgiving)

- [x] **Mount all 7 ports.** (John, 11/27.)
- [ ] **End effector 2 done, including electrical.** Now Friday.
- [x] **Final Tether, full arm.** Assembled and driven. No shell.
- [ ] **Verify ROS. Test docking between 2 ports.** Driven, not docked (John, 11/27). The ROS gateway node has not run on the hardware ([Steve's 11-27 note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md)). Now Friday.
- [x] Ask a Roski student for access. Not needed: Watt Hall B1 is open every day (John, 11/27).
- [ ] Shell design done. Not recorded.
- [ ] Build interactive boxes. Not recorded. Now Saturday.
- Added: an IMU on each module, and all four arm boards reflashed ([on-arm note](../notes/2026-11-26-john-imu-on-arm-bringup.md)). Reason: the play in the dock.
- Added: the EE2 servo moved over the radio through the buffer board ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)).
- Added: all 7 motors mirrored live into tethersim while limp. SpaceMouse teleop and an E-stop in the sim ([Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md)).

### Friday 11/27

**By the end of the day: both end effectors fully manufactured and working electrically, and the camera tags reaching the laptop (John, 11/27).**

Overnight (1 AM):

- [ ] **Stream the IMU data.** In progress (John). Added after the arm test on Wednesday night showed the arm is far too wobbly, from play in the system.
  - The data feeds PID tuning and policy training (John).
  - A `T_IMU` logger does not exist yet ([Steve's 11-27 note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md)). Logging with the arm moving gives the swing and the base tilt.

By midday:

- [ ] **Finish the servo buffer board.** The half-duplex adapter between the C5 and the STS3215s. A work in progress. Done around midday (John).
  - Fixes from EE2's bench board: pull-up on U1 pin 3, not on DATA. TX on D7. A ground wire from pack − to the XIAO's GND ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)).
- [ ] **M2.5 tap arrives.** Around midday (John).

Afternoon:

- [ ] **End effector 1 electrical,** on the buffer board. Was Wednesday. It is complete mechanically, and earlier tests with it worked.
  - Find out why the EE1 board sent no radio packets on 11/26.
- [ ] **End effector 2: tap TAG-Mech-005 (M2.5), then assemble it fully.** Waits on the tap. Was Wednesday.
- [ ] **End effector 2 electrical.** Was Saturday.
- [ ] **Mount both end effectors on the robot and get everything working.**
- [ ] **Camera tags to the laptop. Must be done today (John).** The EE firmware has to forward the camera's tag data, or the camera needs its own C5 ([Steve's EE2 note](../notes/2026-11-26-steve-ee2-servo-buffer-debug.md)). Blocks the deterministic track.

Evening, after both end effectors are on:

- [ ] **PID tuning with the IMU feedback,** to take out some of the wobble (John).
  - Before more torque: check each joint's sign and zero against tethersim, and which end is anchored ([Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md)).
  - Agree the `COMMAND_FF` limits. The ones on `main` are proposals.
- [ ] **Dock between 2 ports.** Was Thursday. Full stack if possible: ROS, comms, deterministic control. The port tolerance is loose, and the dock has play. Spills to Saturday if the end effectors are late.

Also Friday:

- [ ] **Set up the environment at Watt Hall B1 and start walking on it.** Was "maybe". It is open every day.
- [ ] **Software debugging** starts, in two tracks:
  - Deterministic path: CV tuning, reCamera detection, the rest. Everyone but Steve.
  - Policy track: Steve.
- [ ] **Shell manufacturing.** It has not started, and it needs about 2 days.
  - Print parts in parallel on the Prusas.

### Saturday 11/28

- [ ] **First step with both end effectors.** One end holds, the other swings and docks, then they swap. Needed before Sunday. Not on the 11/21 plan.
- [ ] **Software debugging**, both tracks, second day. At Watt Hall B1, steps included (D-055).
  - Policy: train with the IMU data (John, 11/27). Steve. The sim needs the dock play (a loose, sprung joint at the port), or the IMU reading only repeats the joint angles and the policy learns nothing from it ([IMU wiring note](../notes/2026-11-26-john-imu-bno08x-module-wiring.md)).
- [ ] Shell manufacturing done.
- [ ] Build interactive boxes. Whoever is free. Was Thursday.
  - Each box has a docking port on it, so Tether can grab it the way it grabs a dock.
  - Magnets on the boxes make them stick to each other when Tether stacks one on another.

### Sunday 11/29 (last day of break)

- [ ] **Full run on the course.** This is the goal for the break. Kept on 11/27 (John).

### Monday 11/30

- [ ] **Mount the shell.** First thing.
- [ ] **Test. Full run with the shell on.**

### Tuesday 12/1 and Wednesday 12/2

Not planned. These are the only spare days left.

### Thursday 12/3

Demo day. Be at Watt Hall B1 from **5:00 PM**.

## Parts status (as of 11/27)

Rows marked 11/21 have no newer source. Not checked against the parts themselves.

| Part | Status |
|---|---|
| End effector 1 | Complete mechanically (John, 11/27). Electrical waits on the buffer board. |
| End effector 2 | TAG-Mech-005 left to tap, then full assembly. Waits on the M2.5 tap, arriving around midday 11/27 (John). |
| M2.5 tap | Not in hand. Arrives around midday 11/27 (John). |
| Pizza slices | Enough for end effector 1. The rest not recorded. |
| TAG-Mech-003 | Done for end effector 1. |
| TAG-Mech-005 | Both machined (John, 11/27). The one for end effector 2 still needs an M2.5 tap, on Friday 11/27. |
| DM-J4340 rear mounts | The JB Weld arrived 11/24, not 11/23 (Discord). The arm was driven by 11/27. Whether all four were retapped and epoxied is not recorded. |
| Modules | All three wired and streaming on 11/26. |
| Center spacer | 11/21: on the CNC. The arm is assembled now. |
| One center part | 11/21: 3D printed, not machined. |
| Camera mounts | 11/21: enough in hand. |
| Belts | 11/21: in hand. |
| End effector electronics | Each needs a 74LS125 buffer board for the servos. EE2's bench board works. The board for the robot is a work in progress, due around midday 11/27 (John). Parts list posted on Discord 11/25. |
| IMUs | One GY-BNO08X on each module (11/26). |
| ESP32-C5s | Three ESPs died since 11/24. Spares not recorded. |
| Docking boards | 11/21: printing that night. Not recorded since. |
| Ports | All 7 mounted (John, 11/27). |
| Ring LEDs | Lit on a C5 on 11/24. A second loom stayed dark, maybe from 3.3 V data into a 5 V ring ([note](../notes/2026-11-24-john-nano-c5-docking-endurance.md)). |

## Software plan

- As of 11/22 the ROS nodes talk to the motors over ESP-NOW (John).
- With the event-driven gateway node, ROS adds about 1 ms over the serial port, measured on the bench ([note](../notes/2026-11-22-john-tether-ros-bench-and-sim.md)).
- As of 11/26 the sim mirrors all 7 real motors live, and SpaceMouse teleop runs in a one-dock sim scene ([Steve's 11-26 note](../notes/2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md)).
- As of 11/27 tethersmall `main` is the firmware on the arm, and tether_ros publishes the IMUs ([Steve's 11-27 note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md)). Torque commands with feedforward go through Steve's host script, not the ROS gateway node.
- ROS runs on a laptop. The sim connects to it as a topic. The wireless link to the modules is hidden behind a master and slave layer.
- Two tracks, so one can stand in if the other fails:
  - **Deterministic.** A planned path. Works as long as the AprilTags are detected. Mostly CV tuning and detection accuracy. Needs the camera tags to reach the laptop.
  - **Policy.** A trained policy. Also covers the boxes and human interaction. Steve.
- About 2 people per track.
- Walking alone may take 1 to 2 days of testing.
- The policy needs the real layout to match what it trained on. Step height matters less than the layout.
- Idea: when a person hands Tether a box, the ring LEDs show a status. Not scheduled.

## Risks and backups

- **No dock between two ports yet.** Sunday's full run needs docking, a step with both ends, and walking. Two days are left for all of it.
- **Play in the dock.** The arm is far too wobbly (John, 11/27). The sim is rigid, so the policy may not cope. The IMUs measure it. The plan is PID tuning and policy training with the IMU data. Nothing logs it yet, and the sim does not model the play.
- **Camera tags do not reach the laptop.** The EE firmware drops them. Without them the deterministic track cannot run. Due by the end of Friday.
- **Both end effectors hang on midday Friday.** The buffer board and the M2.5 tap are both due around then. If either is late, mounting, PID tuning and docking slip into Saturday, and Saturday already holds the first step with both ends.
- **End effector lock.** Seen in a port on 11/25, with play. An electromagnet backup was raised and not chosen: it needs extra ESPs and relays, battery power for the magnets, and changes to the sim and software. There is no budget for it.
- **ESPs dying.** Three since 11/24. Never power a C5 from USB and the buck at once. Plug the pack in last ([power order](../notes/2026-11-24-john-nano-c5-docking-endurance.md)). The spare count is not recorded.
- **`COMMAND_FF` limits.** 80 Nm, 25 Nm and kp 500 are on `main` as proposals, not agreed numbers.
- **Battery.** Nothing reads pack voltage. The motors' undervoltage setting has not been read ([open question 25](../truth/open-questions.md)).
- **4340 rear mounts.** The arm has been driven on them. The [load note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) says M4 with epoxy holds floor and step loads on paper but not a drop. Calculated, not measured.
- **Two arm URDFs.** The sim and tether_ros use different arm files. The [4340 load note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) used the 14.35 kg one.
- **Friday is overloaded.** It holds both end effectors, the camera path, the IMU streaming, PID tuning, docking, the Watt Hall setup and the shell start. Who does which is not set.
- **Shell.** Not started, and it needs about 2 days. To go on Monday it has to start Friday. It matters for how the robot looks.
- **Shell and the center joint.** The back electronics make one side thicker than planned, and the spacer can't get thicker. The shell will be asymmetric. Software should swing the full 360° only on the flat side.
- **Spillover.** Two spare days are left before demo day, 12/1 and 12/2.

## Changes

Add a line when something moves.

| Date | What changed |
|---|---|
| 2026-11-21 | Plan written at the planning meeting. |
| 2026-11-22 | John's corrections: demo day and site (D-051), Sunday test is by hand and Tuesday is powered, part number TAG-Mech-005, what the boxes are for. |
| 2026-11-22 | John: the outstanding TAG-Mech-005 will be machined at the Castle. No longer an assumption. Day unchanged (Monday). |
| 2026-11-22 | John: retap the DM-J4340 rear holes to M4 and epoxy the motors to the mounts by end of 11/23. Side module wiring, arm assembly and the powered test move to Wed 11/25. Full arm and the 2-port docking test move to Thu 11/26. Site walking moves to Fri 11/27. Full run moves to Sun 11/29. Shell mount and the shell-on run move to Mon 11/30. |
| 2026-11-22 | John's status for 11/22: ROS nodes talk to the motors over ESP-NOW. Center module pretty much fully wired. Pizza slices might be done 11/23. Hand test blocked by a missing M2.5 hand tap for TAG-Mech-003, to be tapped 11/23 at BHE. TAG-Mech-005 machining starts 11/23. End effector 1 mechanical and the hand test move to Tue 11/24. End effector 1 electrical and end effector 2 mechanical move to Wed 11/25. End effector 2 electrical moves to Thu 11/26. |
| 2026-11-22 | From Steve's 11-22 note: the sim is connected to ROS (sim only), so Monday's ROS item becomes follow-ups from the sim findings. Added two risks: holding the arm over the gateway protocol, and the two arm URDFs. Added the table port drawings to the IYA item. |
| 2026-11-22 | From Hansi's tether_ros work (unmerged branch): the bench run behind "ROS nodes talk to the motors", the 1 ms ROS latency, the camera link on 5 GHz channel 36, and a second confirmation of the gateway holding risk. No days moved. |
| 2026-11-27 | John's status for 11/27: arm driven, not docked. End effector 1 complete mechanically. End effector 2 not complete. All 7 ports mounted. Watt Hall B1 open every day. Shell manufacturing not started. The servos need a 74LS125 buffer board. Full run kept on Sun 11/29, shell kept on Mon 11/30. |
| 2026-11-27 | Moved: the 2-port docking test and end effector 1 electrical to Fri 11/27. End effector 2 mechanical and TAG-Mech-005 to Fri 11/27. End effector 2 electrical and the interactive boxes to Sat 11/28. Watt Hall setup on Friday is no longer a maybe. |
| 2026-11-27 | Added from the 11-24 to 11-27 notes: camera tags to the laptop, IMU logging, joint signs and zeros, the `COMMAND_FF` limits, dock play in the sim, and a first step with both ends on Saturday. New risks: no dock yet, play in the dock, the camera path, end effector 2, ESPs dying, `COMMAND_FF` limits, battery. Removed past risks: Monday overloaded, Wednesday has no slack, Watt Hall access, holding the arm over the gateway, time for software. Yang's part (TAG-Mech-005) is now under the end effector 2 risk. |
| 2026-11-27 | The days for the carried and added items were proposed by John's AI agent on 11/27. Owners are not set. |
| 2026-11-27 | John, about 1 AM Friday: both end effectors fully manufactured and working electrically by the end of Friday. The servo buffer board is due around midday. End effector 2 has one part left to tap, waiting on an M2.5 tap due around midday. End effector 2 electrical moves from Saturday to Friday. IMU streaming is in progress, after Wednesday night's test showed the arm far too wobbly. The IMU data feeds PID tuning and policy training. The camera tags must reach the laptop by the end of Friday. Friday is now split into overnight, midday, afternoon and evening. Docking between 2 ports is Friday evening and spills to Saturday if the end effectors are late. |
| 2026-11-27 | John: the part left to tap on end effector 2 is TAG-Mech-005. Both are machined. Yang's part is no longer outstanding. |
