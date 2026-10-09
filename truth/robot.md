---
status: active
owner: John Peng (hardware)
last_reviewed: 2026-10-08
---

# Robot: Cove and Tether

Every fact here carries a tag. **[verified]** means measured on hardware with a recorded artifact. **[as built]** means true of the physical Cove but not measured against the model. **[decided]** means a design decision with a log entry. **[assumed]** means used in sim or planning but not checked.

Nothing is **[verified]** yet. Gate G0 is what changes that.

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
| Modules | 3 wireless modules, one ESP brain each. No separate end-effector modules. | decided D-020 |
| Inter-module wiring | None. Fully wireless. | decided D-006 |
| Inter-module link | ESP-NOW first, NRF ESB as fallback (BLE ruled out) | decided D-019 |
| Batteries | Layout planned for 5 modules, needs rework for 3 (see open questions). 3 sizes, 5–6 total, 5,000 mAh main modules, ~2 h runtime target, ~$50 per small battery | decided D-004 |
| Battery protection | No BMS. Motors have built-in min-voltage shutoff. DC-DC converter for ESPs. | decided D-008 |
| End effectors | Symmetric servo claw on both ends, folds into a circular docking housing | decided D-005 |
| Video link | Unresolved. ESP bandwidth is insufficient. Jetson ruled out as too heavy. | open |
| Compute | Fully offboard | decided D-013 |
| Localization | Motion capture primary, AprilTag on docking as backup, encoders as last resort | decided D-012 |
| Control approach | Motion planning, no RL for now | decided D-014 |
| Electronics build | Breadboard, no PCB yet | decided D-007 |
| End-effector battery | Not yet specced | open |

## Simulation model

- **Model source:** `vendor/cove-controls/src/full_assembly/urdf/simple_assembly.urdf`, cloned from [TerralabsCove/cove-controls](https://github.com/TerralabsCove/cove-controls). **[assumed]** It is Cove's exported URDF and has not been audited against the hardware.
- **Collision geometry:** visual meshes used as provisional collision shapes. **[assumed]**
- **B-end contact point:** 49.5 mm along +Z from `wrist_link`, taken from the mesh envelope. **[assumed]**
- **Not modeled:** contact stability, friction and grip force, torque and current, cable fatigue, payload dynamics.
- **Note:** the sim models Cove's geometry. It does not yet reflect the offset layout (D-002) or the 3-module wireless design (D-020).

### Wire-routing comparison (sim, 2026-09-27)

Run on Cove's URDF with an assumed ±0.5-turn cable budget. **[assumed]** Not validated against hardware.

| Variant | Joint semantics | Result |
|---|---|---|
| Inchworm (slip rings) | All 7 joints continuous | Walked 1.08 m, climbed all 5 rungs, closed the table loop |
| Cable 360 | ±360° joints with cable winding | Hit the twist limit before the ladder |
| Existing (Cove as built) | ~290° Y travel, wiring-limited Z | J4 hit its 145° limit at the ladder |
