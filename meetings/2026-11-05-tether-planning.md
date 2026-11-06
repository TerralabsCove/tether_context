---
type: meeting
date: 2026-11-05
topic: Emergency planning. Manufacturing blockers, end effector backup, camera and compute
attendees: not recorded. No speaker labels. John recorded; Ming joined partway. Others unlabeled.
source: Granola, https://notes.granola.ai/d/024cc3f6-ea96-418e-86bb-5cc35c442d37
decisions_logged: D-037 to D-041
---

<!-- Granola summary, with comments about individual members removed at John's request. Otherwise as-is. "Bomb" is Baum Family Makerspace, misheard by Granola. Points where this summary
     and the transcript or BOM disagree are in truth/open-questions.md under "Conflicts between sources". -->

# Manufacturing Blockers

- Water-jetted panels not done by Bomb Family; expected this weekend
  - If not done, contact Yang (Bomb employee) for Monday water jetting
  - Get verbal confirmation from Yang via Ripple beforehand
- End effector design delayed ~2 weeks
  - 13 parts to mill total: estimated 2 weeks of machining time
  - End mounts also blocked: tap broke
- Project ~2 weeks behind schedule overall

# Water Jetting Contingency

- IYA also has a water jet: viable concurrent option
  - Someone available from 2pm Saturday to run it
  - Need to confirm stock is at Bomb and fits IYA machine
- Jack Carpino not available this weekend
- Get machining quote (price per block + shipping + time) by tomorrow
  - If timeline exceeds deadline, current end effector design is not viable

# End Effector: Backup Design

- Current design has 13 parts to mill: very hard to manufacture, likely 2-week timeline
- Ming proposed simpler alternative mechanical gripper
  - Grips standard sheet metal, sustains load, DFM-focused
  - Design should be relatively simple and outsourceable
- Plan: let Isaac continue, but develop Ming’s design as backup in parallel
- Hybrid approach discussed: 3D print vertical-load parts, mill horizontal-load parts

# Camera and Compute

- Decided: single fisheye camera, no stereo
  - Stereo requires streaming full 3D point cloud to master computer: too much latency
  - ROS stack can’t run on both arm sides simultaneously
  - AprilTags only need mono camera; position data is lightweight to stream
- Camera: ReCamera 2002W (fisheye, 1080p, 15 FPS, 1 GHz, runs Linux)
  - 65-degree FOV; tested detecting AprilTags at 15-20 cm
  - Can detect at least 3 AprilTags simultaneously
  - Need to verify minimum compute required for AprilTag detection
- Fisheye confirmed as non-negotiable for reliable AprilTag tracking
- Camera mount: place on far end of arm, point straight, rotate as needed
  - AprilTag docking marker can go on the side, position relative to other side is all that matters

# Camera Procurement

- ReCamera 2002W (wireless/W version) selected
  - PoE version out of stock; standard 5V wireless version confirmed
  - Ordered despite higher cost (tariffs + shipping): time savings justify it
  - Need to verify if fisheye lens mod is possible; if not, may need to return
- Mouser link identified as faster shipping option (~3 days from ship date)
- Need 2 cameras total

# Hardware Scheduling and Software Transition

- Hardware must lock in ASAP: no more delays tolerable
  - Specific deadlines needed for each electrical sub-task before switching to software
  - Worst case: software-only work begins in ~1.5-2 weeks
- Software team currently thin
- Discussed forcing a focused work session (Friday or Saturday hackathon)
- Buck converters (24V to 5V step-down) needed for ESP and servos
  - Stall current: 3.2A at 4.8V; confirm regulator sizing
  - Potentiometer-style converters flagged as a risk on the arm (could twist)

# Next Steps

- **Contact Yang on Ripple for water jet backup**

  Get verbal confirmation he can water jet panels Monday if Bomb doesn't finish this weekend.
- **Get machining quote for end effector by tomorrow**

  Price per block, shipping, and lead time. If it blows the deadline, pivot fully to Ming's backup design.
- **Run Saturday water jet session at IYA from 2pm**

  Pick up stock from Bomb first; confirm it fits the IYA machine.
- **Verify AprilTag compute requirements for ReCamera 2002W**

  Determine if onboard processing is sufficient or if a streaming solution is needed.
- **Message Jack Carpino about Yang and water jet situation**

  Keep him informed on the contingency plan for parts.
- **Set hardware-to-software transition schedule**

  Define specific days each electrical sub-task must be done before team switches to software.

---

Meeting transcript and chat: https://notes.granola.ai/d/024cc3f6-ea96-418e-86bb-5cc35c442d37
