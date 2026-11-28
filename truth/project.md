---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-28
---

# Tether: Project Overview

## What it is

Tether is a Terra Labs project for fall 2026. It turns **Cove**, the 7-DOF arm the team built in spring 2026, into an **inchworm robot**. Tether has a gripper on both ends. One end holds on while the other swings to the next spot, then they swap. It has no fixed base and no cable to a wall. The goal is a robot that can walk, climb, and still manipulate.

In code the robot is called **COVE2**. "Tether" and "COVE2" refer to the same robot.

## Where things stand (as of 2026-11-21)

- **Demo day: 12/3, at Watt Hall B1. Be there from 5 PM** (D-051). Goal for the end of Thanksgiving break (11/29): the arm running on the setup (D-050).
- **Schedule:** day by day in [plans/final-push-schedule.md](../plans/final-push-schedule.md). It is tight and assumes Ming's end effector works the first time.
- **Mech:** both ends use Ming's end effector (D-052). Most of its parts are machined. Still open: the pizza slices, one TAG-Mech-005 (to be machined at the Castle, per John 2026-11-22), the center spacer. No end effector is assembled yet. The shell is not designed yet.
- **Electrical:** final wiring of the 3 modules is planned for 11/22. End effector electronics are not finished.
- **Software:** ROS on a laptop with the sim connected, then two tracks: a deterministic AprilTag path and a trained policy (D-053). No mocap (D-054). See the plan.
- **Site:** Watt Hall B1 is the demo site and the practice site (D-051). Tether climbs the steps there (D-055). Access over Thanksgiving is not confirmed. Otherwise practice at Ming's house.

## Earlier status (as of 2026-11-06)

- **Schedule:** about 2 weeks behind (11-05 meeting). Worst case, software-only work starts in about 1.5–2 weeks. Demo day was then given as the week of 11/30. It is 12/3 (D-051).
- **Blocking assembly:** water-jet panels at Baum (D-041), end mounts waiting on a tapping bit, and the end effector design (D-040).
- **Electrical:** the 11-02 meeting reports batteries in hand, a motor tested wirelessly, and the robot fully wireless. No recorded artifact is linked yet.
- **Localization:** one camera per end reading AprilTags (D-037, D-038), with the GC2053 stock lens, not a fisheye (D-046). The reCamera read tags on its own in a [first handheld test](../notes/2026-11-06-john-claw-camera-followups.md). Wireless is untested.
- **Software:** thin. See D-035.
- **Demo:** Area D. Curious robot moving objects between piles is the leading idea, not final. See the [designer meeting](../meetings/2026-11-01-designer-demo.md).

## Earlier status (as of 2026-10-11)

- **Cove** is built and moves. It is the hardware starting point.
- **Tether in software:** the sim (COVE2 Robot Studio) can plan collision-free walking, a ladder climb, and a loop around a table on Cove's model. See [the tether repo](https://github.com/TerralabsCove/tether).
- **Tether in hardware:** the mechanical layout is chosen (D-002, D-003). The arm is now 3 wireless modules (D-020), and the first module is being built as an MVP (D-011). Electrical is on breadboards (D-007).
- **ESP-NOW + Damiao testbed (tethersmall), 2026-10-11:** an RL policy on a Mac drove two Damiao motors through per-module ESP32s over ESP-NOW (offboard compute, wireless modules, ESP-NOW first: D-013, D-020, D-019). It ran 20 s with no faults and reproduced the sim gait. The link works but has little margin. See [robot.md](robot.md#tethersmall-testbed-2026-10-11) and [the note](../notes/2026-10-11-john-tethersmall-rl-over-espnow.md). D-014 (no RL) has since been superseded by D-053.
- **Direction changes since kickoff:** compute moved fully offboard (D-013). The BMS was dropped (D-008). RL is not needed for now; locomotion uses motion planning (D-014).

## Goals, in priority order

1. Walk: alternating-anchor locomotion on the ground.
2. Climb: e.g. a ladder.
3. Manipulate with an end-effector claw. Secondary target (D-014).

Climbing: the steps at Watt Hall B1 are in scope (D-055). [PR #8](https://github.com/TerralabsCove/tether_context/pull/8), which proposes dropping climbing, is still open.

## Roadmap: validation gates

From the kickoff deck and the repo's validation plan. Rough timing from kickoff: G0 and G2 in the first month, G3 and G4 bench tests mid-semester, first G5 steps by the end of the semester. Real dates are still to be set.

| Gate | Name | Track | Status |
|---|---|---|---|
| G0 | Model freeze: audit Cove hardware against the URDF | software + hardware | not started |
| G1 | Kinematic feasibility | software | done in sim |
| G2 | Scripted dynamics | software | started |
| G3 | Contact + robustness (RL now deprioritized, D-014) | software | not started |
| G4 | Hardware bench tests: gripper pull-off, battery, slip ring / cable rotation, comms, motor watchdogs | hardware | comms and motor watchdogs exercised on the tethersmall testbed (2026-10-11); the rest not started |
| G5 | Integrated locomotion: first supported steps on the real robot, compared against sim logs | both | not started |

Full gate definitions live in the code repo: `docs/VALIDATION_PLAN.md` in [tether](https://github.com/TerralabsCove/tether).

## Working principles (sim-to-real)

1. Verify by artifacts, not by the absence of errors.
2. Generate sim values from audited ground truth.
3. Keep verified and assumed facts explicitly separate.
4. Keep deterministic evaluation separate from training curves.
5. Seed A/B comparisons and sweep difficulty.

## Where to find more

| What | Where |
|---|---|
| Current robot specs, verified vs assumed | [robot.md](robot.md) |
| Who does what | [team.md](team.md) |
| Every decision and why | [decisions.md](decisions.md) |
| What's unresolved | [open-questions.md](open-questions.md) |
| Sim codebase snapshot | `PROJECT_SUMMARY.md` in the tether repo (archived as of 2026-11-28) |
| ESP-NOW + Damiao testbed (RL over ESP-NOW) | [tethersmall repo](https://github.com/TerralabsCove/tethersmall) (archived), `docs/ESPNOW_BRINGUP.md` |
| Every ESP's firmware, and which env goes on which board | [tether-firmware](https://github.com/TerralabsCove/tether-firmware) (private), its `README.md` |
| Kickoff deck | [assets/2026-09-27-tether-kickoff.pptx](../assets/2026-09-27-tether-kickoff.pptx) |
| BOM (canonical, D-031) | [Tether BOM (F26 - Terra Labs)](https://docs.google.com/spreadsheets/d/16mWqcQNEYmytco0OLClecacfsPCy_qwmkcIXcmFBWYw/edit) |
| Rolling status from Discord (unverified) | [Notion: Tether and Terra Everything](https://app.notion.com/p/407b37231fea8062a1b0f09d333779b4), [digest](../notes/2026-11-06-john-notion-digest.md) |
