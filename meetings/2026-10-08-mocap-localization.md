---
type: meeting
date: 2026-10-08  # UNCONFIRMED. Note had no date; this is the day it was added. Happened after the 10-06 mech meeting.
topic: Localization strategy (mocap), hardware testing, software roles
attendees: not recorded (Trent and Jason assigned work)
source: Granola, https://notes.granola.ai/t/be14d3fb-57e6-40d0-a497-b545ea8fc8e8
decisions_logged: D-012 to D-015, D-018
---

# Localization Strategy: Mocap vs. Alternatives

- Mocap chosen as primary localization approach
  - Cameras are small enough to place externally around the environment
  - Only need 3 points: two endpoints and the middle joint to get full joint state
  - SLAM ruled out: too noisy in dark/leafy outdoor conditions
  - TOF/LiDAR sensors ruled out: point cloud overkill, unnecessary complexity
- Mocap source options, in priority order:
  1. Borrow IYA (Avalon) system: preferred, but high chance of “no”
  2. Ask WISP team: they may also use mocap, worth checking
  3. Build/source own open-source mocap system
  4. Fall back to encoders: present on robot, but drift observed last time
- AprilTags considered as backup for end-effector alignment
  - Camera on end effector + AprilTag in docking hole for fine alignment
  - Need mechs to leave a centered hole in the end effector design for this
  - Dim lighting is a hard constraint: pure vision/cameras alone won’t work

# Hardware Testing and Software Integration

- ESP-NOW wireless comms test happening this week
  - 3 motors wired to ESP-NOW nodes, test if they move in a straight line
  - If it passes, confirms wireless comms strategy and module build-out begins
- Key software challenge: 3 wireless modules must behave as one unified arm in ROS
  - Need low-level comms layer with packet loss handling and redundancy
  - If redundancy is solid, simulation noise injection matters less
- Compute: all processing offboard (no onboard compute on robot)
  - Battery-powered, so keeping compute off the bot is the right call
  - L1A cluster compute discussed for future model training needs
- Locomotion via motion planning (no RL needed at this stage)
  - Manipulation (end effector grab) is a secondary target, not primary
  - VLA/VLM ideas floated for later stages, deprioritized for now

# Team Roles and Next Steps

- Mocap setup and testing assigned to software team (Trent and Jason)
  - Everyone else occupied on mechanical/electrical side
  - Both Trent and Jason back Monday, so mocap work starts next week
- Iris: may shift from ROS to electrical given bandwidth constraints
- Trent and Jason: also taking on low-level comms software together
- IYA mocap decision expected by Monday; fallback plan needed regardless
- Meeting with designers needs to be scheduled to align on end effector hole placement

# Next Steps

- **Ask IYA (through Ming) to borrow mocap system**
- **Check with WISP team on their mocap setup**
- **Schedule meeting with mechanical designers**
- **Trent and Jason: set up and test mocap system next week** (Trent, Jason)

---

Chat with meeting transcript: https://notes.granola.ai/t/be14d3fb-57e6-40d0-a497-b545ea8fc8e8