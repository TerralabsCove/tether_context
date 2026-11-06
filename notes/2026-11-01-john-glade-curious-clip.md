---
status: draft
owner: John Peng
last_reviewed: 2026-11-01
---

# Mood clip: a curious Tether in the Glade (sim, 2026-11-01)

> **Scope change, 2026-11-04 ([D-030](../truth/decisions.md)):** climbing is out of scope, including the tree.
> The reach toward the tree trunk at the end of this clip is not a planned capability.

Written by John's AI agent for the Glade set designers. This is a mood piece, not a design. Everything here is
**[assumed]**: it comes from the step-reach sim on the corrected URDF (14.35 kg), and nothing is measured on
hardware. Code: tether_controls `sim/step_reach_sim/glade_curious.py`. Dock rules and loads are in the
[designer clips note](2026-11-01-john-designer-capability-clips.md).

- [Clip (107 s)](2026-11-01-john-glade-curious-clip/glade_curious.mp4)
- [Still: studying a leaf](2026-11-01-john-glade-curious-clip/still_leaf.jpg)
- [Still: the cairn, then reaching toward the tree](2026-11-01-john-glade-curious-clip/still_cairn_and_tree.jpg)

## What it shows

1. The robot walks in along a trail of floor docks through moss, about 1 ft 6 in (0.45 m) apart.
2. It stops at a leaf. The free gripper hovers over it, leans in, then looks again from the other side,
   turning its spin motor like a head tilt.
3. It stacks a small cairn: three prop stones onto a base rock that is part of the set.
4. It steps back and looks at the cairn, then walks to the tree and reaches up toward the trunk.

The set uses the Glade check-in deck's tree (6 ft 10 in, 3 ft at the base) with a pond, ferns and fallen leaves.
The look is stylised: the robot keeps its real colours, so it reads as tech in nature.

## What is real and what is not

- **"Looking" is only a pose.** The robot has no camera in this sim. The curiosity is the free gripper
  hovering near something. Every pose is collision-checked like a normal step.
- **It only grips docks.** It cannot pick up a real leaf or a loose rock. Each cairn stone has a dock on top,
  left visible on purpose.
- **The stones are light props**: 1.0, 1.5 and 2.0 kg, up to 0.30 m (12 in) across. A real rock that size
  weighs 10–20 kg, far beyond what the arm can carry.
- **Torque.** Motors stay within rated torque apart from one brief peak of 1.06× rated on a 4340 roll motor.
  It happens as the robot lifts the first stone off the ground, and stays well under peak.
- Speed is not real.

## For the designers

- A cairn, or any stacked feature the robot builds, needs a dock in each piece and a base fixed to the floor.
- Every spot the robot stands on needs a floor dock fixed to structure, not to moss or a foam shell.
- The tree reach is a gesture only. The robot does not dock to the trunk here, and the trunk has no docks.
