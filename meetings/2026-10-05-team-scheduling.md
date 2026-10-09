---
type: meeting
date: 2026-10-05
topic: Team scheduling and task delegation (mech, electrical, software)
attendees: not recorded (PMs; Ming present)
source: Granola, https://notes.granola.ai/t/8fbf0dbc-ff36-4db5-9905-dad2db60c26c-00demib2
decisions_logged: D-007, D-008, D-009, D-016
---

# Project team scheduling and task delegation for mechanical, electrical, and software work

Mon, 05 Oct 26

## Scheduling: Mechanical and Electrical Meetings

- Mechanical meeting: Tuesday at 6:30 PM
  - Isaac, Ryan, Jack targeted; Jack Carpino leaving Wednesday so Tuesday is the deadline
  - Goal: lock in a design direction and force a draft to pass to Jason
- Electrical meeting: Wednesday at 6:15–7:30 PM (before TerraGM at 7 PM)
  - Iris confirmed available that window; Hansi, Isaac, Jack Carpino all unavailable Wednesday night
- Software meeting: skipped this week (faded)
  - Nothing concrete enough to discuss yet; software depends on electrical and mech progress
  - Revisit next week, possibly Sunday (fall break, most people still on campus)

## Electrical Design Decisions

- Design target: breadboard only, no custom PCB yet
  - House all power and communication electronics on a single breadboard
- Power architecture settled:
  - Motors connect directly (have built-in min-voltage shutoff, no BMS needed)
  - DC-DC converter to step down for ESPs (not a separate battery)
  - ESP antenna: leave top exposed, no shell coverage to avoid interference
- Hardware on hand: Xiao from Ming’s house; streaming/sensor electronics purchased
  - Still need to sort remaining power components

## Software and Team Context

- Trent assigned as embedded software lead (Iris too busy with RPL/Triple L)
  - Bring Trent to Ming’s house Wednesday after gym to get up to speed
  - Jason (high-level software) is waiting on mech and electrical progress
- Key concern: PM team holds too much context; members building without full picture
- Broader issue: member availability underreported on scheduling tools; plan to ask in person going forward

## Next Steps

- **Confirm Iris availability for Wednesday 6:15–7:30 PM**
- **Lock in mechanical meeting Tuesday at 6:30 PM**
- **Tell electrical team to start breadboarding before Tuesday**
- **Bring Trent to Ming's house Wednesday after gym**
- **Ask software team about Sunday availability for next week**

---

Chat with meeting transcript: https://notes.granola.ai/t/8fbf0dbc-ff36-4db5-9905-dad2db60c26c-00demib2