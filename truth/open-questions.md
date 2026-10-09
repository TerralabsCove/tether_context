---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-10-08
---

# Open Questions

When one is answered, move it to [decisions.md](decisions.md) as a new entry and delete it here. Each item names who should answer.

## Conflicts between sources

None right now. When two sources disagree, list it here and let a PM decide.

## Localization

1. **Do we have access to a mocap system at all?** In progress. IYA/Avalon answer expected Monday. WISP team not yet asked. See D-018 and [the mocap plan](../plans/mocap-integration.md). Owner: John (via Ming), Trent, Jason.
2. **Is mocap lab-only, or part of how the robot runs?** Being decided now, and it depends on question 1. The mocap plan treats mocap as lab-only ground truth the robot must never depend on. The 10-08 meeting picked mocap as primary localization, with cameras placed around the environment. These lead to very different software. Owner: Steve, Jason.
3. **Dim lighting.** Pure vision fails in dim light. Does that also rule out mocap or the AprilTag backup in the target environment? Owner: Jason.

## Follow-ups from the 3-module change (D-020)

4. **Where do the claws live now?** D-005 put each claw's motor in its own claw module and said each end always needs one. With end-effector modules gone, which module powers and controls each claw servo? Owner: mech.
5. **Battery layout for 3 modules.** D-004 planned 3 battery sizes and 5–6 batteries across 5 modules. That needs redoing. Owner: mech, electrical.
6. **End-effector battery spec.** May no longer be a separate battery after D-020. Owner: mech.

## Hardware

7. **Video streaming.** ESP bandwidth is too low. Options: dedicated wireless video module (DJI-style) or Raspberry Pi. Jetson ruled out as too heavy. FireEye camera preferred over ToF. Owner: Jason, Trent.
8. **Wire routing inside a module.** Per-module batteries remove cables between modules. Joints within a module, especially the continuous middle joint (D-003), may still need a slip ring. Owner: mech.
9. **Docking alignment hole.** The AprilTag backup needs a centered hole in the end effector. Needs a meeting with the mechanical designers. Owner: John.
10. **Does the docking geometry lock orientation?** A triangle or pinned shape could remove a rotation motor. Owner: mech.

## Software

11. **Sim update.** The sim still models Cove's geometry. When does it pick up the offset layout and the 3-module design? Owner: Steve.
12. **Packet loss and redundancy.** The comms layer must make the 3 wireless modules act as one arm in ROS. What's the design? Owner: Trent, Jason.

# Risks to Watch

Not questions to answer, but things that could bite us later. Revisit at each gate.

| Risk | Why it matters | Watch for | Owner |
|---|---|---|---|
| **3 tracked points may not give full joint state** | The 10-08 meeting assumed two endpoints plus the middle joint are enough. That only holds if each is tracked as a full 6-DoF rigid body (position and orientation) on the right link. Three single 3D points can't pin down 7 joints. | Mocap marker design. Make sure each tracked body has enough markers for orientation. | Steve, Jason |
| **Encoder drift** | Encoders are the last-resort localization fallback (D-018), and they drifted last time. | Any plan that leans on encoders alone for world position. | Trent |
| **URDF still unaudited** | We now trust the URDF for joint axes (D-021), but nothing has been measured against hardware yet. | G0 audit results. | John |
