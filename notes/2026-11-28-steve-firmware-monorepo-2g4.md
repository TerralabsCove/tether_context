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

**State of the arm right now:** only the center module has the new 2.4 GHz firmware. The gateway, boards 11 and 13,
EE1 and EE2 are still on 5 GHz channel 36 and must be reflashed before the arm runs again. See
[Reflash status](#reflash-status).

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

| Board | MAC | Env | On 2.4 GHz ch 11? |
|---|---|---|---|
| 10, gateway | 10:BD:A3:C7:FC:5C | `gateway_cam_c5_5g` | **Not yet flashed** |
| 11 | 10:BD:A3:CA:2F:C0 | `arm7_11_c5_5g_imu` | **Not yet flashed** |
| 12 role, center (S3) | 7C:E8:B1:A1:43:4C | `arm7_12_s3_imu` | Flashed, boots **[verified]** |
| 13 | 10:BD:A3:CA:23:D8 | `arm7_13_c5_5g_imu` | **Not yet flashed** |
| EE1 (C5 #3) | 10:BD:A3:CD:BE:54 | `xiao_c5_ee1` | **Not yet flashed** with the 2.4 GHz build |
| EE2 (C5 #2) | 10:BD:A3:CD:D1:B8 | `xiao_c5_ee2_buf` (on the board now) | **Not yet flashed** |

MACs for 10, 11 and 13 are from [John's 11-26 note](2026-11-26-john-imu-on-arm-bringup.md).

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
| EE2 (unchanged) | C5 #2 | `10:BD:A3:CD:D1:B8` | |
| No longer EE1 | C5 #1 | `38:44:BE:1F:F9:DC` | |

C5 #3 arrived with Seeed's factory test firmware and was flashed with `xiao_c5_ee1` on 2026-11-27: servo 1 disabled
for ROS, servo 2 limited to 20..400 steps. **[as built]** It still has to be flashed with the 2.4 GHz build.

Still open: EE1's servo 1 rests at 4092, at the 4095 → 0 wrap. It needs `ofs 1 <n>` before ROS uses it.

The board Steve identified as EE1 in the [11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md), which sent no radio
packets, was most likely C5 #1. **[assumed]**, not checked.

## End C5 = servos + end camera

The C5 at each end of the arm is wired to both the STS3215 servos and the end reCamera's USB-C. So the EE builds
(`xiao_c5_ee1`, `xiao_c5_ee2`, `xiao_c5_ee2_buf`) now also do tether_camera's `camera_slave` job. This closes the
gap in the [11-26 note](2026-11-26-steve-ee2-servo-buffer-debug.md), where 30,922 camera messages reached the EE C5
and stopped there. **[as built]**, builds for all EE envs; **not tested on hardware.**

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
not send it. Boards 10 and 11 run that branch now (11-27 note), so reflashing them from tether-firmware removes the
battery frames until the work is brought into tether-firmware.

## Not tested

- Any board other than the S3 on 2.4 GHz channel 11, and the arm on 2.4 GHz at all: loss, RTT, range.
- The S3 with its CAN transceiver, motor and IMU wired.
- The end C5 carrying the camera link: no hardware run, on bench or arm, on either end.
- tether_ros `flash_dryrun.py` against tether-firmware beyond flashing the S3.

## Open

- Reflash 10, 11, 13, EE1 and EE2.
- Measure the arm link on 2.4 GHz channel 11 (open questions [14](../truth/open-questions.md) and
  [15](../truth/open-questions.md)).
- Two end cameras through one gateway peer (open question 32).
- Bring `T_POWER` into tether-firmware, or accept losing the battery frames.
- EE1 servo 1: `ofs 1 <n>` before ROS uses it.
- Commit the tether_ros `flash_dryrun.py` change.
- Update the old repo names in tether_ros, tethersim and tether_context docs.
