---
status: draft
owner: Steve Lu
last_reviewed: 2026-11-26
---

# Single-EE SpaceMouse teleop, 4-board C5 flash, and live 7-motor digital twin (2026-11-26)

Written by Steve's AI agent on 2026-11-26. Not authoritative. Summarizes work pushed to unmerged feature branches:

- `TerralabsCove/tethersim` branch `steve/single-ee-spacemouse` (HEAD `0725405`)
- `TerralabsCove/tether_ros` branch `steve/single-ee-spacemouse` (HEAD `6bedbea`)
- Flashed firmware from `TerralabsCove/tethersmall` branch `steve/cmd-feedforward` (`b3a0331`, 5 GHz channel 36)

Touches [open question 13](../truth/open-questions.md) (comms / ROS / feedforward), [open question 15](../truth/open-questions.md) (3 modules + gateway on one 5 GHz channel), [open question 24](../truth/open-questions.md) (wireless E-stop), and [open question 25](../truth/open-questions.md) (D-008 battery monitoring / undervoltage).

**Hardware scope boundary:** All 7 motors were powered, flashed, streamed over 5 GHz ESP-NOW through Board 10, and live-mirrored into `tethersim` while limp **[verified]**. **Closed-loop torque driving (`Enable` / `COMMAND_FF`) on the physical 7-motor arm has not been run yet.**

---

## 1. Hardware bring-up: 4× XIAO ESP32-C5 flash and live 7/7 motor link

All four arm/gateway XIAO ESP32-C5 boards were flashed from `tethersmall` (`steve/cmd-feedforward` @ `b3a0331`) using PlatformIO with MAC verification via `esptool` `BASE MAC` **[verified]**. End-effector C5s (`xiao_c5_ee1`, `xiao_c5_ee2`) were intentionally skipped for this single-EE bench session (assuming one end is locked in a floor port and one end is free).

| Board | Role | PlatformIO env | Verified `BASE MAC` | Motors (ESC IDs) | Status |
|---|---|---|---|---|---|
| **Board 10** | USB gateway (5 GHz ch 36) | `gateway_cam_c5_5g` | `10:BD:A3:C7:FC:5C` | — | Flashed; 1 Hz `DIAG` over USB CDC, `bad_crc: 0` **[verified]** |
| **Board 11** | Module 1 (base / stance) | `arm7_11_c5_5g` | `10:BD:A3:CA:2F:C0` | 0–2 (`0x01`, `0x02`, `0x07`) | Flashed & streaming **[verified]** |
| **Board 12** | Module 2 (center joint) | `arm7_12_c5_5g` | `10:BD:A3:C7:EC:1C` | 3 (`0x04`) | Flashed & streaming **[verified]** |
| **Board 13** | Module 3 (free end) | `arm7_13_c5_5g` | `10:BD:A3:CA:23:D8` | 4–6 (`0x03`, `0x06`, `0x05`) | Flashed & streaming **[verified]** |

### Live 7/7 motor check on Board 10 (`/dev/cu.usbmodem2101`) **[verified]**

With all 3 modules powered on the bench and Board 10 plugged into macOS over USB CDC, all 7 motors reported `0x00 OK` concurrently on 5 GHz channel 36 (`bad_crc: 0`, `bad_frames: 0`, `queue_drops: 0`):

| Motor index | ESC ID | Rate | Sample `q` (rad) | Temp | RSSI |
|---:|---|---:|---:|---:|---:|
| 0 | `0x01` | 220 Hz | `-1.752` | 19 °C | `-49 dBm` |
| 1 | `0x02` | 220 Hz | `-2.197` | 20 °C | `-49 dBm` |
| 2 | `0x07` | 220 Hz | `+2.483` | 19 °C | `-49 dBm` |
| 3 | `0x04` | 191 Hz | `+0.096` | 20 °C | `-52 dBm` |
| 4 | `0x03` | 215 Hz | `+2.767` | 21 °C | `-54 dBm` |
| 5 | `0x06` | 215 Hz | `-3.083` | 21 °C | `-54 dBm` |
| 6 | `0x05` | 201 Hz | `+2.336` | 20 °C | `-54 dBm` |

### Live digital-twin mirroring **[verified]**

- Both `tools/robot_mirror.py` and `tools/robot_control.py` (in `tether_ros`) streamed all 7 physical motor states into `tethersim` (`POST /api/robot/mirror`) at ~44–46 Hz while limp.
- Moving physical joints 4 and 6 by hand (`delta_deg = [0.0, -0.3, -0.1, 0.1, 7.9, 0.0, -8.6]`) moved the 3D arm live in `tethersim`.
- Note on flashing pitfall: macOS USB port assignments swapped between Board 12 and Board 13 mid-session (`/dev/cu.usbmodem1101`); flashing was redone with a MAC-checked wrapper so each board is guaranteed to carry its matching `arm7_1x_c5_5g` image.

---

## 2. `tethersim` changes (`steve/single-ee-spacemouse`, `fd7493d`..`0725405`)

- **New default scene `single_ee`** (`fd7493d`, `b0b8068`, `22e2fb0`) **[verified in sim]**:
  - Open studio floor with one floor docking port (`floor_1` on `floor_1_disc`), `MingEE-male_2` latched into `floor_1`, and `MingEE-male_1` free for 6-DOF teleop (no Watt Hall stairs/furniture).
  - Starting pose optimized to an exact **0.00° straight vertical** configuration: lower link tube (`EndBlock_2→EndBlock4Config_1`) and upper link tube (`EndBlock4Config_2→EndBlock_4`) aligned at 0.00° tilt along `+Z`, all three pitch axes parallel (zero roll twist), and `MingEE-male_1` pointing straight up (`dock+Z = [0, 0, -1]`) at `[-0.0057, 0.0767, 1.186] m`.
  - Vertical stance joint angles: `{'Revolute_73': -1.1903, 'Revolute_29': 0.0925, 'EE_2_wrist': 0.0, 'Revolute_112': -2.1729, 'Revolute_57': -1.597, 'Revolute_22': 0.0, 'EE_1_wrist': 0.0}`.
  - Verified 6-DOF SpaceMouse / API teleop response (`±X`, `±Y`, `-Z`, `RX`, `RY`, `RZ`) from the vertical pose without singularity lockup.
  - Fixed 3Dconnexion `NavLibMouse` `view.target` tracking in `web/navlib.js`.
- **Collapsible inspector UI + live debug motor sliders** (`67a8a86`, `0ca0c42`, `d84de1b`, `98de7cd`) **[verified in sim]**:
  - Made all `.property-section` inspector panels collapsible (`localStorage`-persisted).
  - Added collapsible `Motor sliders (debug · live)` in the Drive panel.
  - Defaulted slider `0°` reference to the vertical standing pose (`scene.stance.joints`) rather than bent CAD zero; added **Zero motors**, **Go to zero**, **Sync**, and **Default zero** buttons.
  - Fixed `World.manual()` (`tethersim/engine.py`) and `web/drive.js` / `web/studio.js` so dragging sliders or clicking `Go to zero` keeps SpaceMouse Drive armed (`debugSlideGraceUntil`), automatically pauses mirror authority (`/mirror_off`) when switching from passive mirroring to driving, and adds **Mirror live** + real-arm re-sync on **Sync**.
- **Emergency stop & fault interlock** (`b32121b`, `4c38f7e`) **[verified in sim]**:
  - Added always-visible red **E-STOP** button in the top bar, **EMERGENCY STOP** in Drive, and global `Shift+Esc` shortcut.
  - Backed by `World.estop()` + `POST /api/estop` (`tethersim/engine.py`, `tethersim/server.py`) with immediate `_frame = None` snapshot invalidation and `HTTP 409` fault interlock on manual/teleop commands until Reset.
  - Wired UI `triggerEstop()` to hit both `/api/estop` and the host hardware bridge `http://127.0.0.1:8768/estop`.
- **Real robot (Board 10) Drive panel** (`4c38f7e`) **[as built, UI tested against limp bridge]**:
  - Collapsible panel in Drive talking to host `http://127.0.0.1:8768` (`Enable` / `Disable`, `Zero real arm`, `Go limp`, `Mirror live`).
- **Battery (6S LiPo · est.) panel** (`0725405`) **[as built, `node --check` passed; Docker container rebuild pending]**:
  - Collapsible panel in Drive showing all 3 modules (`mod11` 5 Ah, `mod12` 6.4 Ah, `mod13` 5 Ah), live estimated `%` / `V` / `W` / runtime, Damiao `0x09` undervoltage alert badge, and `Set V` / `100%` sync controls.

---

## 3. `tether_ros` changes (`steve/single-ee-spacemouse`, `166d7a1`..`6bedbea`)

- **Docker / ROS 2 teleop integration** (`166d7a1`) **[verified in Docker]**:
  - Defaulted `SIM_SCENE=single_ee` in `compose.yaml` and `.env.example`.
  - Added ROS 2 `teleop_node` (`src/tether_bridge/tether_bridge/teleop_node.py`) bridging `/tether/teleop_twist`, `/tether/teleop_frame`, `/tether/teleop_speed`, `/tether/teleop_stop` to `sim:8766/api/control`.
  - Added unit tests `src/tether_bridge/test/test_teleop.py` (13/13 pytest passing in `tether-ros:jazzy`).
  - Added host SpaceMouse CLI `tools/spacemouse_teleop.py` (verified handshake with local macOS 3Dconnexion `3DxNLServer` v1.5.1 at `wss://127.51.68.120:8182`, with `pyspacemouse` fallback). Note: on macOS, 3Dconnexion's DriverKit daemon holds exclusive puck access, so NavLib WAMP v1 is the working path.
- **Host Board 10 mirror & hardware control bridge** (`b0da20e`, `7f7e505`, `0ea56aa`) **[limp mirror verified; enabled `COMMAND_FF` as built / untested on hardware]**:
  - `tools/robot_mirror.py`: read-only Board 10 → `tethersim /api/robot/mirror`.
  - `tools/robot_control.py`: HTTP bridge on `http://127.0.0.1:8768` that boots limp & mirroring, exposes `/mirror_off` and `/mirror_on` guarded by `sim_op_lock` (eliminating mirror vs. enable HTTP 409 races), and when enabled sends `COMMAND_FF (0x06)` at 50 Hz with gravity feedforward from `tethersim /api/robot/gravity`, conservative caps (`<= 0.5 rad/s` slew, `0.65 rad` tracking-error trip, `kp = 150 / 40`, `kd = 4.5 / 1.5`), and E-STOP / stale-state watchdogs.
- **3-module 6S LiPo estimator & UV monitor** (`6bedbea`) **[as built, `py_compile` passed]**:
  - Added per-module energy integration, 6S LiPo OCV voltage-to-% curve (`POST /battery`), `.robot_battery_state.json` persistence, and live Damiao `0x09` undervoltage fault detection in `tools/robot_control.py`.

---

## 4. Battery telemetry hardware finding **[verified in firmware/docs]**

Checked `tethercontrol/libraries/DamiaoCan/src/DamiaoCan.h` (`REG_UV_Value = 0`, `REG_KI_APR = 28`, `REG_OV_Value = 29`) alongside [robot.md](../truth/robot.md) (D-008: "No BMS"):

- Damiao motors do **not** expose live DC bus voltage over CAN — only the status fault nibble (`0x09` undervoltage, `0x08` overvoltage) and static UV/OV threshold registers.
- The module ESP32-C5s have no ADC battery voltage divider wired.
- Therefore software cannot directly read pack voltage today; the new Battery panel reports **estimated** SoC (torque/speed power integration + idle draw **[assumed]**), calibrated by user LiPo-checker voltage entry (`Set V` / `100%`), paired with real-time `0x09` undervoltage warnings from motor feedback frames. True voltage telemetry would require an ADC divider on each module C5 or a smart BMS.

---

## 5. Not yet verified / open follow-ups

- **Closed-loop physical motor driving (`COMMAND_FF`):** `Enable` in `tools/robot_control.py` has not yet been tested on the real 7-motor arm. Before enabling torque, verify per-joint sign/direction, physical zero offset vs. `tethersim`, and confirm which physical end is anchored (`EE_2` vs `EE_1`).
- **`tether_ros` `gateway_node` vs `COMMAND_FF`:** `tether_ros` branch `steve/single-ee-spacemouse` branched from `main`, so the containerized ROS `gateway_node` does not yet carry `COMMAND_FF (0x06)` (only host `tools/robot_control.py` does). Merge/rebase with `tether_ros` `COMMAND_FF` work when ready.
- **Battery panel live deployment:** Commits `0725405` (`tethersim`) and `6bedbea` (`tether_ros`) are syntax-checked and pushed, but the running `tether_ros-sim-1` Docker image and host `robot_control.py` process still need a rebuild/restart to show the Battery panel live.
- **End-effector C5s:** `xiao_c5_ee1` and `xiao_c5_ee2` were not flashed or tested alongside the 3 module radios on 5 GHz ch 36.
- **Damiao `UV_Value` register check ([open question 25](../truth/open-questions.md)):** Still not read/raised from motor default to ~19.8–21 V on the 7 motors.
