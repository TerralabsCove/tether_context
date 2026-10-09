---
type: meeting
date: 2026-10-06
topic: Mechanical layout, batteries, end effector, electronics
attendees: not recorded (mech team: Isaac, Ryan, Jack targeted)
source: Granola, https://notes.granola.ai/t/132a2823-7580-45c3-9c57-b6b029be2e9b-00demib2
decisions_logged: D-002 to D-006, D-010, D-011, D-017
---

# Tether Mech Meeting

Tue, 06 Oct 26

## Configuration Decision: Asymmetric vs. Offset Layout

- Settled on “straighter but offset” configuration, not fully diagonal
  - Full diagonal rejected: too unbalanced, screws would fail
  - Offset gives more joint freedom without requiring full 360 rotation
- Key change from Cove: middle joint needs continuous 360 spin capability
  - Cove’s joint range was too limited; IK couldn’t reach some positions
  - Offset geometry solves this without full diagonal tradeoff

## Battery Layout

- 3 battery sizes, 5-6 batteries total across the arm
  - Two sizes shared between end modules (same size each pair)
  - Middle module has its own separate battery
- Placement: batteries on left side for bottom modules, right side for top
  - Spinning joints get batteries on the outside with a spacer to avoid collision
  - Stationary parts mount on the inside with hard mounts to motor
- Middle battery powers only its one motor; end batteries power 3 motors each
- 5,000 mAh battery spec for main modules; target runtime ~2 hours
  - Small batteries ~$50 each; quick-swap considered

## End Effector and Claw

- Symmetric claw design: one servo-based claw on each end of the arm
  - Both claws powered by their respective end-effector battery systems
  - Claw is retractable/foldable into the docking connector housing
- Docking mechanism is circular; can be designed to lock in a fixed orientation
  - Geometry can enforce alignment (e.g. triangle or pinned shape), removing need for a rotation motor there
- Claw motor permanently part of the claw module, not the arm
  - Means each end always needs a claw module attached

## Electronics and Communication

- 5 ESPs needed (one brain per module), all communicating wirelessly
  - No wiring between modules; fully wireless inter-module comms
  - Each battery connects to its own motor driver (Max 2)
- NRF / ESB (NRF ESB protocol) preferred for slow sensor data streaming
  - BLE ruled out; NRF fine for low-bandwidth data
- Camera/video streaming is a separate, unresolved problem
  - ESP not sufficient bandwidth for video
  - Options floated: dedicated wireless video module (DJI-style), Raspberry Pi, Jetson (Jetson ruled out as too heavy)
  - FireEye camera preferred over TOF; TOF reliability questioned
  - Need answers from Jason and Trent on software/sensor approach

## Build Plan and Modules

- 5 modules total in the arm
- Next step: build one module first as MVP, then replicate
  - Jack to work on first module
  - Others to handle the opposite-side exterior module
- Battery sizing for end-effector module still needs to be specced out
  - Team will find a battery and add it to the CAD model

## Next Meeting and Logistics

- Regular meeting cadence being established
  - Fridays at 5 PM and Sundays (both recurring)
- Urgent: loop in Jason and Trent (software) this weekend to unblock sensor/comms decisions
  - Neither has replied to the calendar invite yet

## Next Steps

- **Build first arm module as MVP** (Jack)
- **Spec and source end-effector battery**
- **Ping Jason and Trent to meet this weekend**
- **Resolve camera and video streaming approach**

---

Chat with meeting transcript: https://notes.granola.ai/t/132a2823-7580-45c3-9c57-b6b029be2e9b-00demib2