---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-27
---

# Module IMU firmware merged to main; tether_ros decodes it (2026-11-27)

Written by Steve's AI agent on 2026-11-27, from a session with Steve. Not authoritative. Follows John's
[on-arm note](2026-11-26-john-imu-on-arm-bringup.md) and closes two of its open items: the pull request for
`john/module-imu`, and a laptop reader for `T_IMU`. Touches [open question 31](../truth/open-questions.md).

## What was merged

| Repo | PR | What |
|---|---|---|
| tethersmall | [#9](https://github.com/TerralabsCove/tethersmall/pull/9), merge `5aad32a` | John's `john/module-imu` into `main`. It carries Steve's `COMMAND_FF` (#7) and Hansi's EE forwarding underneath. |
| tethersmall | #7 closed, #8 closed | #7's commits are on `main` through #9. #8 (Steve's own `steve/imu-bno08x`) is superseded: a second IMU firmware that was never on the arm. |
| tether_ros | [#5](https://github.com/TerralabsCove/tether_ros/pull/5), merge `fbe4859` | `T_IMU` decoder matched to John's layout. |
| tether_controls | [#9](https://github.com/TerralabsCove/tether_controls/pull/9), still draft | EE2 buffer-board firmware, now merged with John's button page (`8fdcce6`). Waits for a re-test on the servo. |

So `main` in tethersmall is now the firmware on boards 10 to 13. **[as built]** by commit content: `45c56ff` is in
`main`. The boards were not re-read.

**`COMMAND_FF` limits are still proposals.** 80 Nm big, 25 Nm small, kp 500. The code still calls them proposals;
merging put them on `main`, it did not agree the numbers.

## Two IMU frame layouts, one kept

Steve's `steve/imu-bno08x` and John's `john/module-imu` both defined `T_IMU` (`0x07`, 31 bytes). The first 29 bytes
match. The last two differed:

| Byte | Steve's branch (old tether_ros) | John's (on the arm, kept) |
|---|---|---|
| 15 | yaw accuracy, 0.5° (255 none) | RSSI, stamped by the gateway |
| 16 | RSSI | IMU restarts since boot |
| 14 bit 6 | unused | INT line dead, node polls |

tether_ros `main` had the old layout, so against the arm it would have shown the restart count as RSSI and the
RSSI as about 2 rad of yaw accuracy. It now reads John's layout. **[verified]** on John's 58 s full-arm capture
(tethersmall `deploy/hardware_logs/imu-full-arm-20261126/01-...bin`):

| IMU | Frames | RSSI, dBm | Restarts | Mean \|a\|, m/s² |
|---|---|---|---|---|
| 11 | 5,791 | −39 to −23 | 0 | 9.84 |
| 12 | 5,481 | −44 to −30 | 0 | 9.68 |
| 13 | 5,619 | −57 to −30 | 0 | 9.71 |

These match John's note (9.86 / 9.68 / 9.70, −28 to −36 dBm).

## Laptop reader

In tether_ros `main`: `/tether/imu/<name>` (`sensor_msgs/Imu`, one per module), IMU entries in `/diagnostics` with
rate, loss, RSSI, restarts and the INT line, `tools/imu_monitor.py` for the bench, and fake IMUs in
`tools/fake_gateway.py`. `robot_control.py` reports the IMUs in `/status`.

## Checks

- tethersmall, merged tree: `gateway_cam_c5_5g`, `arm7_11/12/13_c5_5g_imu` and `imu_bench_s3` build. 39 tests pass.
  Three test files and two tests in `test_deploy_logging.py` need `gymnasium`, which was not installed; they fail
  the same way on the old `main`.
- tether_ros: 18 tether_bridge tests pass; `imu_monitor` runs against `fake_gateway --imu 11 12 13`.

## Not tested

- tether_ros against the live gateway with the IMUs. Only the recorded capture was decoded.
- The ROS gateway node on hardware.
- Anything driven: no command was sent in this session.

## Still open from John's note

A logger for `T_IMU`, each IMU's rotation relative to its link, the in-place gravity check, why the gyro accuracy
flag stays at 0, what triggers the I2C dropouts, and the loose dock joint in the sim.
