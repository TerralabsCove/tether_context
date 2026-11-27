---
status: draft
owner: John Peng
last_reviewed: 2026-11-26
---

# IMUs on the arm: firmware, flashing all four boards, calibration and first radio numbers (2026-11-26, evening)

Written by John's AI agent on 2026-11-26, from a working session with John at the arm. Not authoritative. It
follows the [wiring and plan note](2026-11-26-john-imu-bno08x-module-wiring.md) from the same day, which has the
reasons, the wiring table and the afternoon bench test.

**Scope.** The arm was at rest the whole time. The Mac only listened: no command was sent to any motor. Nothing
here says how the arm behaves when driven on this firmware.

Code and raw logs are in [tethersmall](https://github.com/TerralabsCove/tethersmall) (private), branch
`john/module-imu`: firmware at `45c56ff`, logs at `f00f862` under `deploy/hardware_logs/`. Every **[verified]**
below has its raw capture in one of these folders, each with a README:

| Folder | Holds |
|---|---|
| [`imu-module13-20261126`](https://github.com/TerralabsCove/tethersmall/tree/f00f862/deploy/hardware_logs/imu-module13-20261126) | Board 13, its IMU on the module and on the S3, the first gateway listens |
| [`imu-module12-20261126`](https://github.com/TerralabsCove/tethersmall/tree/f00f862/deploy/hardware_logs/imu-module12-20261126) | Board 12's first boot on the IMU build |
| [`imu-module11-20261126`](https://github.com/TerralabsCove/tethersmall/tree/f00f862/deploy/hardware_logs/imu-module11-20261126) | IMU 11 on the S3, then the wiring fault on the module |
| [`imu-full-arm-20261126`](https://github.com/TerralabsCove/tethersmall/tree/f00f862/deploy/hardware_logs/imu-full-arm-20261126) | Seven motors and three IMUs through the gateway |
| [`imu-bench-20261126`](https://github.com/TerralabsCove/tethersmall/tree/f00f862/deploy/hardware_logs/imu-bench-20261126) | The afternoon bench test |

## What is on the arm now

All four boards run tethersmall `john/module-imu` at `45c56ff`. **[as built]** Anyone who reflashes a board from
`steve/cmd-feedforward` removes the IMU code from it.

| Board | MAC | Build | Motors (esc ids) |
|---|---|---|---|
| 10, gateway | 10:BD:A3:C7:FC:5C | `gateway_cam_c5_5g` | none |
| 11 | 10:BD:A3:CA:2F:C0 | `arm7_11_c5_5g_imu` | 0x01, 0x02, 0x07 |
| 12 | 10:BD:A3:C7:EC:1C | `arm7_12_c5_5g_imu` | 0x04 |
| 13 | 10:BD:A3:CA:23:D8 | `arm7_13_c5_5g_imu` | 0x03, 0x06, 0x05 |

Each board was identified by MAC before it was written. Each module has one GY-BNO08X wired SDA D4, SCL D5,
INT D0, RST D1. **[as built]**

The spare XIAO ESP32-S3 (MAC 7C:E8:B1:A1:43:4C) now runs `imu_bench_s3`, the same IMU code alone. It replaced a
program that booted as "s3 buffered servo test". John approved overwriting it. Its source was not found on
John's Mac or in the org's repos.

## What was on the arm before

[Steve's note](2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md) says all four boards were flashed from
tethersmall `steve/cmd-feedforward` at `b3a0331`. That branch is `main` plus Hansi's 7-motor builds and
end-effector forwarding, plus Steve's `COMMAND_FF` (draft
[PR 7](https://github.com/TerralabsCove/tethersmall/pull/7), no reviews). Its limits:

| Path | Big motors | Small motors | Max kp |
|---|---|---|---|
| `COMMAND` | 12 Nm | 9 Nm | 100 |
| `COMMAND_FF` | 80 Nm | 25 Nm | 500 |

The code still calls the `COMMAND_FF` values proposals to be agreed before flashing the arm.

- **Board 13 matched exactly.** Its application image was read from flash and compared with a rebuild of
  `b3a0331`, env `arm7_13_c5_5g`. 411 of 1,067,312 bytes differ: the builder's home path (18 places), the build
  time (`00:38:56`) and the hashes. So board 13 ran that commit with no local edits. **[verified]** (module 13
  folder, file 02)
- **Boards 11 and 12 were not read.** That they ran the same commit is from Steve's note only.
- **Board 10 could not be read.** One 4 KB block at flash offset 0x54000 failed to read on every try, though the
  gateway ran normally. John chose to flash without a backup. Going back means flashing `gateway_cam_c5_5g` from
  `b3a0331`.
- **How the arm stood on 11-26 is not recorded here.** Steve's note says closed-loop driving had not been run.
  John says the arm was stood up that night. Which laptop script version ran is not known.

## The firmware

Details are in tethersmall [`docs/IMU.md`](https://github.com/TerralabsCove/tethersmall/blob/45c56ff/docs/IMU.md)
and [`deploy/PROTOCOL.md`](https://github.com/TerralabsCove/tethersmall/blob/45c56ff/deploy/PROTOCOL.md). In short:

- The motor code is Steve's, untouched. The IMU is read in a separate, lower-priority task with its own bus.
- The IMU task starts before the motor setup, so the IMU reports with motor power off.
- Each board sends `T_IMU` (frame type `0x07`, 31 bytes) once per orientation sample, 100 Hz: orientation
  quaternion with no magnetometer, calibrated gyro, accelerometer, accuracy flags, and the board's clock. That
  clock is the same one stamped on the board's motor reports.
- If the IMU stops answering, the board reruns the whole start sequence by itself.
- If no IMU answers at boot, the board prints which pins see the breakout and scans the bus.
- The gateway forwards `T_IMU` to the laptop.

**Nothing on the laptop reads `T_IMU` yet.** The reader in tether_ros (`steve/single-ee-spacemouse` at
`6bedbea`) skips frame types it does not know, so the new frames should not break it. That is from reading the
code. It was not run against the new gateway. **[assumed]**

The camera relay in the gateway was not changed and was not tested after the flash.

## Wiring faults found

The board's own pin survey found both. A powered breakout pulls SDA, SCL and RST up and holds INT low.

| Module | What the board saw | Cause | Result |
|---|---|---|---|
| 13 | SDA (D4) with no pull-up, the other three lines fine | SDA not connected through | John fixed the wire. Found on the next boot. |
| 11 | SCL (D5) held low. After John swapped the two wires at the C5, SDA held low instead. With both unplugged at the C5, both pins free. | John's meter showed continuity from SCL to GND at the IMU. | John cleared it. Found on the next boot. |

**[verified]** (module 13 folder, files 03 to 05; module 11 folder, files 03 to 06). How John cleared the short on
11 was not recorded. That IMU had run for 7 minutes on the S3 just before, so the short appeared when it went
onto the module.

D0 works as the interrupt input on all three C5 boards. That closes the D0 question in the wiring note.
**[verified]**

## Each IMU on its module, USB, motor power off

| | Board 11 | Board 12 | Board 13 |
|---|---|---|---|
| Found | First try, 0x4B | First try, 0x4B | First try, 0x4B |
| Run | 58 s | 58 s | 178 s |
| Sample rate | 100.07 Hz | 99.90 Hz | 100.07 Hz |
| Frames missing | 0 | 0 | 0 |
| Longest gap | 12.2 ms | 13.9 ms | 12.3 ms |
| I2C errors, IMU restarts | 0, 0 | 0, 0 | 0, 0 |

**[verified]** (module 11 file 06, module 12 file 01, module 13 file 06). On board 13, roll and pitch noise was
about 0.02° and drift at most 0.02° per minute. Modules 11 and 12 were being handled during their captures, so
their noise figures mean little. Accuracy flags read quaternion 3, gyro 0, accelerometer 2 at boot on all three.
The gyro flag never left 0 on any unit. Why is not known.

The afternoon bench firmware missed its first probe on every boot and ran at 97.7 Hz with gaps to 30 ms. Neither
happened with this firmware, on the C5s or the S3.

## Calibration

The accelerometer calibrates itself when the IMU is held still on several faces, and saves the result in the
chip. Moving a whole module through six faces is not practical, so IMUs were calibrated off the module.

| IMU | Where | Result on the bench | Reads once mounted |
|---|---|---|---|
| 11 | On the S3, two rounds of six faces | 9.69 to 9.85 m/s² on six faces, offsets 0.03 or less | 9.86 |
| 12 | Believed to be the afternoon bench unit (John). Not confirmed. | 9.71 to 9.80 that afternoon | 9.90, later 9.68 |
| 13 | Partly on the module, then on the S3 | 9.71 to 9.78 on five faces. The −x face was not measured. | 9.70 |

**[verified]** for the readings (module 11 files 01, 02, 06; module 12 file 01; module 13 files 07 to 11; full-arm
folder for the later 12 reading).

- **IMU 13 needed it most.** Before: +x read 10.22 and −x read 9.48, an offset of about 0.37 m/s². After: +x read
  9.78.
- **The calibration is saved in the chip.** It held through resets on both units, and through IMU 13 being
  unplugged and moved to another board.
- **The accelerometer flag restarts at 2 on every boot.** It does not show whether a unit is calibrated.
- **All three read about 1 % off true gravity once mounted,** though each was within about 0.3 % on the bench.
  IMU 12 gave 9.90 and 9.68 at two times that evening. If the module's pose differed between them, that is 0.2 m/s²
  of offset on one sensor.
- **Likely cause: mounting stress.** Glue or fasteners that bend or squeeze the breakout shift an accelerometer's
  zero. **[assumed]** One pose per IMU cannot show it, and the chips' own continuing self-calibration is not
  ruled out.

What this costs: sway measurement depends on changes, so it is not affected. Absolute tilt could be off by a
degree or so. The way out is to record each IMU in place over a few resting arm poses and correct on the laptop.
Not done.

## Dropout and automatic recovery

With IMU 13 on the S3, sitting still, four I2C reads failed with `ESP_ERR_INVALID_STATE`. This is the error from
the afternoon, when the old bench firmware retried for 252 s and never recovered. This time the firmware
restarted the IMU by itself: one gap of 0.5 s, then 100 Hz again, calibration intact. **[verified]** (module 13
folder, file 09)

- The cause is not known. Both dropouts that day were on the S3 and its jumper wires. No C5 on the arm showed
  one, but each has only minutes of run time.
- After this, the restart rule was changed from "no sample for 300 ms" to "three failed reads in a row". That
  version is the one on the arm. It has not met a dropout yet.

## Motors on the new build, through the gateway

Modules on their own batteries, no USB on the module boards, gateway on USB. No commands sent.

**Board 13 alone, 30 s, before the gateway was reflashed.** Motors 4, 5, 6 at 200.0 Hz, status OK on every
report, 1 report lost of about 17,000. The spacing of the board's own clock stamps was off the 5 ms grid by
0.19 to 0.32 ms at worst. **[verified]** (module 13 folder, file 12) After the gateway flash, with the IMU
frames forwarded: IMU 13 at 100.07 Hz with none lost in 28 s, motors losing 2 of about 17,000. (file 13)

**Whole arm, 58 s.** **[verified]** (full-arm folder)

| Stream | Rate, Hz | Lost | Worst gap, ms |
|---|---|---|---|
| Motors 0, 1, 2 (board 11) | 199.3, 198.9, 198.7 | 0.3 %, 0.5 %, 0.6 % | 10, 10, 15 |
| Motor 3 (board 12) | 198.6 | 0.7 % | 15 |
| Motors 4, 5, 6 (board 13) | 197.5, 197.4, 198.2 | 1.2 %, 1.3 %, 0.9 % | 15, 15, 10 |
| IMU 11 | 99.5 | 0.6 % | 30 |
| IMU 12 | 94.2 | 5.7 % | 50 |
| IMU 13 | 96.6 | 3.5 % | 31 |

- Every motor report had status OK. Signal at the gateway was −28 to −36 dBm.
- The gateway reported no bad frames, no queue drops and no short USB writes. So the losses are on the radio or at
  the senders.
- **How much of the loss the IMU frames cause is not known.** There is no run of the full arm without them.
  [robot.md](../truth/robot.md) has round-trip times for the all-C5 link, not loss.
- Motor loss is inside the 0 to 5 % the policy was trained with, per tethersmall `deploy/PROTOCOL.md`.
- Ways to cut the loss, none tried: a lower IMU rate, or one combined frame per board for its motors and IMU.

## Low battery voltage

Asked during the session: does the firmware report low battery?

- The Damiao feedback frame carries no voltage. It carries a fault code. The slave firmware copies that code
  into the status byte of each motor report, so an undervoltage fault (`0x9`) reaches the laptop. Steve's laptop
  script shows it. **[as built]**, read from the code on both sides.
- That arrives after the motor has already faulted. The firmware does not clear faults.
- The firmware never reads or sets the motors' undervoltage setting. What it is on our motors is not known.
- Steve's battery panel is an estimate from torque and speed plus a typed-in voltage. It is not a measurement.

This is [open question 25](../truth/open-questions.md) (does D-008's battery protection hold?). Nothing here
answers it. Options, cheapest first: clip-on LiPo alarms on the balance leads; read and report each motor's
undervoltage setting at boot; measure pack voltage on each module with a divider into the C5.

For the third option: in the XIAO ESP32-C5 pin file, D0 is the only header pin that is an ADC input, and INT now
uses it. **[assumed]** that the bottom pads offer no other.

## Powering a module board from USB and its buck together

Not done, on John's call. Seeed's page for the XIAO ESP32-C5 labels the 5V pin "VBUS", power input and output,
and says nothing about USB and an external 5 V together. The schematic was not read, and which pin the buck
feeds was not checked. Until then, treat it as unsafe: flash and read a module board on USB with motor power
off, and watch a powered module through the gateway. **[assumed]**

## Working notes

- Opening a C5's serial port straight after the flashing tool has reset it drops the port once. Opening it again
  works. The boot banner prints the MAC, so there is no need to read it with the tool first.
- Opening the gateway's port restarts the gateway. A capture starts with a gap of a few seconds.

## Not tested

- The arm driven on this firmware, with either command type.
- Radio loss with and without the IMU frames.
- The new restart rule against a real dropout.
- IMU angles against a known angle, slow rotation, a magnet nearby, a loaded motor nearby.
- The camera relay through the reflashed gateway.
- Steve's laptop script against the reflashed gateway.

## Open

- A laptop reader and logger for `T_IMU`. Without it the data goes nowhere.
- Each IMU's rotation relative to its link, with the arm at rest in a known pose.
- In-place gravity check over several arm poses, and a correction on the laptop if it confirms the 1 % error.
- Whether IMU 12 is the unit calibrated in the afternoon.
- Why the gyro accuracy flag stays at 0.
- What triggers the I2C dropouts.
- A pull request for `john/module-imu`. It is stacked on Steve's draft PR 7, which is itself unreviewed.
- Whether the sim gets a loose joint at the dock, so the policy can use this data. See the wiring note.
