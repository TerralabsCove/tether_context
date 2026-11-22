---
status: active
owner: John Peng, Steve Lu
last_reviewed: 2026-11-22
---

# Open Questions

When one is answered, move it to [decisions.md](decisions.md) as a new entry and delete it here. Each item names who should answer.

## Conflicts between sources

When two sources disagree, list it here and let a PM decide.

- **Master radio location.** D-026 and the [embedded bench note](../notes/2026-10-12-irisy-embedded-controls-bench.md) put the master ESP on the robot as node ID 0 with one motor, reached by the laptop over the master's SoftAP. The [2026-10-16 plan](../notes/2026-10-16-john-mvp-one-pager.md) and the [antenna plan](../notes/2026-10-19-john-esp32c5-antenna-rf-plan.md) put the master at the offboard computer, as tethersmall did. The antenna placement and near-far handling differ between the two. The [Notion page](../notes/2026-11-06-john-notion-digest.md) calls the wired master on the laptop the current plan, but no decision records it. Measured input: the laptop USB gateway ran 11/11 straight with RTT p95 20–26 ms, while the on-robot SoftAP master passed 3/5 with p95 159–642 ms. The arm layout also differed, so this isn't a controlled comparison ([run logs](../notes/2026-10-20-hansi-straightline-run-logs.md)). Owner: John, Hansi.
- **Camera compute vs D-013.** D-013 says no onboard compute. The 11-02 and 11-05 meetings have the camera run tag detection itself and send positions (D-037, D-038). Neither meeting mentions D-013, and the [11-01 note](../notes/2026-11-01-john-onboard-localization.md) says this needs its own decision. Owner: John, Steve.
- **Were the cameras ordered?** The 11-05 summary says ordered. The BOM on 11-06 has TTH-092 and TTH-093 as Draft, "not yet ordered". TTH-093 is quantity 1 and D-038 says two in total. Ming's existing unit may be the second, but no source says so. Owner: John, Ming.
- **Budget.** The BOM sheet says $1,500 ($1,290.44 committed). The Notion page says $2,000 and asks whether it is $2,500. Owner: John, Ming.
- **LiDAR on the BOM.** TTH-084 (2 × Unitree L1, $854) is still Draft, with a note saying it supersedes the no-LiDAR assumption. D-034 and the 11-02 transcript drop LiDAR. Owner: John.
- **IYA water-jet session day.** The 11-05 summary says Saturday from 2 PM. In the transcript it is "tomorrow", said on Thursday night. Owner: John.

## Localization

1. **Mocap access.** Closed. No motion capture (D-054).
2. **Mocap role.** Closed. No motion capture (D-054).
3. **Dim lighting.** Pure vision fails in dim light. Does that also rule out mocap or the AprilTag backup in the target environment? Owner: Jason.
   Input (11-02, 11-05): LEDs at the end effector, on a separate mount (D-039). Not yet tested in dim light.

## Follow-ups from the 3-module change (D-020)

4. **End-effector radio and mounting.** The end effector is powered on its own and has its own radio (D-048), with no slip ring (D-047). The radio is a XIAO ESP32-C5 (John, 2026-11-20). How the laptop addresses it and where the parts mount are not stated. Owner: mech.
   Input (10-18, 11-01, 11-05): the earlier plan ran 5 V, GND and two servo signals through a slip ring (D-044, superseded). Extra ESPs were raised then as the fallback.
5. **Battery layout for 3 modules.** D-004 planned 3 battery sizes and 5–6 batteries across 5 modules. That needs redoing. Owner: mech, electrical.
   Input: the middle module has two (D-036), while the [10-18 meeting](../meetings/2026-10-18-docking-power.md) counted 3 batteries in total with 1 in the center. The Notion page says the second pack's whereabouts are unclear.
6. **End-effector power spec.** Answered except for the BOM: a 3S 450 mAh battery and an LM2596 buck to 5 V for the camera, C5 and servos, with runtime long enough for our use (John, 2026-11-20). The BOM lists neither the pack nor an active LM2596 (TTH-018 is Cancelled). Add rows if they were bought for Tether. Owner: Ming.
   Input (11-05): servos were planned on the module's 24 V to 5 V buck, which D-048 replaces. The 11-01 plan powered the end camera through the slip ring; where the camera gets power now is not stated.

## Hardware

7. **Camera compute and data path.** D-037 settled no video and no stereo. Still open: is the reCamera fast enough for AprilTags, and how does tag data reach the laptop? Plan (D-049): USB-C from the camera to the end-effector C5 first, and the camera's debug UART if USB fails. The C5 forwards over ESP-NOW. Neither is tested end to end. The camera's own Wi-Fi was also raised (about 100 ms was mentioned on 11-05, with no test data). If compute falls short, the team looks at streaming. Pis on the arm with switched control authority were raised and not chosen. First test: 3–8 detections per second, [11-06 note](../notes/2026-11-06-john-claw-camera-followups.md). Owner: John, Steve, Ming.
   Input (11-21, [note](../notes/2026-11-21-hansi-camera-c5-tags-on-master.md)): the USB route works on the bench. Camera 2, acting as USB host to its C5, sent tags over ESP-NOW to the master C5 on the laptop at 24–29 per second **[verified]**. Not yet tested on camera 1, on end-effector power, or alongside the module radios. It ran on 2.4 GHz channel 1, and the arm link was measured on 5 GHz channel 36.
8. **Wire routing inside a module.** Per-module batteries remove cables between modules. Joints within a module, especially the continuous middle joint (D-003), may still need a slip ring. Owner: mech.
   Input: the slip ring was scoped to the end effector (D-044) and is now dropped (D-047). A cable chain at the end effector (±180°) was raised on 10-26 and not decided. The wire housing from the 11-01 motor flip item may no longer be needed (D-032).
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
19. **End effector go or no-go.** Closed. Both ends use Ming's end effector (D-052). Whether it holds is question 26.
20. **Buck converter and servo power.** Size the 24 V to 5 V buck for the ESP, camera and servos (stall quoted as 3.2 A at 4.8 V, and 2.8 A was also said on 11-05). Potentiometer-style converters could twist on the arm. Separately, Ming bought 4 FEETECH STS3215 12 V servos on 11-04 (TTH-090), and no source says what they are for. After D-048, whether the servos still load this buck is not stated. Owner: Electrical, Ming.
    Input (11-18): budget each end camera at 5 W, about 1 A at 5 V. John says the reCamera documentation gives about 5 W in theory. Whether that is typical or maximum is not confirmed, and the draw is not measured. **[assumed]** Planned check once the end effector is wired: the voltage at the camera, through the buck and the slip ring, while the tag loop runs (it keeps the CPU fully busy). Owner: Hansi.
21. **Hardware-to-software schedule.** Set on 11-21 (D-050): days are in the [final push plan](../plans/final-push-schedule.md). Electrical moves to software once the full arm is assembled, planned for 11/25. Nothing is planned yet for 11/30 to 12/3. Owner: John.
22. **Seeing objects without tags.** Stereo would help manipulation, and it is out (D-037). Low-contrast objects like the glowing orbs may be hard to detect. Dropping them or testing in sim were both raised. Owner: John, Steve.
23. **Final demo and obstacles.** The direction is a leading idea only. Lively motion has no software owner, and a mid-demo battery swap is unsettled. Owner: John, Steve.
24. **E-stop.** Likely wireless and freezing all motors rather than cutting power (11-01). It's only an idea so far, with no owner. Owner: electrical.
25. **Does D-008's battery protection hold?** From the [soft-start note](../notes/2026-10-30-john-soft-start-modules.md): the DM-J4340P supply floor is 15 V, or 2.5 V per cell on 6S, which over-discharges a LiPo. Motors only protect the pack if `UV_Value` is raised to about 19.8–21 V and saved on every motor, and the default isn't read yet. A pack left plugged in also keeps draining. The AS60 soft-start (TTH-075) has no switch input, so an on/off switch is still open. Owner: electrical.
26. **End effector backup if the lock fails.** The lock is turned by hand on 11/22 and tested under power on 11/24. If it fails, about 10 days are left. An electromagnet backup was raised on 11-21 and not chosen: extra ESPs and relays, battery power for the magnets, sim and software changes, and no budget. To be decided with Jack and Ming on 11/22. Owner: John, Ming, Jack.
27. **Watt Hall B1 access over Thanksgiving.** It is the demo and practice site (D-051). Not known if the building is open over the break. The plan is to ask a Roski student. Without it, the team practices at Ming's, where the front steps are too shallow to stand in for the real ones. Owner: John, Steve.
28. **Shell clearance at the center joint.** The back electronics make one side of the arm thicker than planned, and the center spacer can't get thicker. The 11-21 meeting settled on an asymmetric shell, with software swinging the full 360° only on the flat side. That limit is not in the sim or the URDF yet. Owner: Steve, JC.
29. **Shell time.** JC's availability over Thanksgiving is not confirmed. Design is due 11/26 and manufacturing 11/28, with about 2 days of printing. Owner: John, JC.
30. **Who is on which software track.** Steve has the policy track. The deterministic track is "others", with no names. About 2 people per track was the idea. Owner: John, Steve.

# Risks to Watch

Not questions to answer, but things that could bite us later. Revisit at each gate.

| Risk | Why it matters | Watch for | Owner |
|---|---|---|---|
| **3 tracked points may not give full joint state** | The 10-08 meeting assumed two endpoints plus the middle joint are enough. That only holds if each is tracked as a full 6-DoF rigid body (position and orientation) on the right link. Three single 3D points can't pin down 7 joints. | Mocap marker design. Make sure each tracked body has enough markers for orientation. | Steve, Jason |
| **Encoder drift** | Encoders are the last-resort localization fallback (D-018), and they drifted last time. | Any plan that leans on encoders alone for world position. | Unassigned (was Trent) |
| **0x05 CAN wiring** | 0x05 has gone silent from its wiring twice, and it moved about 100° unexplained between scans on 10-30 ([note](../notes/2026-10-30-hansi-0x05-hold-wiring.md)). Not tested with the arm moving. | 0x05's hold line on the first hardware run. | Electrical |
| **End effector lock untested** | The whole final push plan assumes Ming's end effector (D-052) locks into a port and holds the arm the first time. Nothing has been tested, and one end carries the whole arm (question 16). | The hand test on 11/22 and the powered lock and swing test on 11/24. | Ming, John |
| **URDF still unaudited** | We now trust the URDF for joint axes (D-021), but nothing has been measured against hardware yet. | G0 audit results. | John |
