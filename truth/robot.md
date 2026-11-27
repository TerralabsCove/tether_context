---
status: active
owner: John Peng (hardware)
last_reviewed: 2026-11-26
---

# Robot: Cove and Tether

Every fact here carries a tag. **[verified]** means measured on hardware with a recorded artifact. **[as built]** means true of the physical Cove but not measured against the model. **[decided]** means a design decision with a log entry. **[assumed]** means used in sim or planning but not checked.

Nothing about Cove or Tether is **[verified]** yet. Gate G0 is what changes that. The first measured artifacts are from the tethersmall testbed below.

## Cove (spring 2026, the starting point)

| Item | Value | Tag |
|---|---|---|
| Joints | 7 | as built |
| Joint axes | Z-Y-Z-Y-Z-Y-Z, per the URDF. The kickoff deck's Z-X-Z notation is superseded. | decided D-021 (still to be confirmed by the G0 audit) |
| Actuators | 7 Damiao actuators with built-in encoders and torque sensing, daisy-chained on one CAN bus | as built |
| Torque budget | ≈50 Nm working | as built |
| Payload | ≈7 kg at full reach | as built |
| Structure | 8 aluminum parts milled from 3 pieces of stock ($308), every part 3D-printed first for fitment | as built |
| Power | 24 V trunk (XT-60/XT-30) from a bench supply, hardware e-stop on motor power | as built |
| Compute | Raspberry Pi host, CAN/UART bridge, ROS 2 + MoveIt2, AprilTags for target pose | as built |
| End effector | Electromagnet, one end only | as built |
| Known failure | 2026-04-26: bottom threads stripped under load and the arm fell. 4 actuators broken, fuses blown, CAN ports fried. Rebuilt. | as built |

## Tether (fall 2026, the target)

| Area | Design | Tag |
|---|---|---|
| Base | None. Either end anchors. | decided D-001 |
| Joint layout | "Straighter but offset", not full diagonal | decided D-002 |
| Middle joint | Continuous 360° | decided D-003 |
| Modules | 3 wireless modules, one ESP brain each. The end effector is powered on its own and has its own radio (D-048). | decided D-020, D-048 |
| Drive motors | Seven total. Master ID 0 controls one. Left ID 1 and right ID 2 control three each. Every module uses a private local CAN bus. | decided D-026 |
| Motor models | 3 × DM-J10010-2EC on the pitch joints (40 Nm rated, 150 Nm peak, 1.485 kg; the plain 10010, although the URDF link names say J10010L). 4 × DM-J4340P-2EC on the rolls and gripper spins (9 Nm rated, 27 Nm peak, 0.375 kg). Figures from the user manuals. Run at 24 V: rated torque holds; the 10010, rated at 48 V, runs at about half speed. | as built |
| Arm mass | 14.35 kg (31.6 lb) in the corrected URDF. Batteries (3200 mAh 218 g, 5000 mAh 1.52 lb), slip rings (10.5 oz) and gripper servos (3.52 oz) were weighed, with no recorded artifact. Motors are from the manuals. Aluminium structure and gripper housing are from CAD. Wiring, ESP boards, DC-DC converters and fasteners are not included. The slip rings are now dropped (D-047) and the figure has not been redone. | as built (weighed parts), assumed (rest) |
| Top motor orientation | Kept as built, not flipped | decided D-032 |
| Motor identities | Master slot 0: slave `0x04`, previously measured feedback `0x14`. Remote slots are big / near-master / far-end. Node 1 slave IDs: `0x02` / `0x05` / `0x01`. Node 2: `0x06` / `0x03` / `0x07`. Remote feedback IDs and limits are not yet scanned. | decided D-028; feedback IDs open |
| Inter-module wiring | None. Fully wireless. | decided D-006 |
| Inter-module link | ESP-NOW first, NRF ESB as fallback (BLE ruled out) | decided D-019 |
| Radio board | Seeed XIAO ESP32-C5 on every module and on the master. U.FL external antenna only; no on-board antenna. Band, channel, antenna type, and mounting are open and go through the test matrix in the [antenna and RF plan](../notes/2026-10-19-john-esp32c5-antenna-rf-plan.md). | decided D-029; band and antenna open |
| Batteries | Layout planned for 5 modules, needs rework for 3 (see open questions). 3 sizes, 5–6 total, 5,000 mAh main modules, ~2 h runtime target, ~$50 per small battery. Middle module has two (D-036). | decided D-004, D-036 |
| Battery protection | No BMS. Motors have built-in min-voltage shutoff. DC-DC converter for ESPs. | decided D-008 |
| Module power | Battery splits to the motors and a 24 V to 5 V buck. ESP and CAN transceiver on the big motor side, enclosed. | decided D-033 |
| Module IMU | One GY-BNO08X on each module, on the module's ESP over I2C: SDA D4, SCL D5, INT D0, RST D1. Added 2026-11-26 to measure dock play and arm sway; no decision number. Chip variant not confirmed. Each was calibrated off the arm, and each reads gravity about 1 % off once mounted. See the [on-arm note](../notes/2026-11-26-john-imu-on-arm-bringup.md). | as built |
| Arm firmware | Since 2026-11-26 boards 10 to 13 run tethersmall `john/module-imu` at `45c56ff`: `steve/cmd-feedforward` (`b3a0331`) plus an IMU task. Merged to tethersmall `main` on 2026-11-27 (`5aad32a`); the `COMMAND_FF` limits in it are still proposals. Run with the arm at rest only, no commands sent. tether_ros `main` decodes the IMU frames (checked on a recorded capture, not live). See the [on-arm note](../notes/2026-11-26-john-imu-on-arm-bringup.md) and the [merge note](../notes/2026-11-27-steve-imu-merged-laptop-reader.md). | as built |
| Mounts | Loads go through interlocking geometry, not bolts | decided D-042 |
| Slip ring | None (D-047). The earlier plan (D-044) put a Taidacent hollow 6-wire slip ring (TTH-058) at the end effector. That part is on site. | decided D-047 |
| End effectors | Ming's end effector on both ends (D-052). CAD: [end effector](../assets/2026-11-21-MingEE-male-v3.step), [dock](../assets/2026-11-21-MingEE-female-v3.step). Docking is servo-driven pins on the arm into passive holes on the structure (D-043). No metal end effector is assembled or tested yet as of 11-21. The earlier servo claw (D-005) is replaced. | decided D-052, D-043 |
| End-effector servos | 4 × ANNIMOS 35 kg 270° (TTH-054), received. Stall current quoted as 3.2 A at 4.8 V, not measured. | as built (part), assumed (current) |
| End camera | One per end, no stereo. reCamera 2002W, about 1 GHz, Linux. Both units now have the GC2053 sensor board with its stock 2.9 mm lens (M12 mount), replacing the stock 65° OV5647 board. No fisheye (D-046). The GC2053 board has no fill LEDs. Camera 2 measured 84.6° H × 53.9° V at 1080p, fx 1065 px, almost no distortion. Camera 1 is not calibrated. The stream runs at 9 fps whatever it is set to (Seeed's stock pipeline). On-camera tag detection runs about 5–6 Hz at 640 × 480, the only size the camera decodes. Mounted on the far end, pointing straight. Separate LED mount. Tests: [11-06](../notes/2026-11-06-john-claw-camera-followups.md), [11-13](../notes/2026-11-13-john-recamera-gc2053-bringup.md), [11-13 calibration](../notes/2026-11-13-john-recamera-lens-calibration.md). | decided D-037, D-038, D-039, D-046; as built (GC2053 + stock lens); verified (rates, 11-13 logs; camera 2 FOV and calibration, 11-13); camera 1 FOV open |
| Video link | No video stream. Only tag position data is sent. Analog FPV ruled out. How that data reaches the laptop is open (question 7). | decided D-034, D-037 |
| Compute | Fully offboard. The 11-05 camera plan runs detection on the camera, see [conflicts](open-questions.md#conflicts-between-sources). | decided D-013; in conflict |
| Localization | AprilTags on the docks, read by the end cameras, plus joint states. No motion capture (D-054). LiDAR is out (D-034). | decided D-054 |
| Control approach | Two tracks: a deterministic AprilTag path and a trained policy (D-050, D-053). | decided D-050, D-053 |
| Electronics build | Breadboard, no PCB yet | decided D-007 |
| End-effector power | Powered on its own, with its own radio (D-048). Each end effector has its own 3S 450 mAh battery, stepped down to 5 V by an LM2596 buck converter. The radio is a Seeed XIAO ESP32-C5. Runtime is long enough for our use. (John, 2026-11-20.) Neither the 450 mAh pack nor an active LM2596 row is on the BOM: TTH-018 (LM2596 5-pack) is marked Cancelled. | decided D-048; as stated (battery, buck, C5, runtime) |

## tethersmall testbed (2026-10-11)

Two Cove pitch modules (DM10010) and their brackets, with no other joints, driven by an RL policy on a Mac over ESP-NOW. It is the Tether wireless architecture in miniature. Details live with the code: [docs/ESPNOW_BRINGUP.md](https://github.com/TerralabsCove/tethersmall/blob/main/docs/ESPNOW_BRINGUP.md). Artifacts: [deploy/hardware_logs/](https://github.com/TerralabsCove/tethersmall/tree/main/deploy/hardware_logs).

| Item | Value | Tag |
|---|---|---|
| Link | Mac → USB → master XIAO ESP32-C3 → ESP-NOW broadcast (channel 11, 1 Mbit/s) → slave XIAO ESP32-C3 / ESP32-C6 → CAN 1 Mbit/s → Damiao (MIT mode) | as built |
| Safety on each slave | 2.5 rad/s target slew, 200 ms watchdog (goes limp), overspeed cut at 3.5 rad/s, 12 Nm torque cap | as built |
| Command delivery, each command sent twice | 91–94 % on a bench; losses are bursty | verified (hardware_logs, bench tests) |
| Command→state round trip | p50 13 ms, p95 ~70 ms, max ~210 ms | verified (run-20261011-013601) |
| Channel choice | Channel 1 lost 10–34 % of one slave's packets to nearby Wi-Fi; channel 11 lost 0 % | verified (bench measurement, 2026-10-11; numbers in ESPNOW_BRINGUP.md) |
| Damiao position wrap | A motor's position reading can jump by 2π. One motor's straight pose sat next to its wrap; firmware now tracks turns | verified (observed on motor A) |
| Policy on hardware | 20 s with no faults; B−A phase +89.9° (sim +86°), amplitudes 0.45 / 0.59 rad (sim 0.49 / 0.57) | verified (run-20261011-013601) |
| Forward progress | ~0.20 m in 20 s, limited by cable drag. Not a policy result. | as built (observed, not instrumented) |
| Straight-line arm, 3 motors (2026-10-19/20) | USB gateway: 11/11 straight, RTT p95 20–26 ms. On-robot SoftAP master: 3/5 passed, RTT p95 159–642 ms. Layouts differed. | verified ([run logs](../notes/2026-10-20-hansi-straightline-run-logs.md)) |
| All-C5 arm link (2026-10-28) | 5 GHz channel 36, USB gateway, damped motors: RTT p50 12–13 ms, p95 19–22 ms, bench to 5–6 m through a wall | verified ([range test](../notes/2026-10-28-hansi-c5-range-test.md)) |
| Arm at rest with IMUs (2026-11-26) | 5 GHz channel 36, USB gateway, listening only, 58 s. 7 motors: 197–199 Hz each, status OK, 0.3–1.3 % of reports lost. 3 IMUs: 94–100 Hz, 0.6–5.7 % of frames lost. No run without the IMU frames to compare with. | verified ([on-arm note](../notes/2026-11-26-john-imu-on-arm-bringup.md)) |

## Simulation model

- **Model source:** `vendor/cove-controls/src/full_assembly/urdf/simple_assembly.urdf`, cloned from [TerralabsCove/cove-controls](https://github.com/TerralabsCove/cove-controls). **[assumed]** It is Cove's exported URDF and has not been audited against the hardware.
- **Collision geometry:** visual meshes used as provisional collision shapes. **[assumed]**
- **B-end contact point:** 49.5 mm along +Z from `wrist_link`, taken from the mesh envelope. **[assumed]**
- **Not modeled:** contact stability, friction and grip force, torque and current, cable fatigue, payload dynamics.
- **Note:** the sim models Cove's geometry. It does not yet reflect the offset layout (D-002) or the 3-module wireless design (D-020).
- **Tether arm model:** `description/terra_arm_description/urdf/arm.urdf` in [tether_controls](https://github.com/TerralabsCove/tether_controls), masses corrected 2026-10-31 (moved from cove-controls 2026-11-01). The step-reach sim (`sim/step_reach_sim/` there) uses it, not Cove's URDF. Results: [2026-10-28 step-reach note](../notes/2026-10-28-john-step-reach-sim.md), re-run 2026-10-31 at 14.35 kg. **[assumed]**

### Wire-routing comparison (sim, 2026-09-27)

Run on Cove's URDF with an assumed ±0.5-turn cable budget. **[assumed]** Not validated against hardware.

| Variant | Joint semantics | Result |
|---|---|---|
| Inchworm (slip rings) | All 7 joints continuous | Walked 1.08 m, climbed all 5 rungs, closed the table loop |
| Cable 360 | ±360° joints with cable winding | Hit the twist limit before the ladder |
| Existing (Cove as built) | ~290° Y travel, wiring-limited Z | J4 hit its 145° limit at the ladder |
