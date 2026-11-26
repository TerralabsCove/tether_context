---
status: draft
owner: John Peng
last_reviewed: 2026-11-26
---

# IMU on each module: GY-BNO08X wiring to the slave C5 and how it fits the control stack (2026-11-26)

Written by John's AI agent on 2026-11-26, from a conversation with John. Not authoritative. The wiring and the plan
are proposals. One IMU was then run on a bench board the same day: see [Bench results](#bench-results-2026-11-26).
Nothing has run on the arm.

## Why

Per John, 2026-11-26: the motor tests on 2026-11-25 showed a good amount of play in the docking port. The base
wiggles and the arm swings when it moves. The sim treats everything as rigid, so the policy may not cope. No
measurement of the play is recorded. **[as stated]**

The plan is one IMU per module, three in total: one by the center big motor and one by each of the other two big
motors. The part on hand is the GY-BNO08X breakout, 10 pins. Which chip is on it (BNO080, BNO085 or BNO086) is not
confirmed.

## What the slave firmware uses today

Read from the firmware flashed on the arm, tethersmall branch
[`steve/cmd-feedforward`](https://github.com/TerralabsCove/tethersmall/pull/7) at `b3a0331` (builds `arm7_11_c5_5g`,
`arm7_12_c5_5g`, `arm7_13_c5_5g`), and from the XIAO ESP32-C5 pin file in the Arduino core. **[as built]**

| C5 pin | Used by |
|---|---|
| D9 (GPIO9) | CAN TX, all three slaves |
| D10 (GPIO10) | CAN RX, all three slaves |
| USB | Serial debug |
| D0 to D8 | Unused |

The slave builds touch no other GPIO. The antenna-switch code only compiles for the C6. Boards 11, 12 and 13 use the
same pins, so one wiring works for all three.

## Wiring

Six wires. Match them to the silkscreen names on the breakout, not to header position.

| IMU pin | C5 pin | Notes |
|---|---|---|
| VCC | 3V3 | Not 5V. Keeps SDA, SCL and INT at 3.3 V. |
| GND | GND | |
| SDA | D4 (GPIO23) | The board's default I2C data pin. |
| SCL | D5 (GPIO24) | The board's default I2C clock pin. 400 kHz. |
| INT | D0 (GPIO1) | Goes low when a sample is ready. |
| RST | D1 (GPIO0) | Lets firmware reset a hung IMU. |
| PS0, PS1 | none | Both low selects I2C. |
| ADDR | none | Picks I2C address 0x4A or 0x4B. |
| CS | none | SPI only. |

Check before first power-up:

- **PS0 and PS1.** Leaving them open only works if the breakout pulls both low. Measure each to GND. If either
  floats, tie both to GND. **[assumed]** that this breakout pulls them low.
- **I2C address.** Run a scan once to see whether the boards answer at 0x4A or 0x4B. The one board tested answers
  at 0x4B with ADDR open.
- **D0 as an input.** In the [11-24 bench note](2026-11-24-john-sts3215-c5-bench.md) an LED ring worked on D1 and did
  nothing on D0, on a different C5. The cause was not found. Test D0 with the IMU's INT line first. If it does not
  read, move INT to D8 (GPIO8).
- **D2, D3 and D6 are left alone on purpose.** GPIO25 and GPIO7 are thought to be boot-strapping pins on the C5, and
  GPIO11 carries the chip's boot messages. **[assumed]**, not checked against the datasheet.

Keep the four signal wires short and away from the motor phase leads and the CAN pair. Motor switching noise is the
usual cause of this chip hanging the I2C bus.

## Why use INT and RST

The slave's control task runs at 1 kHz and does the CAN exchange every tick. An I2C read takes most of a millisecond
and this chip can stall the bus, so the read must not sit in that task.

- A separate, lower-priority IMU task sleeps until INT fires, reads the sample and stores the newest one.
- The interrupt edge gives the sample time, which the laptop needs to line IMU data up with joint data.
- No interrupt for about 50 ms means the IMU has hung. Pulse RST and mark the sample stale.

## What to read

- **Game rotation vector**: orientation without the magnetometer. The magnetometer is no use next to the motors.
- **Calibrated gyroscope**: angular velocity. This is the direct measure of swing.
- Linear acceleration is optional. Skip it at first.

Both at 200 Hz, to match the STATE rate. The laptop turns each orientation into a gravity direction per module.

## Fitting it into the stack

1. **Slave firmware.** STATE is fixed at 16 bytes, so the IMU needs a new frame type. `0x04` to `0x06` are taken on
   the open branches and `0x10` to `0x12` by the camera gateway. `0x07` is free. About 20 bytes: module, status,
   sequence, quaternion, gyro. The bench firmware already sends type `0x07` with a 31-byte payload.
2. **Gateway.** Forward the new frame the way `hansi/ee-telemetry-dryrun` forwards end-effector telemetry.
3. **Radio load.** Three more frames per cycle, on top of seven STATE frames on channel 36. Start at 100 Hz and watch
   the per-motor STATE rates.
4. **Laptop.** Log first, with the arm running today's motions. That gives the swing frequency and the base tilt
   before any control change.

## Using the data

- **First use, no retraining.** The docked module's IMU gives the real base tilt. Feed it into the gravity
  feedforward, which now assumes a rigid, level dock.
- **Policy input.** The sim must model the dock play first: a loose, sprung joint at the port, randomized. In a
  rigid sim the IMU reading follows from the joint angles, so the policy learns nothing from it.
- **Limit.** The link's round trip is 12 to 13 ms at p50 (see [robot.md](../truth/robot.md), all-C5 arm link). The
  laptop can damp slow swing of a few hertz. Fast rattle in the port needs lower accelerations and gains.

## Mounting

Mount each IMU on the rigid structure by the big motor. Record its orientation. Calibrate its rotation to the link
with the arm at rest in a known pose.

## Bench results (2026-11-26)

One GY-BNO08X on a bench board, USB to John's Mac. The agent logged the board's serial output and scored it. These
are measurements, but the raw logs sit in a temporary folder on John's Mac and are not filed in a repo. So nothing
here is tagged **[verified]** yet.

**Setup.** The board's boot banner says ESP32-S3, not C5. Its firmware prints "tethersmall IMU test board", pins
SDA 5, SCL 6, INT 1, RST 2, radio channel 11, 100 Hz. Those pins match D4, D5, D0, D1 on a XIAO ESP32-S3
**[assumed]**. The firmware source was not on the tethersmall remote when checked. An S3 has no 5 GHz radio, so
this board cannot join the arm's channel 36 link. Opening the serial port from the Mac resets the board.

### Boot

12 reset cycles, all the same:

| | Result |
|---|---|
| First probe fails | 12 of 12, with three I2C errors (`ESP_ERR_INVALID_STATE`) about 0.6 s after reset |
| Recovers after one IMU reset | 12 of 12 |
| Address | 0x4B |
| Reset to first sample | 1.59 to 1.60 s |

The miss is the same on every boot, so it is timing, not wiring. Likely the probe runs before the chip is ready.
After cycle 12 the USB serial link went silent until a replug. Likely caused by the rapid reset cycling.

### Still, 179 s

| Measure | Result |
|---|---|
| Frames received | 17,452. No CRC failures. 12 missing (0.07 %), never two in a row. |
| IMU resets during the run | 0 |
| Sample rate | 97.7 Hz. In 386 of the 10 ms slots no sample was sent. |
| Longest gap | 30 ms, twice |
| Roll / pitch noise | 0.011° / 0.018° standard deviation |
| Heading drift | +0.002° per minute |
| Gyro at rest | Mean zero on all axes |
| Gravity | 9.65 m/s², about 1.5 % low |
| Accuracy flags | Quaternion 3, gyro 0, accelerometer 2 |

The frame layout (sequence, microsecond clock, quaternion, gyro, acceleration) was worked out from the data, not
from the source. Gyro counts are thought to be about 0.001 rad/s each **[assumed]**.

### Calibration

John held the board still on each of its six faces for about 5 s, partly by hand, then repeated the six faces.

- Before: flat read 9.649 m/s² and flipped read 9.970. That is an offset of about 0.16 m/s² on z.
- The accelerometer accuracy flag went from 2 to 3 about 17 s into the first pass.
- After, second pass:

| Face up | Gravity, m/s² |
|---|---|
| +z / −z | 9.786 / 9.804 |
| +y / −y | 9.769 / 9.786 |
| +x / −x | 9.747 / 9.713 (the −x pose was cut short by the dropout below) |

- Offsets are now 0.01 to 0.02 m/s² per axis, about 0.1° of tilt. The x axis reads about 0.7 % lower than z.
- **The calibration is saved in the chip.** Flat read 9.805 after an ESP reset and 9.803 after a USB unplug and
  replug. It read 9.65 after every reset before calibrating.
- The accelerometer flag restarts at 2 on every boot, so the flag does not show whether a sensor is calibrated.
- Gyro accuracy stayed at 0 throughout, at rest and after calibration.

### Dropout and recovery

During the last pose the IMU dropped out. I2C reads failed with `ESP_ERR_INVALID_STATE`. The board then printed
"NOT FOUND: ACKs, but the SH-2 open (begin_I2C) failed" about once a second for 252 s and never recovered. John
checked the wires and found nothing loose. The trigger is not known.

An ESP reset, with the IMU still powered, brought it back on the normal boot sequence. It then ran 222 s with no
bad frame. So the chip and wiring were fine, and the firmware's runtime retry cannot do what its boot code does.

### Firmware fixes this points to

1. **Runtime recovery.** Do the whole boot sequence in the retry: restart the I2C driver, pulse RST, wait for INT,
   reopen the sensor, turn the reports back on. An arm slave cannot reset its ESP to get the IMU back.
2. **Boot probe.** Wait for INT, or longer after RST, before the first probe.
3. **Rate.** Send on the IMU's interrupt, not a fixed 10 ms tick.
4. **Gyro accuracy.** Find out whether gyro calibration is on, or whether the flag is read wrongly.

### Not tested

Angle accuracy against a square, slow rotation, magnet immunity, a loaded motor nearby, and the radio link.

## Open

- Whether the calibration and recovery results hold on a C5 and on the arm.
- Where the bench firmware source lives, and filing the raw logs.
- Which chip is on the breakout.
- How much play the dock has, measured.
- Whether D0 reads as an input on the slave boards.
- Whether three extra frames per cycle cost STATE rate on channel 36.
- Who writes the firmware, and on which tethersmall branch. The flashed branch is an unmerged draft.
