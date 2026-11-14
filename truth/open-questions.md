---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-13
---

# Open Questions

When one is answered, move it to [decisions.md](decisions.md) as a new entry and delete it here. Each item names who should answer.

## Conflicts between sources

When two sources disagree, list it here and let a PM decide.

- **Climbing scope.** [PR #8](https://github.com/TerralabsCove/tether_context/pull/8) (Hansi, 11-04) proposes D-030: walk across a floor along a path of docks, with climbing out of scope (no tree, ladder, wall or ceiling). It asks John and Steve to confirm, and neither has on the record. Against it: the [10-19 meeting](../meetings/2026-10-19-showcase-mvp.md) kept sideways as a possibility (D-045), the [11-01 all-hands](../meetings/2026-11-01-all-hands.md) moved from the tree to a hill, and the [11-02 transcript](../meetings/2026-11-02-leads-status.md) plans a small hill with docks at height that the robot climbs. The 11-05 meeting floated vertical mounts only for this semester. Hill climbing is the part PR #8 would rule out that the meetings still plan. Owner: John, Steve.
- **RL vs D-014.** D-014 (10-08 meeting) says locomotion uses motion planning, with no RL at this stage. On 2026-10-11 an RL policy drove the tethersmall testbed over ESP-NOW ([note](../notes/2026-10-11-john-tethersmall-rl-over-espnow.md)). Is tethersmall only a link and firmware testbed that leaves D-014 standing, or does it reopen RL for Tether? Owner: John, Steve.
- **Master radio location.** D-026 and the [embedded bench note](../notes/2026-10-12-irisy-embedded-controls-bench.md) put the master ESP on the robot as node ID 0 with one motor, reached by the laptop over the master's SoftAP. The [2026-10-16 plan](../notes/2026-10-16-john-mvp-one-pager.md) and the [antenna plan](../notes/2026-10-19-john-esp32c5-antenna-rf-plan.md) put the master at the offboard computer, as tethersmall did. The antenna placement and near-far handling differ between the two. The [Notion page](../notes/2026-11-06-john-notion-digest.md) calls the wired master on the laptop the current plan, but no decision records it. Measured input: the laptop USB gateway ran 11/11 straight with RTT p95 20–26 ms, while the on-robot SoftAP master passed 3/5 with p95 159–642 ms. The arm layout also differed, so this isn't a controlled comparison ([run logs](../notes/2026-10-20-hansi-straightline-run-logs.md)). Owner: John, Hansi.
- **Camera compute vs D-013.** D-013 says no onboard compute. The 11-02 and 11-05 meetings have the camera run tag detection itself and send positions (D-037, D-038). Neither meeting mentions D-013, and the [11-01 note](../notes/2026-11-01-john-onboard-localization.md) says this needs its own decision. Owner: John, Steve.
- **AprilTags vs D-012.** D-012 makes mocap primary and AprilTags a backup. The 11-02 meeting and John's 11-05 #tether post use AprilTags on docks plus joint states, with no external localization sensor. This also bears on questions 1 and 2. Owner: John, Steve.
- **Were the cameras ordered?** The 11-05 summary says ordered. The BOM on 11-06 has TTH-092 and TTH-093 as Draft, "not yet ordered". TTH-093 is quantity 1 and D-038 says two in total. Ming's existing unit may be the second, but no source says so. Owner: John, Ming.
- **Budget.** The BOM sheet says $1,500 ($1,290.44 committed). The Notion page says $2,000 and asks whether it is $2,500. Owner: John, Ming.
- **LiDAR on the BOM.** TTH-084 (2 × Unitree L1, $854) is still Draft, with a note saying it supersedes the no-LiDAR assumption. D-034 and the 11-02 transcript drop LiDAR. Owner: John.
- **Demo day date.** The task sheet format says Dec 3. The [10-19 meeting](../meetings/2026-10-19-showcase-mvp.md) says the Fall Showcase is Dec 4, 5–7 PM, Trojan Ballrooms. An 11-05 announcement says 25 days out, which is Nov 30. Owner: John, Steve.
- **IYA water-jet session day.** The 11-05 summary says Saturday from 2 PM. In the transcript it is "tomorrow", said on Thursday night. Owner: John.

## Localization

1. **Do we have access to a mocap system at all?** In progress. IYA/Avalon answer expected Monday. WISP team not yet asked. See D-018 and [the mocap plan](../plans/mocap-integration.md). Owner: John (via Ming), Jason.
   Input (10-19): a Mocap (OptiTrack) timeline of 3–4 weeks came up in the leads meeting, with markers research tied to Wisp and IYA's setup. No source says Tether has access.
2. **Is mocap lab-only, or part of how the robot runs?** Being decided now, and it depends on question 1. The mocap plan treats mocap as lab-only ground truth the robot must never depend on. The 10-08 meeting picked mocap as primary localization, with cameras placed around the environment. These lead to very different software. Owner: Steve, Jason.
3. **Dim lighting.** Pure vision fails in dim light. Does that also rule out mocap or the AprilTag backup in the target environment? Owner: Jason.
   Input (11-02, 11-05): LEDs at the end effector, on a separate mount (D-039). Not yet tested in dim light.

## Follow-ups from the 3-module change (D-020)

4. **Where do the claws live now?** D-005 put each claw's motor in its own claw module and said each end always needs one. With end-effector modules gone, which module powers and controls each claw servo? Owner: mech.
   Input (10-18, 11-01, 11-05): the slip ring is at the end effector (D-044), and the plan runs 5 V, GND and two servo signals through it. Servo signals over the slip ring are untested. The fallback raised is extra ESPs.
5. **Battery layout for 3 modules.** D-004 planned 3 battery sizes and 5–6 batteries across 5 modules. That needs redoing. Owner: mech, electrical.
   Input: the middle module has two (D-036), while the [10-18 meeting](../meetings/2026-10-18-docking-power.md) counted 3 batteries in total with 1 in the center. The Notion page says the second pack's whereabouts are unclear.
6. **End-effector battery spec.** May no longer be a separate battery after D-020. Owner: mech.
   Input (11-05): servos are planned on a 24 V to 5 V buck, which would remove it. Not stated as a decision.

## Hardware

7. **Camera compute and data path.** D-037 settled no video and no stereo. Still open: is the reCamera fast enough for AprilTags, and how does tag data reach the laptop? Options are UART through the module's C5 over ESP-NOW, or the camera's own Wi-Fi (about 100 ms was mentioned on 11-05, with no test data). If compute falls short, the team looks at streaming. Pis on the arm with switched control authority were raised and not chosen. First test: 3–8 detections per second, [11-06 note](../notes/2026-11-06-john-claw-camera-followups.md). Owner: John, Steve, Ming.
8. **Wire routing inside a module.** Per-module batteries remove cables between modules. Joints within a module, especially the continuous middle joint (D-003), may still need a slip ring. Owner: mech.
   Input: the slip ring is scoped to the end effector (D-044). It is on site and needs measuring. A cable chain at the end effector (±180°) was raised on 10-26 and not decided. The wire housing from the 11-01 motor flip item may no longer be needed (D-032).
9. **Docking alignment hole.** The AprilTag backup needs a centered hole in the end effector. Needs a meeting with the mechanical designers. Owner: John.
   Input (10-18, 11-05): docks are now pins on the arm into passive holes (D-043). The tag can go on the side of the dock (D-039), so a centered camera hole may not be needed. The camera's minimum focus distance vs the dock geometry was raised and not settled. Measure it.
10. **Does the docking geometry lock orientation?** A triangle or pinned shape could remove a rotation motor. The 10-18 meeting has a 3-pin layout with 120° of servo rotation, and the 10-26 meeting has 4 pegs 90° apart. Confirm which was built. Owner: mech.
    Input from the [step-reach sim](../notes/2026-10-28-john-step-reach-sim.md): on inclines and walls the anchored gripper is twisted about its own axis, and only the gripper-spin motor (27 Nm peak) resists it. The gripper-to-dock lock should hold more twist than that.
11. **Motor feedback identities and limits.** The slave IDs and remote slot roles are assigned in D-028. Scan the six remote motors and record each feedback ID, model, PMAX, VMAX, and TMAX. Confirm the master `0x04` motor still replies on feedback ID `0x14`. IDs must be distinct within a module's local CAN bus; do not derive feedback IDs by assumption. Owner: embedded, electrical.
    Input ([10-30 wiring note](../notes/2026-10-30-hansi-0x05-hold-wiring.md)): five motors found on the testbed: 0x02 (TMAX 200) and 0x05 (DM4340, TMAX 28) on board 11, 0x04 on board 12, 0x06 and 0x03 (TMAX 28, reply 0x013) on board 13. These IDs match D-028. 0x01 and 0x07 aren't in that test.

## Software

12. **Sim update.** The sim still models Cove's geometry. When does it pick up the offset layout and the 3-module design? Owner: Steve.
    Input (2026-10-31): the new Tether arm URDF (`terra_arm_description`, masses corrected) exists in cove-controls and the step-reach sim already uses it. See [robot.md](robot.md#simulation-model).
13. **Packet loss and redundancy.** The comms layer must make the 3 wireless modules act as one arm in ROS. What's the design? Owner: Electrical (was Trent, D-035).
    Input from tethersmall (2026-10-11): ESP-NOW broadcast with each command sent twice, newest-sequence-wins on the module, 200 Hz state streaming, and watchdog/slew limits on the ESP. It delivered 91–94 % of commands, and the losses come in bursts. See [robot.md](robot.md#tethersmall-testbed-2026-10-11).
14. **Is ESP-NOW's margin enough for Tether?** D-019 says to fall back to NRF ESB only if ESP-NOW falls short. On tethersmall it works but sits at the edge: RTT p95 ~70 ms, outages up to ~200 ms. Master placement and an external antenna are untested. Owner: Electrical (was Trent, D-035), John.
    With the C5 (D-029): 5 GHz channel 149–165 (or 36–48) vs 2.4 GHz channel 11, ESP-NOW rate on 5 GHz, antenna type, and mounting next to the aluminum links are all unmeasured. The [antenna and RF plan](../notes/2026-10-19-john-esp32c5-antenna-rf-plan.md) has the test matrix. Note the firmware currently defaults to channel 1, which tethersmall measured as lossy.
    Input ([C5 range test](../notes/2026-10-28-hansi-c5-range-test.md), 10-28): 5 GHz channel 36 through a USB gateway. RTT p50 12–13 ms and p95 19–22 ms from the bench to 5–6 m through a wall, and max 39 ms. Range shows up as signal and lost frames rather than delay: 0x04 reached −82 dBm and lost 5–10 % of status reports through the wall. Motors were damped, with no motion or policy. The note recommends staying within about 3 m with line of sight. 0x04 is the weakest radio in every test, for an unknown reason.
15. **Three or more ESP-NOW nodes on one channel.** tethersmall had two slaves. Tether needs three modules (D-020) plus the offboard side, and node count affects collisions and loss. Owner: Electrical (was Trent, D-035).

## Locomotion and end effector

From the [step-reach sim](../notes/2026-10-28-john-step-reach-sim.md). Loads are from the 2026-10-31 re-run with the 14.35 kg arm. **[assumed]**

16. **What can the gripper and dock hold?** While the other end swings, one gripper carries the whole arm (141 N). It also sees up to about 95 Nm of bending in floor-to-wall and over-the-edge moves, 141 N of pull-out on a ceiling, and twist up to the 27 Nm gripper-spin peak. Even on a flat floor, the gripper must clamp: about 57 Nm of bending at a 0.80 m step, far more than its weight alone resists. How far must the gripper lift straight out to clear the dock? The sim assumes 12 cm. Needs a bench test of a gripper in a dock. Owner: mech.
17. **Gripper spin axis on walls.** On a wall, sideways steps are limited by the gripper-spin motor's 27 Nm peak: at most 0.38 m (0.14 m within rated torque). Climbing straight up is not limited. Options: a brake on the spin axis, a stronger motor, or no sideways moves on walls. Owner: mech, John.
18. **Can Tether mount sideways at all?** On 11-05 people questioned deflection at the arm end with a sideways mount, and whether Jack's analysis counts the screws and non-rotational load. Limiting this semester to vertical mounts was floated and not decided. Owner: Jack, John, Ming.
19. **End effector go or no-go.** The machining quote was due 11-06. The deadline it is measured against wasn't stated. The summary says 13 parts to mill, while the transcript also counts 7 × 2 + 6. Printing vertical-load parts and milling horizontal-load parts was discussed and not decided. Owner: Isaac, Ming, John.
20. **Buck converter and servo power.** Size the 24 V to 5 V buck for the ESP, camera and servos (stall quoted as 3.2 A at 4.8 V, and 2.8 A was also said on 11-05). Potentiometer-style converters could twist on the arm. Separately, Ming bought 4 FEETECH STS3215 12 V servos on 11-04 (TTH-090), and no source says what they are for. Owner: Electrical, Ming.
21. **Hardware-to-software schedule.** Set a day for each electrical sub-task and a day the team switches to software. A focused Friday or Saturday work session was discussed. Owner: John.
22. **Seeing objects without tags.** Stereo would help manipulation, and it is out (D-037). Low-contrast objects like the glowing orbs may be hard to detect. Dropping them or testing in sim were both raised. Owner: John, Steve.
23. **Final demo and obstacles.** The direction is a leading idea only. Lively motion has no software owner, and a mid-demo battery swap is unsettled. Owner: John, Steve.
24. **E-stop.** Likely wireless and freezing all motors rather than cutting power (11-01). It's only an idea so far, with no owner. Owner: electrical.
25. **Does D-008's battery protection hold?** From the [soft-start note](../notes/2026-10-30-john-soft-start-modules.md): the DM-J4340P supply floor is 15 V, or 2.5 V per cell on 6S, which over-discharges a LiPo. Motors only protect the pack if `UV_Value` is raised to about 19.8–21 V and saved on every motor, and the default isn't read yet. A pack left plugged in also keeps draining. The AS60 soft-start (TTH-075) has no switch input, so an on/off switch is still open. Owner: electrical.

# Risks to Watch

Not questions to answer, but things that could bite us later. Revisit at each gate.

| Risk | Why it matters | Watch for | Owner |
|---|---|---|---|
| **3 tracked points may not give full joint state** | The 10-08 meeting assumed two endpoints plus the middle joint are enough. That only holds if each is tracked as a full 6-DoF rigid body (position and orientation) on the right link. Three single 3D points can't pin down 7 joints. | Mocap marker design. Make sure each tracked body has enough markers for orientation. | Steve, Jason |
| **Encoder drift** | Encoders are the last-resort localization fallback (D-018), and they drifted last time. | Any plan that leans on encoders alone for world position. | Unassigned (was Trent) |
| **0x05 CAN wiring** | 0x05 has gone silent from its wiring twice, and it moved about 100° unexplained between scans on 10-30 ([note](../notes/2026-10-30-hansi-0x05-hold-wiring.md)). Not tested with the arm moving. | 0x05's hold line on the first hardware run. | Electrical |
| **URDF still unaudited** | We now trust the URDF for joint axes (D-021), but nothing has been measured against hardware yet. | G0 audit results. | John |
