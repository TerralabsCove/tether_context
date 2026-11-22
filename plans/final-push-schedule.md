---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-22
---

# Final push schedule: 11/22 to 12/3

**Demo day: Thursday 12/3, at Watt Hall B1. Be there from 5:00 PM.** (D-051)

**Goal for the end of Thanksgiving break (Sunday 11/29): the arm running on the setup.** 8 days.

Set at the [2026-11-21 planning meeting](../meetings/2026-11-21-final-push-planning.md) (D-050). The day lists below are the whiteboard from that meeting: [11/22 to 11/25](../assets/2026-11-21-final-push-whiteboard-nov22-25.jpg), [11/26 to 11/29](../assets/2026-11-21-final-push-whiteboard-nov26-29.jpg). Indented lines add detail from the [transcript](../meetings/2026-11-21-final-push-planning-transcript.md).

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

- [ ] **Final wiring, all 3 modules** (center and both sides). After JC Loctites. No touching the wiring after this.
  - Then tie the wires down, assemble the arm, and test the electronics and basic comms.
- [ ] Ming CAMs and cuts the pizza slices. They block the first metal end effector.
  - The pizza slice stock went to Jack. He may have taken it home. Check when he arrives.
  - 4 slices are enough to build one end effector.
- [ ] End effector test with a port. Mechanical only: turn it by hand and see if there are any issues.
  - The fully powered test is Tuesday.
- [ ] Train a policy. Test it with docking and human interaction. (Steve)
  - In sim. The policy should notice a person nearby and react.
- [ ] Talk through the end effector backup with Jack and Ming in the room. See [risks](#risks-and-backups).
- [ ] Ask JC how many days he has over Thanksgiving for the shell.
- Center spacer is on the CNC now. Assumed ready Sunday. The CNC is tied up until about 1 PM.

### Monday 11/23 (half speed)

- [ ] **Go to IYA with CK. Drill all holes. At least 2 mounted ports. Bring to Ming's.**
  - Drill the holes for every port. Attach at least 2.
  - Bring 1 or 2 plates and a table to Ming's house. IYA is closed over Thanksgiving, and Ming's house is empty.
- [ ] **ROS: write modules and connect the sim.**
  - Abstract master and slave. To ROS, the wireless link should look like a cable.
  - Sim into ROS: the sim is exposed as a ROS topic.
  - Build ROS on a laptop, in a Linux VM, so it can be packaged and sent to other laptops.
- [ ] **1 end effector done mechanically.**
- [ ] Machine the missing part, TAG-Mech-005.
  - One was finished 11/21 at the Castle. The other was Yang's. Assume Yang has not made it, and machine it at the Castle.

### Tuesday 11/24 (half speed)

- [ ] **End effector 1 fully complete, including electrical.**
- [ ] **End effector 2 mechanically done.**
- [ ] **Lock end effector 1 in a port and swing the arm around on it.** Fully powered, with the end effector connected to the arm.
- [ ] Shell start: JC.

### Wednesday 11/25

- [ ] **End effector 2 done, including electrical.**
- [ ] **Final Tether, full arm.** Afternoon. No shell yet.
- [ ] **Verify ROS. Test docking between 2 ports.** Night.
  - Full software stack: ROS, comms, deterministic control. Bounce between the 2 ports if there is time.
  - Docking will need PID tuning. The port tolerance is loose.
- After this, electrical people move to software.

### Thursday 11/26 (Thanksgiving)

- [ ] **Mount all 7 ports.** Morning. (6 plates, 7 ports.)
- [ ] Maybe: go to Watt Hall B1, set up the environment, start walking on it.
- [ ] If not Watt Hall B1: move around on the mushrooms.
- [ ] Ask a Roski student for access.
- [ ] Shell design done.
- [ ] Build interactive boxes. Whoever is free.
  - Each box has a docking port on it, so Tether can grab it the way it grabs a dock.
  - Magnets on the boxes make them stick to each other when Tether stacks one on another.
  - Stacking boxes is a possible part of the demo.

### Friday 11/27

- [ ] **Software debugging**, in two tracks:
  - Deterministic path: CV tuning, reCamera detection, the rest. Everyone but Steve.
  - Policy track: Steve.
- [ ] Shell manufacturing.
  - Print parts in parallel on the Prusas.

### Saturday 11/28

- [ ] **Full run on the course.**
- [ ] Shell manufacturing done.

### Sunday 11/29 (last day of break)

- [ ] **Mount the shell.** First thing.
- [ ] **Test. Full run with the shell on.**

### Monday 11/30 to Thursday 12/3

Not planned at the meeting. Demo day is **12/3**. Be at Watt Hall B1 from **5:00 PM**.

## Parts status (as of 11/21)

From the meeting. Not checked against the parts themselves.

| Part | Status |
|---|---|
| End effector parts, most | In hand. Enough for one end effector, except the pizza slices. |
| Pizza slices | Not machined. Ming cuts them Sunday. |
| TAG-Mech-005 | One finished 11/21 at the Castle. One outstanding (Yang's). |
| Center spacer | On the CNC on 11/21. Holes may not be drilled yet. |
| One center part | 3D printed, not machined. |
| Camera mounts | Enough in hand. |
| Belts | In hand. |
| End effector electronics | Not finished. Hansi is needed. |
| Docking boards | Printing 11/21 night. |
| Floor plates and tables | At IYA. 6 plates. |
| Ring LEDs | Ordered. Each LED can be switched on its own. |

## Software plan

- ROS runs on a laptop. The sim connects to it as a topic. The wireless link to the modules is hidden behind a master and slave layer.
- Two tracks, so one can stand in if the other fails:
  - **Deterministic.** A planned path. Works as long as the AprilTags are detected. Mostly CV tuning and detection accuracy.
  - **Policy.** A trained policy. Also covers the boxes and human interaction. Steve.
- About 2 people per track.
- Walking alone may take 1 to 2 days of testing.
- The policy needs the real layout to match what it trained on. Step height matters less than the layout.
- Idea: when a person hands Tether a box, the ring LEDs show a status. Not scheduled.

## Risks and backups

- **End effector lock.** Turned by hand on Sunday. Not tested under power until Tuesday. If it fails, about 10 days are left. An electromagnet backup was raised and not chosen: it needs extra ESPs and relays, battery power for the magnets, and changes to the sim and software. There is no budget for it. Decide with Jack and Ming on Sunday.
- **Watt Hall B1 access over Thanksgiving.** Unknown. Asking a Roski student. If there is no access, practice at Ming's on the plates, table and mushrooms. Ming's front steps are too shallow to stand in for the real steps.
- **Yang's part.** Assumed not made.
- **Shell.** Low priority next to everything else, but it matters for how the robot looks. Needs about 2 days to manufacture. JC's availability over Thanksgiving is not confirmed.
- **Shell and the center joint.** The back electronics make one side thicker than planned, and the spacer can't get thicker. The shell will be asymmetric. Software should swing the full 360° only on the flat side.
- **Time for software.** After the full arm exists (Wednesday), 2 to 3 days are left before the shell goes on Sunday.
- **Spillover.** Sunday's and Monday's lists are both long.

## Changes

Add a line when something moves.

| Date | What changed |
|---|---|
| 2026-11-21 | Plan written at the planning meeting. |
| 2026-11-22 | John's corrections: demo day and site (D-051), Sunday test is by hand and Tuesday is powered, part number TAG-Mech-005, what the boxes are for. |
