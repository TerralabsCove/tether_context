---
status: draft
owner: John Peng
last_reviewed: 2026-11-01
---

# Concept clips: Tether as a construction robot (sim, 2026-11-01)

Written by John's AI agent for the project managers. A concept, not a design. Everything here is **[assumed]**:
it is from the step-reach sim on the corrected URDF (14.35 kg), and nothing is measured on hardware. Background:
[step-reach note](2026-10-28-john-step-reach-sim.md). Code: cove-controls `scripts/step_reach_sim/construct.py`.

- [Clip (66 s)](2026-11-01-john-construction-concept/construction_concept.mp4)
- [Still: carrying a block onto the tower](2026-11-01-john-construction-concept/still_stacking.jpg)

## What the clip shows

1. A grid of floor docks, 0.50 m (1 ft 8 in) apart, inside the 0.58 m comfortable step.
2. The robot walks two steps across the grid to the dock next to a pile of four blocks.
3. One end stays in that floor dock. The other end locks into the top of a block, lifts it, swings it over
   and sets it down. The free gripper's spin motor turns each block so the layers cross at 90°.
4. Four blocks become a four-layer tower, 0.48 m (1 ft 7 in) tall. Then the free end goes back to a floor dock.

## Second clip: building a wall

- [Clip (80 s)](2026-11-01-john-construction-concept/wall_concept.mp4),
  [still: carrying](2026-11-01-john-construction-concept/still_wall_carrying.jpg),
  [still: finished wall](2026-11-01-john-construction-concept/still_wall_done.jpg).
  Code: cove-controls `scripts/step_reach_sim/wall.py`.
- Floor docks run along the wall line, 0.40 m (1 ft 4 in) apart: one block length. Grid rows are 0.60 m apart.
- A pile of four blocks is staged beside each work dock. From one work dock the robot reaches the pile and
  two wall columns, and builds that 0.80 m (2 ft 7 in) section two courses high.
- It parks its free end in the next floor dock, steps 0.40 m along the row and builds the next section.
  The second section is shown 3× faster.
- Result: 1.6 m (5 ft 3 in) of wall, 0.24 m (9.4 in) high, from 8 blocks and two work docks.
- Worst carry pose: 0.80× rated torque with the 2.5 kg block, so about **4.5 kg (9.9 lb)** is the comfortable
  payload along this path. That is more margin than the tower, because nothing is lifted above 0.36 m.
- The blocks are stacked in columns, not in a running bond, because each pocket must sit over the dock of
  the block below. A running bond would need two docks per block or a different interface.

## Assumptions in the sim

| Item | Value |
|---|---|
| Block | 0.40 × 0.20 × 0.12 m (16 × 8 × 4.7 in), 2.5 kg (5.5 lb). Chosen for the demo, not a real product. |
| Block interface | A female dock on top, the same as a floor dock. A pocket underneath fits over the dock below, so blocks stack. Neither is designed. |
| Carry | Block mass in the static gravity torques. Block box collision-checked against the scene and the arm. Kept within 50° of level. |
| Torque limit | Every motor within rated (continuous) torque for the whole clip, including while carrying. |

## Payload

- Along this path, the worst carry pose reaches 0.99× rated torque with the 2.5 kg block. So **about 2.5 kg
  (5.5 lb) is the comfortable payload for this layout**. That is tight.
- In the best pose for each spot, the free gripper can hold more: roughly 4–9 kg at 0.3–0.4 m reach and 0–0.4 m
  up, about 1.4 kg at 0.5 m on the floor, and under 1 kg at 0.58 m (rated torque, static, gripper pointing
  down). The planner does not yet
  pick torque-minimising carry paths, so 2.5 kg is conservative for this scene.
- A real brick (about 2–2.5 kg) is in range at short reach. A full 8 ft 2×4 (about 4 kg, 2.4 m long) is
  not: its length puts a large twist on the gripper unless it is held at its centre.

## Open items

- A dock built into the material, or a carrier the material sits in.
- How blocks lock to each other once placed (the sim only stacks them).
- Gripper capacity while carrying: pull-out and bending with a payload hanging below.
- Payload tests on hardware.
