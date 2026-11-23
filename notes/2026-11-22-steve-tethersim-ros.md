---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-22
---

# tethersim plugs into ROS 2 and the tether_ros container (2026-11-22)

Written by Steve's AI agent on 2026-11-22. Not authoritative. Summary only: the write-up, code and test results are in
tethersim, [docs/ROS.md](https://github.com/TerralabsCove/tethersim/blob/main/docs/ROS.md) (merged in
[tethersim PR #1](https://github.com/TerralabsCove/tethersim/pull/1), `2c7fdc8`), and in
[tether_ros PR #2](https://github.com/TerralabsCove/tether_ros/pull/2) (`b3ea07b`). Touches
[open question 12](../truth/open-questions.md) (sim update) and [open question 13](../truth/open-questions.md)
(comms layer in ROS).

Everything below was run against the simulator only. **Nothing here has touched the robot.**

## What exists now

- **The sim speaks the robot's own protocols**, so laptop code can't tell it from hardware:
  - tether_controls' master text protocol (v3) over UDP 4210 (`server --robot-link 4210`). tether_controls'
    own `bench/wireless_client/client.py` ran against it unchanged.
  - tethersmall's USB gateway frames over TCP 7001, with the node firmware's rules (newest sequence wins,
    2.5 rad/s slew, 200 ms watchdog, overspeed damping) run in physics (`--gateway-tcp 7001`).
  - tether_camera's pc_master lines over TCP 7002 (`--camera-tcp 7002`) and tagstream's JSON over UDP
    (`--tag-cast 5005`). Tags come from the sim's geometry and the v6 tag plates.
- **The team's container runs against it.** tether_ros now has a compose profile `sim`:
  `docker compose --profile sim up --build tether-sim`, with tethersim checked out next to tether_ros. It builds a
  tethersim image (1.4 GB; first build about 9–14 min, then under a minute) and points tether_bridge at it through
  `config/sim7.yaml`. Their image is unchanged.
- **A ros2_control driver for tether_controls' master** (`ros/tether_ros` in tethersim, C++): one plugin for both
  the robot and the sim, `tether.launch.py target:=sim|robot`. It adds gravity feedforward from the sim's model,
  camera tags as ROS topics, and a **digital twin**: the real arm's telemetry mirrored into the sim at 50 Hz.

## Results in sim

- **tether_ros container (Docker):**
  - `/joint_states` matched the sim's physics within 0.4 mrad.
  - `/tether/enable` held.
  - A +1 rad wrist command arrived in 0.44 s, against 0.4 s for the slew limit.
  - `/tether/estop` went limp.
  - Camera tags reached `/camera_b/tags`.
- **ros2_control driver:**
  - On the ideal link, a trajectory goal was reached within 0.6 mrad.
  - On the modelled SoftAP link, 4 of 4 runs reached the goal. This needed two fixes:
    - `enable` is re-sent;
    - the telemetry timeout is 1 s. At 0.5 s, 2 of 3 runs estopped.
- **Digital twin:**
  - At rest it matched within 0.4 mm at the tool.
  - In motion it ran about 0.05 rad (about 100 ms) behind.

## Findings for the hardware team

- **The gateway protocol cannot hold the full arm stiffly.** A COMMAND frame has one kp/kd for all motors and no
  torque field. At kp 500 / kd 5 (the Damiao MIT maximum), the stance-end big pitch sagged 0.087 rad (5°) in sim.
  At tethersmall's kp 40 it would sag about 1.6 rad and fold; that number is computed, not run. Holding the arm needs:
  - per-motor gains or a feedforward torque in the frame,
  - or gravity compensation on the node.
- **Two arm URDFs disagree.**
  - Which they are:
    - tethersim uses `terra_arm_description.zip`: datasheet motor limits 120/27 Nm, 16.6 kg.
    - tether_ros's `tether7.yaml` uses tether_controls' `arm.urdf`.
  - How they differ:
    - Joint names: `Revolute_44` vs `Revolute_112`, `SlipRing_1/2_spin` vs `EE_1/2_wrist`.
    - Axes and zeros also differ.
  - Consequences:
    - `sim7.yaml` maps by link and runs `urdf:=false`.
    - [robot.md](../truth/robot.md#simulation-model) lists the tether_controls file at 14.35 kg.
    - Which file is current is not settled.
- **Assumptions to confirm** **[assumed]**:
  - EE_1 is node 1.
  - Driver gains are 300/5 on the big motors and 60/1.5 on the small ones.
  - The telemetry timeout is 1 s and the enable window is 2 s.

## Also in this session (2026-11-21)

- Engineering drawings of the table ports: `docs/drawings/table_ports.pdf` in tethersim.
- Plywood circle sizes:
  - Ø19 in under each ground port;
  - Ø31.5 in short tabletop;
  - Ø21.7 in tall tabletop.

  The mushroom lip covers the outer 2 in of each tabletop, so the short-table ports moved to ±0.29 m and `tall_bridge`
  to −0.11 m. The climb still walks in sim. These are positions fitted to the hall model, not measured on site
  **[assumed]**.
