---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-10-08
---

# Tether: Project Overview

## What it is

Tether is a Terra Labs project for fall 2026. It turns **Cove**, the 7-DOF arm the team built in spring 2026, into an **inchworm robot**. Tether has a gripper on both ends. One end holds on while the other swings to the next spot, then they swap. It has no fixed base and no cable to a wall. The goal is a robot that can walk, climb, and still manipulate.

In code the robot is called **COVE2**. "Tether" and "COVE2" refer to the same robot.

## Where things stand (as of 2026-10-08)

- **Cove** is built and moves. It is the hardware starting point.
- **Tether in software:** the sim (COVE2 Robot Studio) can plan collision-free walking, a ladder climb, and a loop around a table on Cove's model. See [the tether repo](https://github.com/TerralabsCove/tether).
- **Tether in hardware:** the mechanical layout is chosen (D-002, D-003). The arm is now 3 wireless modules (D-020), and the first module is being built as an MVP (D-011). Electrical is on breadboards (D-007).
- **Direction changes since kickoff:** compute moved fully offboard (D-013). The BMS was dropped (D-008). RL is not needed for now; locomotion uses motion planning (D-014).

## Goals, in priority order

1. Walk: alternating-anchor locomotion on the ground.
2. Climb: e.g. a ladder.
3. Manipulate with an end-effector claw. Secondary target (D-014).

## Roadmap: validation gates

From the kickoff deck and the repo's validation plan. Rough timing from kickoff: G0 and G2 in the first month, G3 and G4 bench tests mid-semester, first G5 steps by the end of the semester. Real dates are still to be set.

| Gate | Name | Track | Status |
|---|---|---|---|
| G0 | Model freeze: audit Cove hardware against the URDF | software + hardware | not started |
| G1 | Kinematic feasibility | software | done in sim |
| G2 | Scripted dynamics | software | started |
| G3 | Contact + robustness (RL now deprioritized, D-014) | software | not started |
| G4 | Hardware bench tests: gripper pull-off, battery, slip ring / cable rotation, comms, motor watchdogs | hardware | not started |
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
| Sim codebase snapshot | `PROJECT_SUMMARY.md` in the tether repo |
| Kickoff deck | [assets/2026-09-27-tether-kickoff.pptx](../assets/2026-09-27-tether-kickoff.pptx) |
