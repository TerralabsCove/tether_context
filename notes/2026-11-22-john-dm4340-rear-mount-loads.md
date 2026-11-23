---
status: draft
owner: John Peng (hardware)
last_reviewed: 2026-11-22
---

# DM-J4340P-2EC rear mount: will the four rear bolts hold?

Written by John's AI agent. Not authoritative. Everything here is **[assumed]**: it is calculated from the arm URDF and the motor manual, and nothing is measured. Follows the [stripped-threads note](2026-11-11-john-dm4340-stripped-threads.md), which has the hole drawing and the repair history.

## The problem

Per John, 2026-11-22: every 4340 is held on both ends, and one of those ends is the rear face with 4 × M2.5 on a ⌀38 circle. That face is not meant to take load. Some holes were damaged by M3 screws and are being retapped to M4. The backup is a strong epoxy between the motor bottom and the mount.

The 11-12 update in the earlier note says the retap was done. On 11-22 it was described as still to do. Which motors are done is not recorded.

## Bottom line

1. **Well-tapped M4 holds floor and step loads on paper.** Static safety factor about 3 to 7 on the worst bolt.
2. **It does not cover a drop or a hard impact.** A 2× dynamic factor leaves 1.4 to 3.5 on the floor case.
3. **M4 only helps if cut with a bottoming tap.** With a plug or taper tap it is no stronger than an undamaged M2.5.
4. **The rear cap may be a second weak point that M4 does not touch.** See [below](#the-rear-cap).
5. **Epoxy on the rear face alone is not a reliable backup for bending.** Epoxy around the motor body is.

## Method

- Model: a local copy of the corrected Tether arm URDF (`terra_arm_description/urdf/arm.urdf`, 14.35 kg, see [robot.md](../truth/robot.md#simulation-model)). It still has the old gripper and the slip rings, which are dropped (D-047, D-052).
- One end anchored. Static gravity only, no dynamics.
- Floor step: both end columns vertical, pitch joints 0.425 m from the middle, the two middle links make the step. This reproduces the [step-reach sim](2026-10-28-john-step-reach-sim.md): 59 Nm at a 0.84 m step (sim 59), 31 Nm at 0.44 m (sim 32).
- Rear-face positions along the arm, from the URDF: gripper-spin motors about 0.50 m from the middle, roll motors about 0.14 m.
- Bolt tension: rigid plate on 4 bolts at 19 mm radius. Two limits: the mount seats flat on the whole ⌀57 face (pivot at the edge), or it has no support at the edge (pivot through the centre).
- Thread strip: standard internal-thread shear area at minimum tolerance and at nominal size, with 207 MPa shear strength (6061-T6). The housing alloy is not confirmed.

## Loads at each rear face

| Motor | 0.44 m floor step | 0.84 m floor step | Worst case |
|---|---|---|---|
| Gripper spin, anchored end | 31 Nm | 59 Nm | about 95 Nm (floor to wall, over an edge, from the sim) |
| Roll, anchored side | 17 Nm | 32 Nm | 35 Nm (arm straight out, horizontal) |
| Roll, swinging side | 6 Nm | 12 Nm | 16 Nm (same) |
| Gripper spin, swinging end | about 0 | about 0 | 2 Nm (same) |

The gripper-spin motor at the anchored end carries nearly the whole arm, about 125 N. Each rear face also carries its motor's torque as twist: 10 to 13 Nm in a normal swing, up to the 27 Nm peak.

## Tension in the worst bolt

| Bending | Seated flat on the whole face | No support at the edge |
|---|---|---|
| 32 Nm | 0.3 kN | 0.8 kN |
| 59 Nm | 0.6 kN | 1.6 kN |
| 95 Nm | 1.0 kN | 2.5 kN |

Four bolts on a ⌀38 circle is a short lever arm. That, more than the thread size, is the weakness.

## Thread strength per bolt

| Thread | Engaged length | Pull-out strength |
|---|---|---|
| M2.5, undamaged | 3.2 mm | 2.4 to 4 kN (screw or thread, whichever goes first) |
| M2.5 cut by M3 screws | unknown | unknown, treat as near zero |
| M4, bottoming tap | about 2.75 mm | 4.4 to 6.3 kN |
| M4, plug or taper tap | about 1.5 mm | 2.4 to 3.4 kN |

The hole is 4 mm deep (manual). M4 pitch is 0.7 mm, so a normal tap leaves about two full threads.

If the housing is a weaker cast alloy (150 MPa shear), every thread figure drops by about a quarter.

## Margins with good M4

| Case | Static | With a 2× dynamic factor |
|---|---|---|
| Floor, 0.84 m step (59 Nm) | 2.8 to 7 | 1.4 to 3.5 |
| Transition (95 Nm) | 1.8 to 4.4 | 0.9 to 2.2 |

A watchdog limp-drop or a hard dock contact can exceed 2×. Cove fell this way on 2026-04-26 ([robot.md](../truth/robot.md)).

## Tightening and twist

- **Tighten M4 to 1.2 to 1.5 Nm.** The usual chart value of about 3 Nm gives about 3.7 kN of preload, about 80% of the thread's strength before the arm adds anything.
- **Screw length:** part thickness plus no more than 3.5 mm, as in the earlier note.
- **Twist:** at 27 Nm each bolt needs about 355 N of friction. Preload at 1.2 to 1.5 Nm gives about 300 to 375 N at a friction coefficient of 0.2. The joint will creep and loosen at peak twist. This is the thread digging from the [10-15 mount meeting](../meetings/2026-10-15-mount-design.md).

## The rear cap

In the manual's cover photo the bottom section with the connectors looks like a separate cap. The rear drawing shows four counterbored screws near the edge, which probably hold it to the body. If so, the whole arm load also goes through those screws, whatever is done to the mounting holes. Their size and the cap material are not in the manual. Not checked on a motor.

## Epoxy

| Where | Bending | Twist (27 Nm) | Verdict |
|---|---|---|---|
| Rear face only (ring ⌀57 outside, ⌀30 inside) | 3.5 MPa peel at 59 Nm, 5.7 MPa at 95 Nm | 0.8 MPa | Helps with the bolts clamping it: stops creep, seats the face fully. Not trusted alone. Still loads the rear cap. |
| Around the ⌀57 body, a cup or collar 15 mm deep | Taken by the cup wall as plain contact | 0.35 MPa | Bypasses the bolts and the cap. This is D-042. |

Peel is the loading epoxy handles worst. Lab lap-shear figures of 20 to 30 MPa do not apply to it.

Practical limits:

- Use a toughened structural epoxy. 5-minute epoxy softens near 50 to 60 °C, and the motor runs warm.
- Abrade the anodise and degrease.
- Keep epoxy out of the cap seam and the connectors. A cup needs cut-outs for the connectors.
- Allow 24 hours to cure.
- It is permanent. A spare motor has M2.5 holes and no cup.

## Open

1. Is the rear cap a separate piece, and what screws hold it to the body?
2. Which tap cut the M4 threads, and did any hole break through?
3. Does the mount sit flat on the whole rear face? Does any as-built part wrap the motor body?
4. Demo scope: floor and Watt Hall steps only (D-055), or any wall move? That sets 59 Nm against 95 Nm.
5. Mass of Ming's end effector. The URDF still has the old gripper (0.91 kg) and slip ring (0.49 kg) on each end.
6. Which way the gripper-spin motor faces. It moves the rear face by 56 mm and changes the result very little.
7. Housing alloy.
