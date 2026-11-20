---
status: draft
owner: John Peng
last_reviewed: 2026-11-19
---

# reCamera to XIAO ESP32-C5: how to get the tag strings onto ESP-NOW (2026-11-19)

Written by John's AI agent from the published schematics and the project's own logs. Not authoritative. Nothing here
is tested on hardware. It is input to [open question 7](../truth/open-questions.md) (camera data path). Nothing
here changes `truth/`.

Sources read: Seeed's reCamera 2002 KiCad and PDF schematics
([OSHW-reCamera-Series](https://github.com/Seeed-Studio/OSHW-reCamera-Series), B101 base board v1.2 and C1-2002w
core board v1.2), the reCamera 2002 and XIAO ESP32-C5 wiki pages (from Seeed's
[wiki source](https://github.com/Seeed-Studio/wiki-documents)), the tethersmall C5 firmware, and the tagstream
logs in [tether_camera](https://github.com/TerralabsCove/tether_camera). The XIAO ESP32-C5 schematic PDF itself
could not be downloaded in this session, so the C5 pin facts come from Seeed's pin map, not the schematic.

## Bottom line

1. **Only one wired option works with the stock camera: its UART0, the Linux debug console.** On the 2002W, it
   is the only data port the base board brings out besides USB and Ethernet. It sits on two test pads, not a
   connector.
2. **Wire camera TX to the C5's D7 (GPIO12, RX), plus a ground.** That is one signal wire. Both sides use 3.3 V
   logic, so no level shifter is needed. D6/D7 are the C5's UART pins and are unused in the tethersmall C5
   firmware (tether_controls was not checked).
   Run the C5's second UART (`Serial1`) on them. CAN stays on D9/D10.
3. **Run the UART at 460800 or 921600 baud, not 115200.** The current JSON lines are about 175 bytes. Eight
   tags at 27 fps need about 380 kbaud. 115200 only covers one or two tags.
4. **Have the C5 send one ESP-NOW frame per camera frame, not one per tag line.** One JSON line fits a 250-byte
   ESP-NOW v1 frame, but eight do not. Either shorten the record (about 16 bytes per tag in binary) or use
   ESP-NOW v2 frames (up to 1470 bytes).
5. **Three risks to handle first:** the camera's TX pin also sets how it boots, the port is also the login
   console, and the wire has to cross the end-effector slip ring. See [Risks](#risks).
6. **USB, I2C and SPI do not work without new hardware.** Details are in [Ruled out](#ruled-out).

## The camera side (reCamera 2002W, B101 base board)

The 2002W is a C1-2002w core board (Sophgo SG2002) on a B101 base board. They connect through two 60-pin
board-to-board connectors.

| Signal | Where | Use for this link |
|---|---|---|
| UART0 TX (`DEBUG_UART0_TX`) | Test pad **TP1** on the base board | **Yes.** Camera to C5 data |
| UART0 RX (`DEBUG_UART0_RX`) | Test pad **TP2** | Only if the C5 has to send to the camera. See risks |
| GND | Test pad **TP6** | **Yes** |
| +5 V (after the 2 A fuse) | Test pad TP8 | Power can also come in here instead of the USB-C cable |
| USB D−/D+ | TP4 / TP5 | No (see [Ruled out](#ruled-out)) |
| UART1 (`BT_UART1_*`) | Board-to-board connector | No. On the 2002W it goes to the Wi-Fi/Bluetooth module. The 0 Ω links that would pass it to the base board are not fitted |
| I2C1, I2C2, PWM, GPIO (`MIPI_TX*` pins) | Board-to-board connector only | No. The B101 does not route them anywhere |
| SDIO1 (`SD1_*`) | Board-to-board connector only | No. Not routed on the B101, and not fitted on the 2002W core |

Seeed's wiki says the same in words: "The base circuit board of the recamera has three contacts tx, rx, and gnd,
which serve as the debug serial port … baud rate of 115200 and can log into the recamera system."

Electrical details, from the core board schematic (v1.2, dated 2024-10-14):

- The UART0 pins are in the `VDDIO_SD0_EMMC` power domain. On this revision that domain is tied to **3.3 V**
  (R83 fitted to +3V3; R84 to +1V8 not fitted). **[assumed]** for our 64 GB units until measured. The schematic
  is for the 8 GB board. Check with a meter: TP1 should idle at about 3.3 V.
- Each UART0 line has a 100 Ω series resistor and a 4.7 kΩ pull-up on the core board.
- **UART0 TX is a boot strap.** The schematic note says: pulled up means normal boot, pulled down means "ROM Fail
  Mode". Whatever is wired to TP1 must not hold it low while the camera powers up.

## The ESP side (Seeed XIAO ESP32-C5)

Pin map from Seeed's wiki, with what the C5 firmware already uses (tethersmall `platformio.ini`, envs `*_c5_5g`):

| XIAO pin | GPIO | Notes | Taken? |
|---|---|---|---|
| D0 | GPIO1 | LP GPIO, ADC | Free |
| D1 | GPIO0 | LP GPIO | Free |
| D2 | GPIO25 | **Strapping pin** | Free, but avoid as a camera input |
| D3 | GPIO7 | **Strapping pin** | Free, but avoid as a camera input |
| D4 / D5 | GPIO23 / GPIO24 | I2C SDA / SCL by default | Free |
| **D6** | **GPIO11** | **UART TX** by default | **Free** |
| **D7** | **GPIO12** | **UART RX** by default | **Free** |
| D8 | GPIO8 | SPI SCK by default | Free |
| D9 / D10 | GPIO9 / GPIO10 | SPI MISO / MOSI by default | **CAN TX / RX** to the SN65HVD230 |

- The C5 has two UARTs (plus a low-power one) and native USB serial. The firmware builds with
  `ARDUINO_USB_CDC_ON_BOOT=1`, so `Serial` is USB and the hardware UART on D6/D7 is free. Seeed's own example opens
  it as `Serial1.begin(baud, SERIAL_8N1, D7, D6)`.
- Any free GPIO can be the UART pin through the GPIO matrix. D6/D7 are the default, and keep the strapping pins
  (D2, D3) out of the camera's reach.
- The C5's ROM prints its boot log on GPIO11 (D6). If D6 is wired to the camera's RX, that log lands in the
  camera's login console. Another reason to leave D6 unconnected.

## Wiring (recommended)

```
reCamera B101                     XIAO ESP32-C5 (module ESP)
  TP1  UART0_TX  ───────────────>  D7  GPIO12  (Serial1 RX)
  TP6  GND       ────────────────  GND
  TP2  UART0_RX     (leave open)   D6  GPIO11  (leave open)
```

One way only: the camera talks and the C5 listens. The C5 never transmits into the camera's console.

If the C5 must send to the camera later (for example, "start" or "change tag size"), add D6 to TP2. Do that only
after the camera's login console on that port is turned off (see risks).

## Data rate: will it fit?

Measured from the tagstream logs in tether_camera (33,923 tag lines from the 11-13 and 11-14 runs, `mac_t` field
removed): a tag line averages **174 bytes**. A heartbeat line is about 113 bytes, once a second. Rates are from the
[scaler capture note](2026-11-14-john-recamera-scaler-capture.md).

UART at 8N1 sends 10 bits per byte.

| Case | Lines/s | Bytes/s | Baud needed | Time on the wire per line at 115200 / 921600 |
|---|---|---|---|---|
| 1 tag, 21.6 Hz (measured) | 22 | 3.8 k | 38 k | 15 ms / 1.9 ms |
| 8 tags, 11.7 Hz each (measured) | 94 | 16.4 k | 164 k | same per line |
| 8 tags at the full 27 fps (ceiling) | 216 | 37.6 k | 376 k | same per line |

- **115200 works for one or two tags and is too slow for eight.** It also adds 15 ms per line, about as much as
  the camera's own 14 ms. Eight lines back to back take about 120 ms.
- **460800 or 921600 covers every case.** The SG2002 UART is expected to manage these speeds (the reCamera Pro
  runs its console at 1.5 Mbaud), but nobody has tried it on our camera. **[assumed]** The C5 handles them.
- Shortening the record helps everywhere. Binary with id, x/y/z in 0.1 mm and roll/pitch/yaw in 0.01° as 16-bit
  numbers, plus a frame count and age, is about 16 bytes per tag. Eight tags at 27 fps is then about 3.5 kB/s,
  which fits 115200 easily. The cost: you can no longer read the stream by eye.

### ESP-NOW frame size and air time

- An ESP-NOW v1 frame carries 250 bytes. One JSON line fits, and two do not.
- ESP-NOW v2 carries up to 1470 bytes (about 1450 usable), on ESP-IDF 5.4.2 or later. Both ends must run v2 to
  get the large frames. A v1 receiver still gets frames up to 250 bytes. The project is on IDF 6.1 / Arduino
  4.0, so v2 should be available; check `ESP_NOW_MAX_DATA_LEN_V2` in the build.
- Sending one ESP-NOW frame per tag line would add up to 216 frames/s per camera, 432 for two. The channel
  already carries about 700 frames/s (commands at 50 Hz sent twice, and 200 Hz state from three nodes). That
  roughly doubles the frame count on air. Batching all tags from one camera frame into one ESP-NOW frame keeps
  it to 27 frames/s per camera. At 6 Mbit/s that is about 0.3 ms of air time each, under 2 % of the channel for
  both cameras. **[assumed]** Calculated, not measured.
- The tethersmall frame format (`A5 5A len type payload crc8`) has a 1-byte length and a 37-byte frame limit. A
  camera frame type needs its own, larger limit (or a 2-byte length if it goes over 255 bytes).

## How the pieces would work

1. **Camera:** tagstream gains a serial output. It opens `/dev/ttyS0`, sets the baud, and writes one framed
   packet per camera frame: sync bytes, length, camera ID, frame count, the tag records, and a CRC. It keeps the
   UDP output for bench work. This code goes in tether_camera.
2. **Module C5:** a UART task reads `Serial1`, finds the sync bytes, checks the CRC, and passes the packet to
   `esp_now_send` unchanged. It does not parse JSON. Motor control keeps priority, and camera packets are
   dropped, not queued, if the radio is busy.
3. **Receiving ESP (the USB gateway on the laptop):** it adds the new frame type to what it forwards over USB.
   The laptop decodes it.

The framing matters because the camera's boot log comes out of the same pin at 115200 before tagstream starts.
The C5 sees noise until then and has to skip it.

## Risks

1. **Boot strap on TP1.** If the C5 is unpowered when the camera boots, the C5's input protection can pull TP1
   low and the camera can stop in ROM fail mode. Feed both from the same 5 V rail so they power up together. Then
   test a camera boot with the C5 unpowered to see whether this happens. If it does, add a buffer powered from
   the camera's side. **[assumed]** Read from the schematic, not observed.
2. **The port is the login console.** U-Boot, the kernel and a login prompt all use UART0. For data:
   - Turn off the login service on `ttyS0`.
   - Set the kernel message level low (`dmesg -n 1`) so kernel messages don't land in the middle of tag data.
   - Leave the boot log alone. The C5 skips it.
   Once this is done, the debug console is gone. Reach the camera over USB (192.168.42.1) or Wi-Fi instead.
3. **Slip ring.** The camera is on the far side of the end-effector slip ring ([D-039](../truth/decisions.md),
   [D-044](../truth/decisions.md)), and the ESP is on the big motor side ([D-033](../truth/decisions.md)). So
   the TX wire uses one of the slip ring's two or more vacant channels. With 5 V, GND and two servo signals,
   that leaves one channel spare, or none if the C5 also has to transmit. Signals through this slip ring are
   untested ([open question 3](../truth/open-questions.md)). A lower baud is more forgiving of a noisy contact,
   which is another reason to shorten the record. The 5 V channel also carries the camera's up to 1 A (5 V 1 A
   rating) on top of the servos ([open question 20](../truth/open-questions.md)).
4. **Test pads, not a connector.** Wires soldered to TP1, TP2 and TP6 need strain relief inside the camera's
   aluminum frame. Check how the leads leave the housing.
5. **Not our board revision.** The schematics are for the 8 GB v1.2 core and the B101 v1.2 base. Check the
   board markings on our units.

## Alternatives

| Option | What it is | Verdict |
|---|---|---|
| **A. Camera UART to the module's C5** (above) | One wire through the slip ring, no new radio | **Recommended to try first** |
| B. A dedicated XIAO C5 next to the camera | Camera UART to its own C5 on the claw side, which sends ESP-NOW itself. The slip ring carries only power | Use this if the slip ring channel is not available or not clean. It adds two radios to the channel (one per end), which is [open question 15](../truth/open-questions.md), and needs an antenna outside the aluminum on a rotating part. It is the "extra ESPs" fallback already raised |
| C. Camera Wi-Fi to the C5 | The camera joins a SoftAP on the C5 and sends UDP. The camera's Wi-Fi does 5 GHz as a station | Not recommended. It puts a Wi-Fi station's traffic on the motor channel and makes the C5 run a SoftAP and ESP-NOW together. tethersmall measured that setup as slower and less reliable ([run logs](2026-10-20-hansi-straightline-run-logs.md)) |
| D. Camera Wi-Fi straight to the laptop | No ESP involved | Already listed under open question 7. Outside this question |

## Ruled out

- **USB.** The XIAO C5's USB is a device port (USB serial/JTAG). The camera's USB-C is also a device port (power
  and USB networking). Two devices cannot talk to each other. **[assumed]** for the C5 having no USB host, from
  Espressif's chip description, not rechecked here.
- **I2C or SPI.** The SG2002's I2C and SPI-capable pins reach the board-to-board connector but go nowhere on the
  B101. A custom base board could bring them out. The B101 is open source in KiCad, so that is possible later,
  but it is new hardware.
- **UART1.** On the 2002W, it is wired to the Wi-Fi/Bluetooth module.

## Bench test (one afternoon)

1. Check the board revision and measure TP1 idle voltage (expect about 3.3 V).
2. Solder TP1 and TP6. Read the camera's boot log on the C5's `Serial1` at 115200, echoed to USB. This proves the
   wiring.
3. Boot the camera with the C5 unpowered. Confirm it still boots (risk 1).
4. Turn off the console login. Have tagstream write to `/dev/ttyS0` at 460800, then 921600. Count lost and bad
   packets on the C5 over 10 minutes with eight tags.
5. Forward the packets over ESP-NOW to the USB gateway while the motors run the damped link check. Check whether
   motor RTT p95 changes from the [range test](2026-10-28-hansi-c5-range-test.md) numbers.
6. Repeat step 4 through the slip ring while it turns.
