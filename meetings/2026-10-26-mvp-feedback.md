---
type: meeting
date: 2026-10-26
topic: Leads meeting. MVP feedback, second-half timeline, task sheets, Tether breakout
attendees: not recorded. No speaker labels. John recorded.
source: Granola, https://notes.granola.ai/d/d41c2012-9afb-400e-9171-ae3d27013e01
decisions_logged: none
---

<!-- Excerpt of the Granola summary. General club items are left out. "Jack Corbino" is Jack Carpino, misheard by
     Granola. Later changes: the dates here slipped, see the 2026-11-05 meeting. -->

# MVP Feedback and Second Half Kickoff

- MVP demo went well, better than expected
- Key feedback: incorporate what was heard, adjust plans accordingly
- Teams should debrief members on feedback and note any presentation improvements

# Timeline and Task Assignment

- Currently week 12; demo day is the week after Thanksgiving break
  - Projects should be complete at least 1-2 days before Thanksgiving
  - Roughly 5 weeks of working time remaining
- Task sheet system introduced (modeled on Ripple’s sheet)
  - Broken down per sub-team, per week, with specific individual tasks
  - This week’s tasks must be fully defined; future weeks can be higher-level initially
  - By tomorrow morning: every member should have at least one assigned task visible in the sheet
  - After GMs each Friday: members fill out their own tasks for the following week
  - GitHub project board can stay; sync it to the Google Sheet via Terabot

# Tether Team Breakout

- Electronics: plugin validation and communication structure done; now swapping to C5s and testing 5 GHz
- Mechanical: CAD freeze nearly complete; Jack Corbino machining parts, targeting Friday completion; module assembly over the weekend
- End effector (Isaac): 3D print Tuesday night, assemble Wednesday, test Wednesday/Thursday, order external parts Friday
  - Validation needed by end of week; FEA unlikely to add more value at this stage
- Software (Jason): building URDF simulation to calculate max reach, step size, and obstacle spacing parameters
  - Designers to be looped in once simulation output is ready
- Waterjet tolerances: test hole sizes first before cutting final parts
- Slip ring / through-axle rod: main remaining blocker
  - Concern raised about the plate-to-rod connection being the weakest structural point
  - FEA needed on that joint; titanium bolts alone may not hold given tip-of-arm load
  - End effector rotation: likely only needs 90-180 degrees (4 pegs, 90° apart); continuous 360 not required
  - Cable chain is a fallback option if FEA fails
  - Resolution: forward full discussion to Jack, confirm manufacturing approach

# Next Steps

- **Complete task sheet by tomorrow morning** (John Peng)

  Every Tether member needs at least one specific assigned task visible in the Google Sheet.
- **Forward slip ring and rod discussion to Jack** (John Peng)

  Confirm plate fastening approach and ensure FEA is completed on the joint; invite Steve to the chat.
- **Validate end effector prototype** (Isaac)

  3D print Tuesday, assemble Wednesday, test by Thursday, ready to order external parts Friday.
- **Run dry electrical test with Hansi and Iris**

  Transfer robot to C5s and complete a full electrical run without arm assembly.
- **Get URDF simulation output from Jason, then meet with designers**

  Simulation needed to finalize obstacle spacing and demo day parameters; designer sync is overdue.

---

Meeting transcript and chat: https://notes.granola.ai/d/d41c2012-9afb-400e-9171-ae3d27013e01
