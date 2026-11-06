---
status: draft
owner: John Peng
last_reviewed: 2026-11-01
---

# What the arm can do, for the set designers (sim clips, 2026-11-01)

> **Scope change, 2026-11-04 ([D-030](../truth/decisions.md)):** climbing is out of scope, including the tree.
> The tree spiral, vertical-surface, floor-to-wall and hanging clips no longer describe a planned capability.

Written by John's AI agent for the meeting with the Glade experience-design team. Not authoritative. Everything
here is **[assumed]**: it comes from the step-reach sim on the corrected URDF (14.35 kg), and nothing is measured
on hardware. Background and method: [step-reach note](2026-10-28-john-step-reach-sim.md). Clips and sheets are in
[2026-11-01-john-designer-capability-clips/](2026-11-01-john-designer-capability-clips/). Code:
tether_controls `sim/step_reach_sim/showcase.py` and `showcase_sheets.py`.

All numbers are **comfortable** limits: the holding motors stay within their rated (continuous) torque at each
dock. Clips use feet and metres, a 5 ft 9 in person for scale and 1 ft floor squares. Animation speed is not real.

## Clips

| Clip | What it shows |
|---|---|
| [01 How it moves](2026-11-01-john-designer-capability-clips/01_how_it_moves.mp4) | Dock to dock, end over end. One dock holds the whole robot during a step. |
| [02 Longest comfortable step](2026-11-01-john-designer-capability-clips/02_longest_comfortable_step.mp4) | 1 ft 11 in (0.58 m) on the flat; absolute limit 2 ft 7 in (0.80 m). The arm rises 2 ft 8 in (0.80 m) above the docks. |
| [03 Where the next dock can go](2026-11-01-john-designer-capability-clips/03_where_the_next_dock_can_go.mp4) | Side view of every comfortable spot for the next dock, with five example reaches. |
| [04 Steps up and down](2026-11-01-john-designer-capability-clips/04_steps_up_and_down.mp4) | Platforms 1 ft 4 in (0.40 m) apart in height. |
| [05 Up a 30° slope](2026-11-01-john-designer-capability-clips/05_up_a_slope.mp4) | 2 ft (0.60 m) steps up the slope. |
| [06 Straight up a vertical surface](2026-11-01-john-designer-capability-clips/06_straight_up_a_vertical_surface.mp4) | Docks in a vertical line 2 ft 4 in (0.70 m) apart. |
| [07 Onto a wall and over the top](2026-11-01-john-designer-capability-clips/07_floor_to_wall_and_over_the_top.mp4) | Floor to wall, up, and over a 4 ft 3 in (1.30 m) edge. |
| [08 Concept: platforms spiralling up the tree](2026-11-01-john-designer-capability-clips/08_concept_tree_spiral.mp4) | Six platforms, 1 ft (0.30 m) rise and about 1 ft 6 in (0.46 m) apart, around the 6 ft 10 in tree (3 ft / 2.5 ft / 2 ft diameter taper). A concept, not a decision. |
| [09 Hanging underneath](2026-11-01-john-designer-capability-clips/09_hanging_underneath.mp4) | Under a beam 7 ft 5 in (2.25 m) up. Gripper not tested for pull-out. |

Stills of the extremes (level, highest step up, deepest step down, clear space, vertical, tree, hanging) are in
[stills/](2026-11-01-john-designer-capability-clips/stills/). Everything is also on one private page,
"Tether Reach Guide" (https://claude.ai/artifact/DXjihNZxuEWTfiGrGoq6Zz), shared only when John chooses.

Two summary sheets: [where the docks can go](2026-11-01-john-designer-capability-clips/10a_where_docks_can_go.png) and
[what each dock must hold](2026-11-01-john-designer-capability-clips/10b_what_docks_must_hold.png).

[Dimensions](2026-11-01-john-designer-capability-clips/11_dimensions.png), from the CAD model laid out straight:
5 ft 3 in (1.60 m) gripper tip to tip, 4 ft 9 in (1.44 m) dock face to dock face. Two 2 ft 5 in (0.73 m) end
modules (12.8 lb, 5.8 kg each) and a 6 in (0.15 m) middle module (6.0 lb, 2.7 kg). Bends 1 ft (0.30 m) from each
dock face and 1 ft 4 in (0.42 m) from the middle bend. Thickest part about 5½ × 7½ in (0.14 × 0.19 m).

## Dock placement rules

| Situation | Comfortable rule |
|---|---|
| Flat floor or platform | Docks up to 1 ft 11 in (0.58 m) apart |
| Step up | Up to 1 ft 9 in (0.54 m) higher, docks up to 1 ft 5 in (0.44 m) apart. A 1 ft 4 in (0.40 m) rise allows 2 ft (0.62 m). |
| Step down | Up to 2 ft 2 in (0.66 m) lower, docks up to 1 ft 5 in (0.44 m) apart |
| 30° slope | Up or down 2 ft 3 in (0.70 m); across under 10 in (0.26 m) |
| Vertical surface | In a vertical line, up to 2 ft 7 in (0.80 m) apart; sideways under 5 in (0.14 m) |
| Floor to wall | First wall dock about 1 ft (0.30 m) up; last floor dock 1 ft 4 in to 2 ft 9 in (0.40 to 0.84 m) from the wall |
| Over a top edge | Both docks within about 8 in (0.20 m) of the edge |
| Hanging underneath | Up to 1 ft 11 in (0.58 m) apart; needs a gripper pull-out test first |

## Loads on a dock and its fixing

Static, swing gripper unsupported, before any safety factor. Worst value along each clip's path.

| Where the dock is | Force | Prying | Twist |
|---|---|---|---|
| Floor or platform | 32 lbf (141 N) pressing in | up to 33 lbf·ft (45 Nm) | none |
| 30° slope | 28 lbf in, 16 lbf along (122 N, 70 N) | up to 53 lbf·ft (72 Nm) | up to 20 lbf·ft (27 Nm) |
| Vertical surface | 32 lbf (141 N) along the surface | up to 75 lbf·ft (102 Nm) | up to 20 lbf·ft (27 Nm) |
| Over a top edge | 32 lbf (141 N) | up to 70 lbf·ft (95 Nm) | up to 20 lbf·ft (27 Nm) |
| Hanging underneath | 32 lbf (141 N) pulling out | up to 30 lbf·ft (40 Nm) | none |

Twist is capped by the gripper-spin motor's 27 Nm peak. The vertical-surface prying (102 Nm) happens mid-swing on
2 ft 4 in steps and is a little above the 95 Nm worst case in the step-reach note; it is still inside the
end-effector deck's proposed 200 Nm target.

## For the meeting

- **The tree is chicken wire and plaster over a wooden stand** (Glade check-in deck, p. 10). Docks must bolt into
  the wooden stand, not the shell. Each one carries the whole robot.
- **The tree's own questions** (p. 12) ask how to keep it sound "with the weight of the components". The loads
  table above is the answer for the robot's part.
- The robot mainly lives on one element. The tree spiral is one option; the same rules work for the back wall,
  the rocks, or a purpose-built structure.

## Corrections to the step-reach note

- **Step-up height with the 12 cm lift-out.** The step-reach note gives ±0.66 m as the max step height. That is
  the static pose. The gripper must also come down into the dock from 12 cm above it, and above about 0.54 m that
  approach pose collides with the arm's own brackets. So the usable step up is **0.54 m** (comfortable, at
  0.26–0.44 m forward); step down stays 0.66 m. At +0.5 m the comfortable reach is 0.54 m, not 0.62 m. A shorter
  lift-out would recover some of this.
- **Planner change.** The showcase planner now prefers docked poses within rated torque. Earlier plans sometimes
  docked with the arm leaning sideways and the roll motors above rated, although an upright pose existed.
  Mid-swing, the roll and gripper-spin motors still go over rated: up to 1.8x on most clips, and over the edge
  the A roll reaches 23 Nm and the gripper spin 26 Nm, just under their 27 Nm peak.
