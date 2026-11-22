---
type: meeting
date: 2026-11-21
topic: Final push planning. Day-by-day schedule for Thanksgiving break, 11/22 to 11/29, up to the 12/3 deadline
attendees: John Peng (recorded), Steve Lu. No speaker labels. At least one more person was in the room, not named. Ming joined by call for about 5 minutes. Jack did not join.
source: Granola, https://notes.granola.ai/d/07318fb5-b92a-4df3-9f40-67ddd314ce61
decisions_logged: D-050
---

<!-- Granola summary, as-is. The schedule the team wrote down is on the whiteboard:
     ../assets/2026-11-21-final-push-whiteboard-nov22-25.jpg and ../assets/2026-11-21-final-push-whiteboard-nov26-29.jpg.
     The working version is ../plans/final-push-schedule.md. Transcript: 2026-11-21-final-push-planning-transcript.md.
     Corrections to this summary, from the whiteboard and John (2026-11-22):
     - "Waite Phillips Hall (WPH)" is wrong. It is Watt Hall B1, the demo site and the practice site (D-051).
     - Demo day is 12/3. The team needs to be there from 5:00 PM (D-051).
     - Shell starts Tuesday, not Monday.
     - The boxes are Thursday, not Wednesday.
     - Sunday has an end effector test: turn it by hand and look for issues. Tuesday is the fully powered test, with the end effector on the arm.
     - The part is TAG-Mech-005, not "TAD-MAT-005".
     - "Jack" who Loctites and designs the shell is Jack Carpino (JC). -->

# Deadline and Timeline Overview

- Hard deadline: December 3rd (demo day)
- 8 days until end of Thanksgiving break to get everything done
- Plan is aggressive; assuming half efficiency Monday and Tuesday (classes, other commitments)
- Things will spill over: plan is a forcing function, not a guarantee

# Parts Status and End Effector Blockers

- Most mechanical parts confirmed in hand
- Key blocker: pizza slices (need machining by Ming)
  - Ming can CAM and cut tomorrow
  - Jack may have brought them home; confirm when he arrives Sunday
- Second missing part: TAD-MAT-005 (one finished today at the castle, one still waiting on Yang)
  - Assume Yang has not done his; plan to machine it in-house Monday
- Center spacer: being milled now, assume available Sunday
- One 3D-printed center part confirmed (not machined)
- Camera mounts: confirmed in hand

# Sunday Nov 22 Goals

- Final wiring on all 3 modules (central + 2 side) after Jack Loctites
- Ming completes pizza slice machining
- Assemble one metal end effector (mechanically), pending pizza slices
- Software: start training a policy, test response to docking and human interaction events
- Tonight: go to MakerZone and 3D print docking boards (PETG, ~6 boards, 2 per machine)

# Monday Nov 23 Goals

- Go to IYA with Caroline Kim: drill holes and attach docking ports to floor plates
  - Prepare holes for all ports, attach at least 2
  - Bring 1-2 plates and a table back to Ming’s house (house will be empty over break)
- Machine TAD-MAT-005 (Yang’s missing part)
- Continue end effector build (mech); first end effector mechanically done by end of Monday
- ROS: write modules, set up laptop build (Linux VM), begin connecting to sim
  - Abstract master-slave architecture
  - Expose ROS topics; connect simulator as a topic
- Jack: begin shell design

# Tuesday Nov 24 Goals

- First end effector fully complete (mechanical + electrical)
- Second end effector mechanically done
- Test: lock end effector 1, swing arm around on docking port
- Software: ROS modules connected to system, sim integration running
- Jack: continue shell design

# Wednesday Nov 25 Goals

- Second end effector fully complete (electrical done)
- Full arm final assembly (Tether minus shell)
- Verify full software stack: ROS, comms, deterministic control
- Test docking between 2 ports (bounce between them)
- Source and tape magnets onto boxes for pickup testing

# Thursday–Sunday: Testing and Shell

- **Thursday:** Mount all 7 docking ports (morning); attempt to go to Waite Phillips Hall (WPH) for environment testing; set up ENV, start walking on steps/terrain
  - Backup if WPH inaccessible: use Ming’s front steps or mushroom obstacles
- **Friday:** Software debugging (2 tracks: deterministic CV/AprilTag track + policy-based track); box pickup testing with LEDs
- **Saturday:** Shell manufacturing done; full run attempt on setup
- **Sunday:** Mount shell first thing; full run on complete Tether

# Backup Plan and Open Risks

- End effector locking mechanism: untested until Tuesday at earliest
  - If it fails, only ~10 days remain before demo; no budget for electromagnet backup
  - Discuss contingency with full team (Jack, Ming) tomorrow
  - Electromagnet fallback discussed but deprioritized: adds ESP/relay complexity, requires sim and software rework
- WPH access during Thanksgiving: unclear if building is open; explore back entrances
- Shell: low structural impact but important for presentation; parallel print on Prusas to save time
- Software split: deterministic track (CV tuning, AprilTag accuracy) vs. policy track (training, generalization); 2 people per track

# Next Steps

- **Confirm pizza slice status with Jack**

  Screenshot CAD parts and send to Jack to verify which pieces he brought home; Ming machines slices Sunday if needed.
- **Go to MakerZone tonight and print docking boards**

  Print ~6 PETG boards (2 per machine); grab PETG from Robo or borrow from Maker if needed.
- **Discuss end effector contingency with full team Sunday**

  Jack and Ming need to be in the room; assess electromagnet fallback and how long assembly realistically takes.
- **Ask Jack about Thanksgiving availability for shell design**

  Shell design needs to start Monday; confirm how many days he can commit.
- **Coordinate IYA visit with Caroline Kim on Monday**

  Drill holes and attach at least 2 docking ports; bring plates and table back to Ming's house.

---

Meeting transcript: [2026-11-21-final-push-planning-transcript.md](2026-11-21-final-push-planning-transcript.md). Granola: https://notes.granola.ai/d/07318fb5-b92a-4df3-9f40-67ddd314ce61

Whiteboard: [11/22 to 11/25](../assets/2026-11-21-final-push-whiteboard-nov22-25.jpg), [11/26 to 11/29](../assets/2026-11-21-final-push-whiteboard-nov26-29.jpg)
