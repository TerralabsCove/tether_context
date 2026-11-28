---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-28
---

# All ESP firmware in one repo (tether-firmware); every link on 2.4 GHz channel 11 for now; S3 center module, new EE1, end C5 carries the camera (2026-11-28)

Written by Steve's AI agent on 2026-11-28, from sessions with Steve on 2026-11-27 and 11-28. Not authoritative.
Follows the [11-27 arm session note](2026-11-27-steve-arm-calibration-imu-sim-controllers.md) and the
[EE2 buffer note](2026-11-26-steve-ee2-servo-buffer-debug.md). Touches open questions
[6](../truth/open-questions.md) (end-effector power), [7](../truth/open-questions.md) (camera data path),
[14 and 15](../truth/open-questions.md) (radio margin, nodes on one channel) and [25](../truth/open-questions.md)
(battery frames), and adds [32](../truth/open-questions.md) (two end cameras, one gateway).

**State of the arm at the end of 11-28:** every board (gateway 10, modules 11, 12 and 13, EE1, EE2) is flashed from
tether-firmware `6f526e3` on 2.4 GHz channel 11. Each was checked on the bench on USB only. Nothing has run with the
arm powered. See [Reflash status](#reflash-status) and [Flashing, 11-28](#flashing-11-28).

## One firmware repo

[TerralabsCove/tether-firmware](https://github.com/TerralabsCove/tether-firmware) (private; Steve's clone is
`~/git/tether-firmware`) now holds every Tether ESP firmware and the code around it. Three repos were copied in
**without git history**, each into a folder of its own name. Paths inside each folder are unchanged, so
"tethersmall `firmware/src/node`" now means `tethersmall/firmware/src/node` in tether-firmware. **[as built]**
(tether-firmware `main`, commits `0deb548`, `e0e5c6c`, `6f526e3`)

| Folder | Was | Imported from |
|---|---|---|
| `tethersmall/` | TerralabsCove/tethersmall | `main` at `5aad32a` |
| `tether_controls/` | TerralabsCove/tether_controls | `main` at `2c3a814` |
| `tether_camera/` | TerralabsCove/tether_camera | `main` at `5679d1d` |

Merged into the old repos before the import, so they are in tether-firmware:

| Repo | PR | Who | What |
|---|---|---|---|
| tether_controls | #8 | Hansi | Button page in % of spec, new EE dock angles |
| tether_controls | #10 | Steve | `steve/ee-buf-debug`: EE builds, buffer board, debug commands over the radio |
| tether_camera | #6 | Steve | Plate tag sizes |
| tether_camera | #3 | Hansi | Eight live tags |

Each old repo's README now starts with a "Moved" pointer. tether-firmware's top-level `README.md` has a
board → firmware → env table; that table is the place to look up what to flash.

### Which repos are live

| Archived on GitHub (read-only) | Still live |
|---|---|
| tethersmall, tether_controls, tether_camera, tethertests, tether, cove-controls, terra-arm-locomotion-analysis | tether-firmware, tether_ros, tethersim, tether_context, terra-discord-mcp |

tether_controls was public. tether-firmware is private, so the Tether arm URDF and the firmware are no longer
publicly readable in their current form (the archived public tether_controls still is).

tether_ros, tethersim and this repo still use the old repo names in places. The paths inside each folder are
unchanged, so those references can be read as "that folder in tether-firmware".

## Radio: everything on 2.4 GHz channel 11, for now

**Why:** the center module is now a XIAO ESP32-S3 (below), which has no 5 GHz radio. Every board must share one
band and channel, so the whole arm moved to 2.4 GHz.

| | Before (to 2026-11-27) | Now |
|---|---|---|
| Motor link, camera link, EE link | 5 GHz channel 36, 6 Mbit/s 802.11a | 2.4 GHz channel 11, 1 Mbit/s 802.11b |

Channel 11 is the 2.4 GHz channel tethersmall measured as cleanest on 2026-10-11
([robot.md](../truth/robot.md#tethersmall-testbed-2026-10-11)). That measurement was with C3/C6 boards and two
slaves. Nothing has been measured on the arm on 2.4 GHz channel 11. The 5 GHz numbers (10-28 range test, 11-26
full-arm loss) do not carry over.

Where it is set, all in tether-firmware: **[as built]**

| What | Setting | To go back to 5 GHz |
|---|---|---|
| `tethersmall/firmware/platformio.ini`, `[c5g]` | `-DESPNOW_5GHZ=0 -DLINK_CHANNEL=11`. The `_5g` env names were kept, so they now build 2.4 GHz. | `-DESPNOW_5GHZ=1` |
| EE sketch, `tether_controls/bench/boards/xiao-esp32-c5/sts3215_led_test` | `EE_CHANNEL` defaults to 11; band and rate follow the channel. | `EE_CHANNEL` 36 |
| `tether_camera/esp/libraries/TetherLink/TetherLink.h` | `LINK_CHANNEL` defaults to 11. | `LINK_CHANNEL` 36 |

Going back to 5 GHz also means the center module goes back to a C5.

### Reflash status

tether_ros `tools/flash_dryrun.py` flashes by MAC. It was changed locally and **not committed yet**: it builds from
`~/git/tether-firmware` (override with env `TETHER_FIRMWARE`), has the S3 as board 12, and reads MACs with
PlatformIO's own esptool.

All flashed from tether-firmware `6f526e3`. Each board's MAC was read with esptool before flashing, and every flash
reported "Hash of data verified". Bench checks are in [Flashing, 11-28](#flashing-11-28).

| Board | MAC | Was running | Now (env) | On 2.4 GHz ch 11? |
|---|---|---|---|---|
| 10, gateway | 10:BD:A3:C7:FC:5C | `steve/battery-telemetry` build, 5 GHz | `gateway_cam_c5_5g` | Flashed **[as built]** (channel fixed by the build, not reported by the board) |
| 11 | 10:BD:A3:CA:2F:C0 | `steve/battery-telemetry` IMU build, channel 36 | `arm7_11_c5_5g_imu` | Flashed **[verified]** (boot line) |
| 12 role, center (S3) | 7C:E8:B1:A1:43:4C | S3 servo buffer test | `arm7_12_s3_imu` | Flashed **[verified]** (boot line) |
| 13 | 10:BD:A3:CA:23:D8 | `module-imu` IMU build, channel 36 | `arm7_13_c5_5g_imu` | Flashed **[verified]** (boot line) |
| EE1 (C5 #3) | 10:BD:A3:CD:BE:54 | `xiao_c5_ee1` from 11-27, no camera link | `xiao_c5_ee1` (servos + camera link) | Flashed **[as built]** |
| EE2 (C5 #2) | 10:BD:A3:CD:D1:B8 | tether_camera `camera_slave`, not EE firmware (below) | `xiao_c5_ee2_buf` (buffer board, servos + camera link) | Flashed **[as built]** |

## Center module is now a XIAO ESP32-S3

Board 12's job (Damiao esc `0x04`, motor 3) moved to the spare XIAO ESP32-S3, MAC `7C:E8:B1:A1:43:4C`. New env
`arm7_12_s3_imu`: **[as built]**

- CAN transceiver on XIAO D9/D10 (GPIO8/GPIO9 on the S3).
- BNO08x IMU on SDA D4, SCL D5, INT D0, RST D1; `IMU_ID` 12. Same pad names as on the C5 modules.

Flashed and booted. Boot line: **[verified]** (serial, USB only)

```text
tethersmall node D (motor 3) mac 7C:E8:B1:A1:43:4C channel 11 (radio 11) CAN tx 8 rx 9
```

On the bench, on USB only, the motor did not answer (status `0xF1`) and the IMU was not found. Nothing was wired, so
both are expected. **Not tested in the arm.**

- The C5 that was board 12 (`10:BD:A3:C7:EC:1C`) was taken out of flash_dryrun's table, so it cannot also answer as
  motor 3.
- The S3's previous firmware (the servo buffer test, tether_controls
  `bench/boards/xiao-esp32-s3/sts3215_buf_test`) was backed up on Steve's Mac only. That S3 was the spare used for
  that sketch, and before that for `imu_bench_s3` ([11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md)).

## EE1 is a new board

| | Board | MAC | Since |
|---|---|---|---|
| EE1 | C5 #3 | `10:BD:A3:CD:BE:54` (SoftAP `:55`) | 2026-11-27 |
| EE2 (same board) | C5 #2 | `10:BD:A3:CD:D1:B8` | |
| No longer EE1 | C5 #1 | `38:44:BE:1F:F9:DC` | |

C5 #3 arrived with Seeed's factory test firmware and was flashed with `xiao_c5_ee1` on 2026-11-27: servo 1 disabled
for ROS, servo 2 limited to 20..400 steps. **[as built]** Reflashed on 11-28 with the 2.4 GHz build that also carries
the camera link ([Flashing, 11-28](#flashing-11-28)).

Still open: EE1's servo 1 rests at 4092, at the 4095 → 0 wrap. It needs `ofs 1 <n>` before ROS uses it.

The board Steve identified as EE1 in the [11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md), which sent no radio
packets, was most likely C5 #1. **[assumed]**, not checked.

## End C5 = servos + end camera

The C5 at each end of the arm is wired to both the STS3215 servos and the end reCamera's USB-C. So the EE builds
(`xiao_c5_ee1`, `xiao_c5_ee2`, `xiao_c5_ee2_buf`) now also do tether_camera's `camera_slave` job. This closes the
gap in the [11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md), where 30,922 camera messages reached the EE C5
and stopped there. **[as built]**, builds for all EE envs. Bench-tested on EE1 and EE2 with fake camera lines over
USB, not with a camera and not on the arm ([Flashing, 11-28](#flashing-11-28)).

- USB lines that start with a digit are the camera's `<port> <message>` lines from `espbridge`. The C5 sends them
  over ESP-NOW as TetherLink packets, also during servo moves.
- Gateway commands for the camera go back over USB as `<port> <command>` lines. Any other USB line is a bench
  command, as before.
- One receive handler splits camera packets (first byte `0x54`) from EE frames (`0xA5`). The build checks
  `LINK_CHANNEL == EE_CHANNEL`.
- The C5 stays silent on the camera link until the camera's first line, and sends no fake tag messages. While a
  camera is attached, bench output starts with `# ` so `espbridge` ignores it. The `ee` command shows the camera
  link counters.

**Power rule.** The camera is the USB host and powers the C5 over USB-C. The buck's 5 V must stay off the C5's 5V
pad. A C5 on USB and the buck at the same time died on 2026-11-24
([John's note](2026-11-24-john-sts3215-c5-bench.md)).

**Known limit.** The gateway (`gateway_cam_c5_5g`) keeps one camera peer. With cameras on both ends, data from both
gets through, but camera commands go to whichever end C5 sent last. Fixing that needs a gateway change. Open
question 32.

## Not carried over: battery telemetry

tethersmall `steve/battery-telemetry` (`T_POWER`, `0x08`, battery frames) was never merged; its PR #10 was closed
unmerged and the branch sits in the archived repo. tether_ros already decodes `T_POWER`, but tether-firmware does
not send it. Boards 10 and 11 ran that branch until 11-28 and were then reflashed from tether-firmware, so **the arm
no longer sends battery frames**. The only flashed copies of that build are the two local backups listed in
[Flashing, 11-28](#flashing-11-28).

## Flashing, 11-28

All bench checks were on laptop USB only, with no motor or servo power and no other board powered.

| Board | Bench check | Tag |
|---|---|---|
| 10, gateway | Sends a `T_DIAG` frame every second. Heard no other board (none was powered). It does not report its channel until a camera `STAT` arrives; the build fixes it at 11 (`static_assert(LINK_CHANNEL == ESPNOW_CHANNEL)`, `LINK_CHANNEL` 11). | as built (channel) |
| 11 | Boot: `node A (motor 0) ... channel 11 (radio 11)`. IMU 11 found at 0x4B and reading, same pose as before the flash. Motor 0x01 no answer, CAN `tx_err` 128, the same before and after the flash. | verified |
| 12, center (S3) | Channel 11. No motor or IMU attached. | verified (boot line, above) |
| 13 | Boot: `node E (motor 4) ... channel 11 (radio 11)`. IMU 13 found at 0x4B and reading. Motor 0x03 no answer, the same before and after. | verified |
| EE1 | Camera path: 20 fake `<port> <message>` lines over USB (10 on port 5005, 10 on 5006) gave lines 20, bad 0, ESP-NOW sent 22 (20 data + 2 `STAT`), failed 0. Bench output had the `# ` prefix while lines came in and went back to normal 2 s after the last one. `ee` showed "gateway not yet" (the gateway was still on channel 36 at the time). Servos: scan found none, `stat 2` no reply (no servo power on USB). | verified |
| EE2 | Camera path: same result as EE1. `bustest` **failed** ("driver off: ... RX never goes low") and scan found no servos. Likely cause: with the buck off, the buffer board and servo ground are not powered or grounded on laptop USB; the [11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md) says EE2's servo ground reaches the XIAO's ground only through the buck. Re-run `bustest` with the buck on before trusting the servo bus. | verified (failure); assumed (cause) |

The motors not answering on 11 and 13 is expected with no motor power, and it was the same before the flash.

**EE2 was running tether_camera `camera_slave`, not EE firmware.** It printed `# camera 0 ... computer no`, which
means it was sending fake tags. Who flashed it, and when, is not known. That fits the
[11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md)'s open item, "camera tag data has no path to Board 10
while the EE C5 runs the servo firmware": the combined EE build now does both. That item is addressed in firmware
and not yet tested on the arm.

Firmware images saved before flashing, on Steve's Mac only (`~/git/tether_controls/bench/backups/`, not in any
repo):

- `board10_10BDA3C7FC5C_battery-telemetry_5g_2026-11-28.bin`
- `board11_10BDA3CA2FC0_battery-telemetry_5g_2026-11-28.bin`
- `ee2_10BDA3CDD1B8_camera_slave_before_2026-11-28.bin`
- `s3_7CE8B1A1434C_buf_test_before_center_2026-11-28.bin`

Boards 13 and EE1 were not backed up; their old builds can be rebuilt from git.

tether_ros `tools/flash_dryrun.py` (local, still uncommitted) now maps boards 11 and 13 to their `_imu` envs.

## Not tested

- Anything with the arm powered. The arm on 2.4 GHz at all: loss, RTT, range.
- Next check, on the arm: gateway on the laptop; tether_ros sees `STATE` from 11, 12 and 13, IMU frames, and EE
  frames from both ends; `ee` on each end C5 shows "gateway known"; camera tags arrive as `T_CAM_DATA`; EE2
  `bustest` passes with the buck on.
- The S3 with its CAN transceiver, motor and IMU wired.
- The end C5 camera link with a real camera, on either end.

## Open

- Run the check above with the arm powered.
- EE2 `bustest` with the buck on.
- Measure the arm link on 2.4 GHz channel 11 (open questions [14](../truth/open-questions.md) and
  [15](../truth/open-questions.md)).
- Two end cameras through one gateway peer (open question 32).
- Bring `T_POWER` into tether-firmware, or accept losing the battery frames.
- EE1 servo 1: `ofs 1 <n>` before ROS uses it.
- Commit the tether_ros `flash_dryrun.py` change.
- Update the old repo names in tether_ros, tethersim and tether_context docs.
