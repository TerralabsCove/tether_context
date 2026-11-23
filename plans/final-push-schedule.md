---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-22
---

# Final push schedule: 11/22 to 12/3

**Demo day: Thursday 12/3, at Watt Hall B1. Be there from 5:00 PM.** (D-051)

**Goal for the end of Thanksgiving break (Sunday 11/29): the arm running on the setup.** 8 days.

**Revised 2026-11-22.** The rear holes on the four DM-J4340s get retapped to M4, and the motors get epoxied to their mounts, by end of day Monday 11/23. Everything that needs a powered arm moves about one day later. The full run is now Sunday 11/29. The shell goes on Monday 11/30. See [Changes](#changes).

Set at the [2026-11-21 planning meeting](../meetings/2026-11-21-final-push-planning.md) (D-050). The day lists below started as the whiteboard from that meeting: [11/22 to 11/25](../assets/2026-11-21-final-push-whiteboard-nov22-25.jpg), [11/26 to 11/29](../assets/2026-11-21-final-push-whiteboard-nov26-29.jpg). Indented lines add detail from the [transcript](../meetings/2026-11-21-final-push-planning-transcript.md). Items that moved say where they were.

This plan is tight on purpose. Things will spill over. When they do, move the item here and note it under [Changes](#changes). Tick items off as they finish.

- Monday and Tuesday are planned at half speed. People have class.
- Both ends use Ming's end effector (D-052). The plan assumes it works the first time. See [risks](#risks-and-backups).
- People: JC is Jack Carpino. CK is Caroline Kim. "Castle" is Ming's house.

## Day by day

### Saturday 11/21 (night of the meeting)

- [ ] Print docking boards at MakerZone, in PETG. About 2 per machine, about 6 boards.
  - PETG from Robo. If Robo has none, borrow from Makers.
- [ ] Send Jack CAD screenshots to confirm which end effector parts are made.
  - Jack answered during the meeting: one part is still missing, the one from Yang. See [parts](#parts-status-as-of-1121).

### Sunday 11/22

- [x] ROS nodes talk to the motors over ESP-NOW, all in ROS. Working on 11/22, ahead of Monday's ROS task (John, 11/22).
- [x] Sim connected to ROS, in sim only. The sim speaks the robot's own protocols, and the tether_ros container and a ros2_control driver run against it ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). Nothing in that work has touched the robot. Was Monday.
- [ ] Center module final wiring. Pretty much fully wired on 11/22 (John).
- [ ] Train a policy. Test it with docking and human interaction. (Steve)
  - In sim. The policy should notice a person nearby and react.
- [ ] Talk through the end effector backup with Jack and Ming in the room. See [risks](#risks-and-backups).
- [ ] Ask JC how many days he has over Thanksgiving for the shell.
- Center spacer was on the CNC on 11/21. Assumed ready Sunday.
- Moved off Sunday:
  - Final wiring on the two side modules, arm assembly and the comms test. They wait for the retap and epoxy. Now Wednesday.
  - Pizza slices. Now Monday.
  - End effector hand test. No M2.5 hand tap for TAG-Mech-003. Now Tuesday.

### Monday 11/23 (half speed)

- [ ] **Retap the rear holes on all four DM-J4340s to M4. Prepare the surfaces. Epoxy the motor bottoms to the mounts. Done by end of day.**
  - The 4340s are the two rolls and the two gripper spins.
  - Tap type, torque, epoxy and what to check: [rear mount loads note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) (draft, calculated, not measured).
- [ ] **Go to IYA with CK. Drill all holes. At least 2 mounted ports. Bring to Ming's.**
  - Drill the holes for every port. Attach at least 2.
  - Bring 1 or 2 plates and a table to Ming's house. IYA is closed over Thanksgiving, and Ming's house is empty.
  - Table port drawings and plywood circle sizes are in tethersim, `docs/drawings/table_ports.pdf` ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). The positions are fitted to the hall model, not measured on site.
- [ ] Ming CAMs and cuts the pizza slices. Might be fully done Monday (John, 11/22). Was Sunday.
  - They block the first metal end effector. 4 slices are enough to build one.
- [ ] Tap TAG-Mech-003 with an M2.5 hand tap, at BHE. It blocks the end effector hand test.
- [ ] Start machining the missing part, TAG-Mech-005, at the Castle.
  - One was finished 11/21 at the Castle. The other was Yang's. It will be machined at the Castle instead (John, 2026-11-22).
- [ ] **ROS: act on what the sim found.** The sim is connected as of 11/22 ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). Left to do:
  - The gateway frame has one kp/kd for all motors and no torque field. In sim the arm sags 5° at the highest gains and would fold at tethersmall's gains. It needs per-motor gains, a feedforward torque, or gravity compensation on the node. Sim only, not seen on the robot.
  - Two arm URDFs disagree: tethersim's (16.6 kg) and tether_controls' (14.35 kg). Joint names, axes and zeros differ. Settle which is current.
  - Confirm the assumptions in the note: EE_1 is node 1, the driver gains, the 1 s telemetry timeout.
  - Run the ROS stack on the robot.

### Tuesday 11/24 (half speed)

- Epoxy cure day. No load and no torque on the side modules until Tuesday night. 24 hours is assumed, from the [load note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md). Check the epoxy's own cure time.
- [ ] **1 end effector done mechanically.** Was Monday. Needs the pizza slices and TAG-Mech-003.
- [ ] End effector test with a port. Mechanical only: turn it by hand and see if there are any issues. Was Sunday.
- [ ] Shell start: JC.

### Wednesday 11/25

- [ ] **Final wiring, both side modules.** After the epoxy has cured, and after JC Loctites. No touching the wiring after this. Was Sunday.
  - Then tie the wires down, assemble the arm, and test the electronics and basic comms.
- [ ] **End effector 1 fully complete, including electrical.** Was Tuesday.
- [ ] **End effector 2 mechanically done.** Was Tuesday. Needs TAG-Mech-005.
- [ ] **Lock end effector 1 in a port and swing the arm around on it.** Night. Fully powered, with the end effector connected to the arm. Was Tuesday.
  - This is also the first load on the epoxied mounts.

### Thursday 11/26 (Thanksgiving)

- [ ] **Mount all 7 ports.** Morning. (6 plates, 7 ports.)
- [ ] **End effector 2 done, including electrical.** Was Wednesday.
- [ ] **Final Tether, full arm.** No shell yet. Was Wednesday.
- [ ] **Verify ROS. Test docking between 2 ports.** Night. Was Wednesday.
  - Full software stack: ROS, comms, deterministic control. Bounce between the 2 ports if there is time.
  - Docking will need PID tuning. The port tolerance is loose.
- [ ] Ask a Roski student for access.
- [ ] Shell design done.
- [ ] Build interactive boxes. Whoever is free.
  - Each box has a docking port on it, so Tether can grab it the way it grabs a dock.
  - Magnets on the boxes make them stick to each other when Tether stacks one on another.
  - Stacking boxes is a possible part of the demo.
- After this, electrical people move to software.

### Friday 11/27

- [ ] Maybe: go to Watt Hall B1, set up the environment, start walking on it. Was Thursday.
- [ ] If not Watt Hall B1: move around on the mushrooms.
- [ ] **Software debugging** starts, in two tracks:
  - Deterministic path: CV tuning, reCamera detection, the rest. Everyone but Steve.
  - Policy track: Steve.
- [ ] Shell manufacturing.
  - Print parts in parallel on the Prusas.

### Saturday 11/28

- [ ] **Software debugging**, both tracks, second day.
- [ ] Shell manufacturing done.

### Sunday 11/29 (last day of break)

- [ ] **Full run on the course.** Was Saturday. This is the goal for the break.

### Monday 11/30

- [ ] **Mount the shell.** First thing. Was Sunday.
- [ ] **Test. Full run with the shell on.** Was Sunday.

### Tuesday 12/1 and Wednesday 12/2

Not planned. These are the only spare days left.

### Thursday 12/3

Demo day. Be at Watt Hall B1 from **5:00 PM**.

## Parts status (as of 11/21)

From the meeting, with John's updates from 11/22 where marked. Not checked against the parts themselves.

| Part | Status |
|---|---|
| End effector parts, most | In hand. Enough for one end effector, except the pizza slices. |
| Pizza slices | Not finished. Might be fully done Monday 11/23 (John, 11/22). |
| TAG-Mech-003 | Needs tapping with an M2.5 hand tap. To be done 11/23 at BHE (John, 11/22). |
| TAG-Mech-005 | One finished 11/21 at the Castle. One outstanding. It will be machined at the Castle, starting 11/23 (John, 2026-11-22). |
| DM-J4340 rear mounts | Rear holes to be retapped to M4, then the motor bottoms epoxied to the mounts. By end of 11/23 (John, 11/22). |
| Center module | Pretty much fully wired on 11/22 (John). |
| Center spacer | On the CNC on 11/21. Holes may not be drilled yet. |
| One center part | 3D printed, not machined. |
| Camera mounts | Enough in hand. |
| Belts | In hand. |
| End effector electronics | Not finished. Hansi is needed. |
| Docking boards | Printing 11/21 night. |
| Floor plates and tables | At IYA. 6 plates. |
| Ring LEDs | Ordered. Each LED can be switched on its own. |

## Software plan

- As of 11/22 the ROS nodes talk to the motors over ESP-NOW (John).
- As of 11/22 the sim is connected to ROS, tested in sim only ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). It also mirrors the real arm's telemetry into the sim as a digital twin.
- ROS runs on a laptop. The sim connects to it as a topic. The wireless link to the modules is hidden behind a master and slave layer.
- Two tracks, so one can stand in if the other fails:
  - **Deterministic.** A planned path. Works as long as the AprilTags are detected. Mostly CV tuning and detection accuracy.
  - **Policy.** A trained policy. Also covers the boxes and human interaction. Steve.
- About 2 people per track.
- Walking alone may take 1 to 2 days of testing.
- The policy needs the real layout to match what it trained on. Step height matters less than the layout.
- Idea: when a person hands Tether a box, the ring LEDs show a status. Not scheduled.

## Risks and backups

- **End effector lock.** Turned by hand on Tuesday. Not tested under power until Wednesday night. If it fails, about 8 days are left. An electromagnet backup was raised and not chosen: it needs extra ESPs and relays, battery power for the magnets, and changes to the sim and software. There is no budget for it. Decide with Jack and Ming.
- **4340 rear mounts.** The retap and epoxy are Monday. The first load on them is Wednesday night. Epoxy is permanent, so check each motor powers up and reports before bonding it. A spare motor has M2.5 holes. The [load note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) says M4 only helps if cut with a bottoming tap, and that M4 with epoxy holds floor and step loads on paper but not a drop. Calculated, not measured.
- **Holding the arm over the gateway.** In sim, the gateway protocol cannot hold the full arm stiffly ([Steve's note](../notes/2026-11-22-steve-tethersim-ros.md)). If the powered test on Wednesday night runs over that path, this needs fixing first. Not seen on the robot.
- **Two arm URDFs.** The sim and tether_ros use different arm files. The [4340 load note](../notes/2026-11-22-john-dm4340-rear-mount-loads.md) used the 14.35 kg one.
- **Monday is overloaded.** It is a half-speed day and now holds the retap, the epoxy, the IYA trip, the BHE tapping and TAG-Mech-005. Who does which is not set.
- **Wednesday has no slack.** The arm and end effector 1 both become ready that day, and the powered test is that night. If the pizza slices or TAG-Mech-003 slip past Monday, the test slips too.
- **Watt Hall B1 access over Thanksgiving.** Unknown. Asking a Roski student. If there is no access, practice at Ming's on the plates, table and mushrooms. Ming's front steps are too shallow to stand in for the real steps.
- **Yang's part (TAG-Mech-005).** Will be machined at the Castle (John, 2026-11-22). Open until it is cut.
- **Shell.** Low priority next to everything else, but it matters for how the robot looks. Needs about 2 days to manufacture. JC's availability over Thanksgiving is not confirmed.
- **Shell and the center joint.** The back electronics make one side thicker than planned, and the spacer can't get thicker. The shell will be asymmetric. Software should swing the full 360° only on the flat side.
- **Time for software.** After the full arm exists (Thursday), about 3 days are left before the shell goes on Monday 11/30.
- **Spillover.** Two spare days are left before demo day, 12/1 and 12/2. There were three.

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
