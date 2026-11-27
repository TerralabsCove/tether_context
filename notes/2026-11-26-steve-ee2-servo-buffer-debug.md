---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-26
---

# EE2 servo bus buffer fixed; servo driven over the radio with debug commands (2026-11-26)

Written by Steve's AI agent on 2026-11-26, from a bench session with Steve. Not authoritative. Nothing here changes
`truth/`. Follows [the morning's note](2026-11-26-steve-single-ee-spacemouse-arm7-bringup.md) and John's
[STS3215 on a C5 note](2026-11-24-john-sts3215-c5-bench.md). Touches [open question 20](../truth/open-questions.md)
(what the STS3215s are for) and [open question 7](../truth/open-questions.md) (camera data path).

The schematic, wiring and before/after drawings are in
[ee2-servo-bus-buffer.html](2026-11-26-steve-ee2-servo-buffer-debug/ee2-servo-bus-buffer.html) (open it in a browser).

Code, all on unmerged branches:

| Repo | Branch | Commits |
|---|---|---|
| tether_controls | `steve/ee-buf-debug` (on top of `hansi/ee-telemetry-dryrun`) | `93450d0` |
| tether_ros | `steve/single-ee-spacemouse` | `83eb8fe` (merge of `hansi/ee-telemetry-dryrun`), `8269325`, `aa820b5` |
| tethersmall | `steve/imu-bno08x` (on top of `steve/cmd-feedforward`) | `7bd1623` |

## Results

- **EE2's servo moved through the whole radio path.** Mac → Board 10 (USB) → ESP-NOW 5 GHz ch 36 → EE2 → 74LS125
  buffer board → STS3215. Servo ID 2 swung 30° each way at 150 steps/s with a 30 % torque cap. Every leg ended
  within 0.7° of its target, peak load 6.8-7.6 %, 12.4 V, 25 °C, torque off at the end. **[verified]** (tool output
  below; the servo was free on the bench)
- **The servo on this board is ID 2.** Nothing answers at ID 1. **[verified]** (scan of IDs 0-253)
- **Debug commands over the radio work without a gateway change.** They ride in a T_EE_CMD frame with flag 0x80;
  replies come back as T_EE_STATE-shaped frames with `ee | 0x80`. **[verified]** (scan, stat and swing above)
- **The reCamera hands tag data to the EE C5 over USB, but that data stops there.** Camera 2 was at 172.16.1.52 on
  the house Wi-Fi. Its `espbridge` log showed the C5 open and 30,922 messages sent with no errors. Board 10 saw zero
  camera packets in the same period: the end-effector servo firmware does not forward them. **[verified]**
  (espbridge log over SSH, gateway frame counts)

## The buffer board

The board is the 74LS125 half-duplex buffer from the diagram posted in Discord (drawing TC-EE2-BUF-001 rev C is the
same circuit): TX → 330 Ω → U1 pin 2, DIR → 330 Ω → U1 pin 1 with 10 kΩ to 3V3, U1 pin 3 → 220 Ω → DATA, DATA →
U1 pin 4 (the receive gate's enable), U1 pin 6 → 1N5819 → RX with 2.2 kΩ to 3V3, and a pull-up from DATA to +5V
(1.1 kΩ on this board, 1 kΩ in the drawing).

Three things were wrong or changed. They were not tested one at a time, so which were strictly needed is not known.

| Change | Before | Now | Evidence |
|---|---|---|---|
| Pull-up (1.1 kΩ to +5V) | On DATA, the servo side of the 220 Ω | On U1 pin 3, the chip side of the 220 Ω | DATA held low: 1.04 V at U1 pin 4 with 0.21 V at pin 3 before; 0.13 V at pin 4 and at the servo's signal pin after. **[verified]** (Steve's multimeter) |
| TX wire | XIAO D9 | XIAO D7 (GPIO12), as in the drawing | The firmware's loop test failed on EE2 with TX on D9 and passes on D7. **[verified]** |
| Ground | Pack − reached the XIAO's GND only through the buck | Unchanged | With EE2 on the Mac's USB and the buck off, the echo was clean but the servo never answered. On board power it answers. Steve confirmed the missing ground link. **[verified]** by behaviour; the link itself was not measured |

Why the pull-up position matters: with the pull-up on DATA, its current (about 3.6 mA) crosses the 220 Ω whenever
the chip pulls low, which lifts DATA about 0.8 V above the chip's output. The servo's spec sheet (ST-3215-C018)
gives low as 0-0.45 V. 1.04 V is out of spec. Steve reports that a jumper-wire prototype with the same 1.1 kΩ
worked, so 1.04 V may have been close to the servo's real threshold. **[assumed]**

The same arithmetic applies to rev C of the drawing, which has R6 (1 kΩ) from DATA to +5V: a low of about 1.1 V.
**[assumed]**, not measured on a board built to the drawing.

```text
                         +5V
                          |
                       [1.1 kΩ]   <- moved here (was on DATA)
                          |
TX D7 --[330]-- 2 |U1A> 3-+--[220]--+-- DATA -- servo signal (J2 pin 3)
DIR D8 --[330]--+- 1 (/OE)          |
                |                   |
             [10 kΩ]                |
                |                   |
               3V3                  |
                                    |
RX D6 --+--|>|-- 6 <U1B| 5 -- GND   |
        |  1N5819   4 (/OE) --------+
     [2.2 kΩ]
        |
       3V3            U1 pin 14: +5V (XIAO 5V pad), pin 7: GND, 100 nF across
```

## Firmware and tools

- **EE2 firmware:** env `xiao_c5_ee2_buf` in tether_controls `bench/boards/xiao-esp32-c5/sts3215_led_test`. It is
  Hansi's published end-effector source with the bus on D7/D6/D8 (echo checked and skipped, up to 3 tries), a
  `bustest` command, and the debug commands. **[as built]**, flashed on EE2 (C5 #2, `10:BD:A3:CD:D1:B8`).
- **It replaced Hansi's buffered build on EE2.** That build's source is not on any branch. A full flash backup is on
  Steve's Mac only (`tether_controls/bench/backups/`, untracked, not pushed). The two builds were not compared.
- **`tools/ee_debug.py`** (tether_ros): scan, stat, move, jog, swing, relax, rd, wr, stop for any servo ID, through
  Board 10. Debug moves ignore the EE's goal limits. The EE still caps torque (5-60 %) and speed, stops on load or
  stall, refuses EEPROM registers, and turns torque off 10 s after the last debug command. **[verified]** for scan,
  stat, swing and relax; the rest **[as built]**.
- **`tools/ee_control.py`** (tether_ros): the guarded T_EE_CMD path from the host. **[as built]**, run only against
  `fake_gateway.py`.
- **tether_ros now has Hansi's EE telemetry and command path** (`/tether/eeN/servo_states`,
  `/tether/eeN/servo_command`), merged into `steve/single-ee-spacemouse`. 18 unit tests pass. Not run in the
  container against hardware on this branch.
- **A XIAO ESP32-S3 bench sketch** for the same board is in tether_controls
  `bench/boards/xiao-esp32-s3/sts3215_buf_test` (loop test, hold-DATA-low, baud sweep). Its loop test passed; it never
  got a servo reply (it was only run on USB, without the ground link).

## IMU software from the earlier session (not verified)

From Steve's earlier session the same day, committed now:

- tethersmall `steve/imu-bno08x`: module nodes and a bare test board read a GY-BNO08X on I2C and send T_IMU (0x07);
  the gateway forwards it. **[as built]**
- tether_ros: `gateway_node` publishes `/tether/imu/<name>`, plus `tools/imu_monitor.py` and fake IMUs.
  **[as built]**, tested against the fake gateway only.
- The one hardware run, `imu_test_s3` on a XIAO ESP32-S3, reported the BNO08x not found on I2C (no ACK at 0x4A or
  0x4B). Cause not looked into. See John's [IMU wiring note](2026-11-26-john-imu-bno08x-module-wiring.md).

## Side effects to know about

- The S3 that carried the IMU test firmware (`7C:E8:B1:A1:43:4C`) now runs the servo bench sketch. Reflash
  `imu_test_s3` before the next IMU test.
- The board Steve identified as EE1 sent no radio packets while powered. Its firmware was not checked.
- EE2's servo 2 sat at 1780 steps (156.4°), outside the firmware's 1080-1660 range for ROS goals, so the guarded
  path will not power it until it is turned back into range.

## Open

- Which of the three board changes were needed. A test with the pull-up back on DATA would settle it.
- Reply error rate on the buffer board. With Hansi's build, servo 2 answered 404 of 602 telemetry reads.
- The spare gates' enables (U1 pins 10 and 13) should be tied to +5V as in the drawing. Pin 13 read 1.6 V earlier
  in the day, which suggests it is open. **[assumed]**
- A ground wire from pack − to the XIAO's GND that does not depend on the buck, so the board also works on USB.
- Camera tag data has no path to Board 10 while the EE C5 runs the servo firmware. The EE build needs
  `camera_slave`'s forwarding, or the camera needs its own C5.
- Hansi's buffered source should be pushed, or the new build reviewed as its replacement.
- Update drawing TC-EE2-BUF-001: R6 to U1 pin 3.

## Swing log

```text
>>> scan 5
servos: [2]
id 2: pos 1781 (156.5 deg) load +0.0% 12.4 V 24 C torque off mode 0 current 0.000 A  (rssi -38 dBm)
>>> swing 2 30
  id 2 -> 2121 (186.4 deg): ok, at 2114 (185.8 deg), peak load 7.2%
  id 2 -> 1780 (156.4 deg): ok, at 1785 (156.9 deg), peak load 7.6%
  id 2 -> 1439 (126.5 deg): ok, at 1447 (127.2 deg), peak load 6.8%
  id 2 -> 1780 (156.4 deg): ok, at 1772 (155.7 deg), peak load 7.6%
swing done; relax: ok
```
