---
status: draft
owner: Irisy
last_reviewed: 2026-10-13
---

# Embedded controls bench

This records the current motor-control bench result. Code-coupled instructions
remain in the control repositories.

## Architecture

- **[decided D-020]** There are three wireless modules: master ID 0, left ID
  1, and right ID 2.
- **[as built]** The laptop talks to master ID 0 through its Wi-Fi SoftAP and
  UDP port 4210.
- **[as built]** The master sends full-state commands to nodes over ESP-NOW.
- **[decided D-024]** Master ID 0 contains two motors. Remote module IDs 1 and
  2 contain three motors each, for eight total. The type and mechanical role
  of each remote module's third motor have not yet been recorded.
- **[assumed]** Each module talks to its local motors over a private 1 Mbit/s
  Classical CAN bus. No motor shares a wired CAN bus across modules.
- **[as built]** CAN IDs only need to be unique within one local bus. IDs may
  overlap across modules because the three CAN buses are electrically separate.
- **[assumed]** Final modules are XIAO ESP32-C6 boards with 3.3 V CAN
  transceivers. Current end-to-end measurements used ESP32-S3 boards and a
  temporary laptop-owned DM-USB-CAN path.

## Identity rules

- **[verified]** Tether node IDs are configured values. They are independent
  of Wi-Fi MACs and Damiao CAN IDs.
- **[verified]** ESP-NOW nodes must peer with the master ESP's **SoftAP MAC**.
  The master station MAC is only its configuration identity. Using the station
  MAC for the node peer leaves the node offline.
- **[as built]** The master is configured and flashed first. Nodes 1 and 2 may
  then be added in either order.

## Current motor map

| Node | Motor | Slave CAN ID | Feedback/master ID | PMAX | VMAX | TMAX | Status |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | small | `0x07` | `0x17` | 12.5 | 10 | 28 | **[verified]** scan and feedback; assigned to master |
| 0 | big | `0x04` | `0x14` | 12.5 | 20 | 200 | **[as built]** current bridge configuration; assigned to master |
| 1 | small | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |
| 1 | big | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |
| 1 | third (type unknown) | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |
| 2 | small | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |
| 2 | big | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |
| 2 | third (type unknown) | unknown | unknown | read from motor | read from motor | read from motor | **[assumed]** not scanned |

The firmware reads PMAX, VMAX, and TMAX from motor registers 21–23 before it
allows enable. Static values are bridge inputs and commissioning references,
not a substitute for reading the connected motor.

## Bench result

- **[verified]** The complete laptop -> master -> ESP-NOW node -> USB-CAN
  bridge -> motor path acknowledged reset, position, enable, disable, and
  estop commands.
- **[verified]** One motion test changed reported position from `0.000` to
  `0.050` rad. The enabled telemetry was `flags=0039`, with increasing CAN RX
  and TX counts, `fail=0`, and `buserr=0`.
- **[verified]** `flags=0038` is motor present, CAN active, limits valid,
  disabled, and estop clear. `0039` adds enabled. `003c` has estop latched.
- **[verified]** Damiao status `0` is disabled and status `1` is enabled.
  Fault values start at `8`. The older `motor_err` display label was
  misleading and is now `motor_status`.
- **[as built]** The updated laptop watchdog estops the master's local motor
  and both remote nodes after one second without heartbeat. Every motor path
  disables after 60 ms without a fresh synthesized or received command.

## C6 readiness

- **[verified]** The deployment Arduino firmware compiles for
  `XIAO_ESP32C6` with Arduino-ESP32 `4.0.0-RC1` and ESP-IDF 6.1.
- **[verified]** Protocol version 3 provides three motor slots. Master ID 0
  uses two slots; remote IDs 1 and 2 use all three. It compiles for a XIAO
  ESP32-C6 master, a three-motor XIAO ESP32-C6 node, and an ESP32-S3 master.
  The simulator verifies node-specific slot counts, independent sequences, and
  watchdogs. Physical multi-motor-on-one-bus behavior is not yet verified.
- **[verified]** On 2026-10-12, Espressif's latest stable Arduino core is
  3.3.12 and its latest prerelease is 4.0.0-RC1. This project requires the
  prerelease because the stable line does not expose the supported IDF 6.1
  TWAI node API.
- **[verified]** The native ESP-IDF project builds for `esp32c6` with ESP-IDF
  `v6.1` and the supported `esp_twai.h` driver.
- **[verified]** `tethertests/espnow_latency` supports XIAO ESP32-C6 and has
  been exercised between a C6 and an S3. It reports the station MAC used for
  ESP-NOW node identity.
- **[as built]** The latency test does not report a SoftAP MAC. Use the C6
  identity sketch in `tether_controls/bench` for master provisioning. A node must
  store the master's SoftAP MAC, not its station MAC.
- **[assumed]** End-to-end C6 radio and CAN behavior will match the S3 logic.
  It is not hardware-verified until the XIAOs and transceivers are tested.
- **[as built]** The C6 firmware uses D9/GPIO20 for TWAI TX, D10/GPIO18 for
  TWAI RX, and configures the XIAO onboard-antenna RF switch.

Before first C6 motion, verify transceiver supply voltage, TXD/RXD direction,
standby or enable state, CAN_H/CAN_L, common ground, 120-ohm end termination,
1 Mbit/s bitrate, motor IDs, and live feedback. Keep a hardware motor-power
cutoff accessible.

## Software status

- `tether_controls/firmware/tether_control_arduino` is the canonical firmware.
  `tether_controls/bench` contains commissioning tools and the exercised S3
  snapshot; it is not a second production source.
- The Arduino edition is the current deployment path. It includes
  SoftAP/UDP laptop control, unicast MAC provisioning, discovery, presence,
  both watchdogs, and direct TWAI motor control. Protocol version 3 selects
  slots `0` and `1` on the master and slots `0` through `2` on each remote
  node, with independent command and telemetry state for every motor on a
  module's shared TWAI bus.
- The native IDF edition is archived under `tether_controls/archive`. It is a
  read-only historical reference and not a deployment option.
- The standalone serial monitor proxy was removed. The supported temporary
  bridge keeps the S3 flashed as an ESP-NOW node and uses USB only as its motor
  transport.
