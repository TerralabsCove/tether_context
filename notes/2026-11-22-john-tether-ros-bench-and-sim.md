---
status: draft
owner: Hansi Lee
last_reviewed: 2026-11-22
---

# tether_ros after the first container: a real motor through ROS, latency, camera on the gateway, sim (2026-11-22)

Written by John's AI agent on 2026-11-22, from Hansi's tether_ros repo. Hansi did the work. Not authoritative. Summary only: the code, write-ups and raw results are in [TerralabsCove/tether_ros](https://github.com/TerralabsCove/tether_ros) (private), branch `hansi/gateway-camera` (commit `3bf6f8f`), under `bench_results/`. That branch is open as [tether_ros PR #1](https://github.com/TerralabsCove/tether_ros/pull/1) and is not merged.

Follows Hansi's first container note, which is in [open PR #23](https://github.com/TerralabsCove/tether_context/pull/23) here and covers the container tested against fakes only. See also [Steve's sim note](2026-11-22-steve-tethersim-ros.md). Touches [open questions 7 and 13](../truth/open-questions.md).

## What is new

### 1. A real motor moved through ROS, on the bench

- Path: `gateway_node` in the container, a serial-to-TCP relay on the Mac, board 10 (gateway C5), ESP-NOW on 5 GHz channel 36, board 11, CAN, motors 0x01 / 0x02 / 0x03.
- Board 11 ran the tethersmall env `bench_all3_c5_5g`: one node board driving three motors on one CAN bus. It was on external power.
- **Turn:** motor 0x01 went +2 rad at 0.2 rad/s (kp 20, kd 1). It moved 1.968 rad. Largest tracking error 0.065 rad. The two held motors moved 0.0000 rad. `/joint_states` ran at 100 Hz. **[verified]** (`bench_results/2026-11-22_ros_turn_0x01`)
- **Sweep:** ±0.3 rad at 2.0 rad/s peak (kp 40, kd 1). It reached −0.291 to +0.299 rad. Largest tracking error 0.184 rad, almost all of it delay. **[verified]** (`bench_results/2026-11-22_ros_sweep_0x01`)
- These used bench values (sign 1, zero 0), not an arm calibration. No load on the motors. Only motor 0x01 was moved.

### 2. ROS adds about 1 ms, after a fix

- The first `gateway_node` added about 21 ms over the serial port. It sent commands on a 50 Hz timer, published state on a 100 Hz timer, and its serial reads blocked.
- Hansi made it event-driven: a command goes out as soon as it arrives, and state is published as soon as every joint reports. It now adds about 1 ms or less. The relay adds about 1 ms. **[verified]** (`bench_results/2026-11-22_latency_serial_vs_ros`, 14 sweeps, none aborted)
- Command to position is about 71 to 73 ms on every path. Most of that is the motor's own response at kp 40. The link round trip is about 5 ms.
- The delay is the same on every joint, because one command frame carries all the targets.
- A diagnostic was also fixed: the round-trip p95 read 152 ms when the real value is 8 ms.
- In sim, the tethersmall walking policy under these link timings: 60 % success on direct serial, 59 % on the event-driven ROS path, 56 % on the old path (not a significant drop). Simulated, not a real walking run.

### 3. The camera can share the motor gateway

- The camera link was moved to 5 GHz channel 36, the motor link's channel ([tether_camera PR #5](https://github.com/TerralabsCove/tether_camera/pull/5), open).
- A new tethersmall env, `gateway_cam_c5_5g`, makes the gateway C5 the camera's receiver too ([tethersmall PR #6](https://github.com/TerralabsCove/tethersmall/pull/6), open). `gateway_node` then publishes the camera topics itself. One C5 on the laptop instead of two.
- Tested against a fake gateway only. Not run with a real camera.
- The [11-21 camera numbers](2026-11-21-hansi-camera-c5-tags-on-master.md) were for 2.4 GHz channel 1. The link has not been measured on 5 GHz.

### 4. A bench tool without ROS

- `tools/gateway_bench.py` listens, holds, or sweeps one motor straight on the gateway's port. It refuses to start unless every motor reports OK, and damps on any fault.

### 5. Commands reach the sim through ROS

- Path: `/tether/joint_command`, `gateway_node`, tethersim's gateway emulation, the MuJoCo arm (`bench_results/2026-11-22_sim_through_ros`). Sim only.
- ROS's joint angles matched the sim's own within 1 mrad. Sign, zero and joint mapping in `sim7.yaml` are right.
- **The loaded joints sag.** Held at kp 500 / kd 5, the stance big pitch joint sagged 91 mrad (5.2°) and did not reach a +0.1 rad step. Two other joints sagged 31 and 34 mrad. Steve's note found the same.
- Cause: the COMMAND frame has one kp/kd for all motors and no torque field. Fixing it needs a protocol change: a torque feedforward field, per-motor gains, or gravity compensation on the node.

## Not done

- `gateway_node` against the real combined gateway with a camera.
- Any run on the arm. Everything real here is three bench motors with no load, on a quiet channel.
- The full 7-motor config. Hansi's first note calls it a placeholder: the motor-to-joint mapping, signs and zeros are unknown. This branch changes only its timing settings.
- Four pull requests hold this work and are open: tether_ros #1, tethersmall #6, tether_camera #5, and tether_context #23.

## What it means for the schedule

- "ROS nodes talk to the motors" in the [final push schedule](../plans/final-push-schedule.md) is the bench run in section 1.
- The sag in section 5 is the "holding the arm over the gateway" risk in the schedule. It has no owner yet.
