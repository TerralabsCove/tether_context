---
status: draft
owner: John Peng
last_reviewed: 2026-10-19
---

# ESP32-C5 antenna and RF plan for Tether (2026-10-19)

Written by John's AI agent from `truth/`, the tether_controls firmware, the tethersmall bring-up log, and
Espressif's ESP32-C5 documents. Not authoritative. Nothing here is measured on Tether hardware yet; the
test matrix at the end is what turns this into facts.

## Bottom line

1. **Run ESP-NOW on 5 GHz, channel 149–165 first choice, 36–48 second.** The losses measured on
   tethersmall came from other 2.4 GHz Wi-Fi, not from range. At demo-set distances both bands have more
   than 40 dB of margin, so giving up ~17 dB to move to 5 GHz is cheap, and it removes the interference.
   Stay off channels 52–144 (DFS radar channels: the C5 cannot run a SoftAP there and ESP-NOW has no
   business there either). Keep the 2.4 GHz channel-11 build as the fallback.
2. **One external dual-band antenna per ESP, on a connector, never the PCB-antenna module.** The chip has
   two RF ports (2.4 and 5 GHz) but the module joins them through a diplexer into **one** antenna. It is
   not two radios and not simultaneous dual band. The XIAO ESP32-C5 already ships this way: U.FL only,
   with a dual-band FPC antenna (A-01) in the box.
3. **Get every antenna out of the aluminum.** Mount it on a printed bracket on the outer face of the link,
   with at least 15 mm of clear air on all sides (Espressif's enclosure rule), and nothing metallic,
   no battery, no motor can, within that zone. This is what D-008 ("ESP antenna stays exposed at the
   top") already says; this note makes it concrete.
4. **Fix the master's antenna problem with placement and polarization, not power.** Put the offboard C5
   on a USB extension, 1.5–2.5 m up with a clear view down onto the set, at least 1 m from the nearest
   module, and give it a **right-hand circularly polarized 5.8 GHz antenna** (FPV cloverleaf type). The
   modules tumble through every orientation as the robot walks; a linear-to-linear link can lose 20 dB
   or more when they cross, a circular-to-linear link loses a fixed ~3 dB whatever the pose.
5. **Protect the connector.** U.FL is a 30-cycle, zero-strain connector. Use a short U.FL-to-SMA bulkhead
   pigtail, bolt the SMA into the bracket, and let the SMA carry the antenna. Never power the radio with
   the antenna unplugged; Espressif says that can damage the front end.
6. **Measure before locking any of this in.** The matrix at the end takes an afternoon with the existing
   `tethertests/espnow_latency` sketch.

## Where the project stands today

| Item | State | Source |
|---|---|---|
| Board | The 2026-10-16 plan says ESP32-C5 everywhere. The bench note and firmware still target XIAO ESP32-C6 and ESP32-S3; the C5 branch in `Config.h` and `radioBegin()` is written but commented out. | [one-pager note](2026-10-16-john-mvp-one-pager.md), [bench note](2026-10-12-irisy-embedded-controls-bench.md), tether_controls `firmware/tether_control_arduino` |
| Channel | Firmware: **channel 1**, 2.4 GHz, master runs a SoftAP the laptop joins, ESP-NOW on the same channel. tethersmall measured channel 1 losing 10–34 % to nearby Wi-Fi and channel 11 losing 0 %. | `Config.h` line 38; [robot.md](../truth/robot.md#tethersmall-testbed-2026-10-11) |
| Where loss happens | At the master's radio, not the slaves. Slaves heard each other ~100 %. Near-far: a slave at −21 dBm next to one at −55 dBm made the master drop the weaker one. | tethersmall `ESPNOW_BRINGUP.md` |
| What didn't help | 12 Mbit/s PHY rate (worse), lower TX power (much worse). | same |
| Antenna today | XIAO C3 U.FL whip; XIAO C6 on-board antenna via RF switch (GPIO3/GPIO14 in firmware). Nothing designed for the robot yet. | same; firmware `radioBegin()` |
| Structure | Milled aluminum links, batteries inside the links (6S LiPo per module), breadboard electronics per module (D-007). | [robot.md](../truth/robot.md), one-pager CAD |
| Master location | Conflict: one-pager puts the master at the offboard computer; D-026 and the bench note put it on the robot as node 0 with one motor. This note assumes an offboard master radio; if the master stays on the robot, section "If the master stays on the robot" applies. | [open question in one-pager note](2026-10-16-john-mvp-one-pager.md) |

## ESP32-C5 radio facts that matter here

Chip and module numbers are from the ESP32-C5 series datasheet and the ESP32-C5-WROOM-1/1U datasheet
v1.3, measured by Espressif at the antenna port. Software behaviour is from ESP-IDF v6.1 docs for the C5.

- **1T1R, one band at a time.** `WIFI_BAND_MODE_AUTO` means automatic selection, not both bands at once.
  All four nodes must sit on one band and one channel.
- **Two RF pins, one antenna.** The chip has `ANT_2G` and `ANT_5G`. Both WROOM variants put a dual-band
  diplexer in front of them, so the module has a single antenna port. WROOM-1 = PCB antenna. WROOM-1U =
  connector (Hirose U.FL / I-PEX MHF I / Amphenol AMC compatible) or the ANT2 pad.
- **"Antenna diversity"** on the C5 means an *external* RF switch between two antennas, driven by GPIOs
  you choose, with `esp_phy_set_ant_gpio()` / `esp_phy_set_ant()`. At most two antennas active.
  Espressif says automatic RX selection is "currently not recommended" because it can flap; fix the
  antenna or write your own selector. Optional for the master, not for the modules.
- **ESP-NOW on 5 GHz is documented.** The C5 ESP-NOW reference lists peer channels 36–177 for the 5 GHz
  band. ESP-NOW Long Range mode is **2.4 GHz only**, so there is no LR safety net on 5 GHz.
- **Band switch API.** `esp_wifi_set_band_mode(WIFI_BAND_MODE_5G_ONLY)` after `WiFi.mode()` and before
  `softAP()` / `esp_wifi_set_channel()`. If no channel is set after switching, the default is 36.
  Needs `CONFIG_SOC_WIFI_SUPPORT_5G` (IDF ≥ 5.4.2; the project is on IDF 6.1 / Arduino 4.0.0-RC1).
- **DFS.** Passive radar detection only. SoftAP is not allowed on DFS channels (52–144). Use 36–48 or
  149–165 in the US.
- **Rates.** There is no 802.11b on 5 GHz, so ESP-NOW's default 1 Mbit/s DSSS does not exist there; the
  base rate is 6 Mbit/s OFDM (or MCS0). Frames are shorter on air, which helps with four nodes on one
  channel. tethersmall found a faster rate hurt at 2.4 GHz; retest on 5 GHz rather than assume.
- **TX power (typical, module port).** 2.4 GHz: 19.0 dBm at 1 Mbit/s DSSS, 18.0 dBm at 6 Mbit/s OFDM.
  5 GHz: 16.5 dBm at 6 Mbit/s OFDM, 16.5 dBm at MCS0. `esp_wifi_set_max_tx_power()` takes 0.25 dBm units,
  range 8–84 (2–20 dBm); the PHY table caps what you actually get.
- **RX sensitivity (typical).** 2.4 GHz: −99.5 dBm at 1 Mbit/s, −94.0 dBm at 6 Mbit/s OFDM.
  5 GHz: −92.5 dBm at 6 Mbit/s and at MCS0.
- **Antenna rules from the datasheet.** Dual band, 50 Ω, gain no more than 3.86 dBi (2.4 GHz) / 3.65 dBi
  (5 GHz) to stay inside the module's certification. The certification antenna was a dual-band whip
  ("SY-WIFI-ESP-Dual Band Ant"). Operation without an antenna "may result in unstable behavior or
  potential damage to the RF circuit."
- **Placement rules from the hardware design guidelines.** Antenna outside or at the edge of any host
  board; at least **15 mm clearance in all directions inside a housing**; keep the antenna away from
  crystals, USB, UART lines and other high-frequency parts; keep all layers clear under the connector;
  test the finished product for range and throughput.
- **XIAO ESP32-C5 specifics.** 21 × 17.8 mm, U.FL connector tied to the chip's antenna path, ships with
  Seeed's A-01 FPC antenna rated 2400–2500 / 5100–5900 MHz, peak 2.8 dBi. No source checked shows an
  on-board antenna or an RF switch on this board, unlike the C6. **[assumed]** until someone looks at
  the Seeed schematic. D9/D10 are GPIO9/GPIO10 on the C5 (the firmware comments already note this).

## Link budget at demo-set range

Free-space, 10 m, 2 dBi antennas each end, no body shadowing. Enough to show where the margin is.

| | 2.4 GHz ch 11, 1 Mbit/s DSSS | 5 GHz ch 149, 6 Mbit/s OFDM |
|---|---|---|
| TX power (typ) | 19.0 dBm | 16.5 dBm |
| Path loss, 10 m | 60 dB | 68 dB |
| Received | ≈ −37 dBm | ≈ −47 dBm |
| Sensitivity | −99.5 dBm | −92.5 dBm |
| Margin | ≈ 62 dB | ≈ 45 dB |

The 5 GHz link gives up about 17 dB and still has 45 dB in hand. A cross-polarized pair (≈20 dB), a
link through the robot's own aluminum body (10–20 dB at 5 GHz), and a bad antenna mount (5–10 dB) can
stack up to eat most of that, which is why the recommendations below are about polarization and
placement rather than power. tethersmall's RSSI values (−21 to −55 dBm on a bench) are consistent with
this: the radio was never short of signal, it was short of clean air time.

## Recommendations in detail

### A. Band, channel, rate

- Build the C5 firmware with `WIFI_BAND_MODE_5G_ONLY` and a channel from 149–165 (UNII-3, non-DFS,
  5.745–5.825 GHz). Channels 36–48 are the backup set. Scan the venue first (a laptop Wi-Fi scan or the
  C5 scan example) and pick the emptiest 20 MHz channel; most home routers default to 36 or 149, so
  157 or 161 are often free.
- Why 149–165 over 36–48: the FPV ecosystem's 5.8 GHz antennas (5.5–6.0 GHz, cheap, SMA, circular
  polarization available) cover it; 36–48 needs a true dual-band or 5.2 GHz part.
- Keep the laptop off the robot's channel: the Mac's own Wi-Fi was on 6 GHz during tethersmall, keep it
  that way or on 2.4 GHz.
- Retest the ESP-NOW rate on 5 GHz: 6 Mbit/s OFDM vs MCS0. Keep "send every command twice" until the
  loss numbers say otherwise.
- The firmware's channel-1 default should change in any case. Even for the 2.4 GHz fallback build it
  should be 11 (or whatever the venue scan says), per the tethersmall measurement.

### B. Boards and antennas

| Node | Board | Antenna | Mount |
|---|---|---|---|
| Robot modules ×3 | XIAO ESP32-C5 (U.FL) or a WROOM-1U carrier | Dual-band 2.4/5 GHz omni whip or a 5.8 GHz FPV linear whip, ≤ 3.65 dBi, 50 Ω, SMA. The bundled A-01 FPC is fine for the first bench test but it is a sticker that needs a flat non-metal surface and will not survive the robot. | U.FL-to-SMA bulkhead pigtail, ≤ 100 mm, SMA bolted through a printed bracket on the link's outer face |
| Master (offboard) | Same board | RHCP 5.8 GHz cloverleaf / skew-planar, 5.5–6.0 GHz, ~1.3 dBic | SMA-to-U.FL pigtail; antenna on a short mast at 1.5–2.5 m |
| Master, optional later | Same board + external 2-way RF switch | Two antennas at 90° (or RHCP + linear) | Only if the matrix below shows polarization fades the CP antenna doesn't cure |

Do not use the WROOM-1 (PCB antenna) variant anywhere on the robot. A PCB antenna needs the host board
as its ground plane and a free edge, and it ends up inside the aluminum with the battery.

Cable loss on 1.13 mm or 1.37 mm micro-coax is roughly 2–3 dB per metre at 5.8 GHz; a 100 mm pigtail
costs well under 0.5 dB. Longer runs, say to get the master antenna up a mast, should be RG-316 or
better (≈1 dB/m at 5.8 GHz) or just put the whole master board at the top of the mast on the USB
extension, which is simpler.

### C. Antenna placement on each module

- Outer face of the link in the "straighter but offset" layout (D-002), at the end of the link away from
  the motor can and away from the battery cavity. Each of the three modules gets the same bracket.
- 15 mm minimum air gap to any metal, battery, or motor in every direction (Espressif). Prefer 26 mm
  (half a wavelength at 5.8 GHz) where the CAD allows it.
- Whip vertical in the robot's nominal standing pose. Across a step the module will roll through every
  angle anyway, which is what the master's circular antenna is for.
- Keep the pigtail and the ESP's CAN leads away from the motor phase leads and the LiPo leads; tie the
  pigtail down so it cannot flex at the U.FL end.
- Nothing on the robot should sit between a module's antenna and the sky on the master's side. In the
  CAD, check each of the three antenna positions against the robot's main poses (standing, mid-step,
  anchored on a bar) for line of sight to a master mounted above the set.
- The breadboard (D-007) can stay inside the link; only the antenna has to be outside.

### D. Master placement

- Offboard C5 on a 2–3 m USB extension, not plugged into the Mac. tethersmall lost frames at the
  master's radio and listed "away from the Mac and its Bluetooth, with a clear line to the robot, an
  external antenna" as the next things to try. This is that.
- Height 1.5–2.5 m, looking down onto the set, so that the robot's own body is never between the master
  and a module. The set itself (bars) should not have large metal panels between master and robot.
- At least 1 m from the nearest module and roughly equal distance to all three, to avoid the near-far
  capture that tethersmall saw at −21 dBm vs −55 dBm.
- The laptop still joins the master's SoftAP for UDP control. On 5 GHz that SoftAP must be on a
  non-DFS channel, which the channel choice above already guarantees. Worth testing whether moving the
  laptop link to USB serial (as tethersmall did) frees enough air time to reduce ESP-NOW loss; that is a
  design question for Trent and Jason, not an antenna question.

### E. If the master stays on the robot (D-026 reading)

Then node 0's antenna follows section C like the others, the laptop-side radio is just a SoftAP client,
and the near-far problem moves on-robot: two modules a few centimetres from node 0 and one 60 cm away.
Lower the TX power on the near modules by a few dB (`esp_wifi_set_max_tx_power`) once the RSSI spread is
measured, rather than lowering it everywhere (tethersmall: global power reduction made loss worse).

### F. Firmware knobs to set at the same time

- `WiFi.setBandMode(WIFI_BAND_MODE_5G_ONLY)` right after `WiFi.mode()` on master and nodes (the
  commented-out lines in `radioBegin()` are already in the right place).
- `TETHER_ESPNOW_CHANNEL` 149 (or the scanned winner) on every build; the SoftAP and ESP-NOW share it.
- `esp_wifi_set_max_tx_power(84)` after `esp_wifi_start()`; the PHY table will hold it at the real
  5 GHz maximum. Confirm with `esp_wifi_get_max_tx_power()` in the radio-state print.
- `esp_now_set_peer_rate_config()` per peer: 6 Mbit/s OFDM first, MCS0 as the comparison.
- Remove the C6 RF-switch GPIO writes from the C5 build (GPIO3/GPIO14 mean other things on the C5).
- Log RSSI per packet on both ends (the node already has `packet.rssi`), so the matrix below gets numbers.

## Test matrix (do this before buying brackets)

Use `tethertests/espnow_latency` (already supports XIAO and reports MAC) between one master C5 and
three node C5s, 50 Hz command + 200 Hz state like tethersmall, 60 s per cell, log delivery %, RTT p50/p95,
RSSI both ways. Same place, same time of day.

| # | Vary | Cells |
|---|---|---|
| 1 | Band / channel | 2.4 ch 11 · 5 GHz ch 36 · 5 GHz ch 149 (or scanned winner) |
| 2 | Rate on the winning 5 GHz channel | 6 Mbit/s · MCS0 · 12 Mbit/s |
| 3 | Node antenna | A-01 FPC · dual-band whip · 5.8 GHz whip |
| 4 | Node mount | whip in free air · whip 15 mm off an aluminum link with battery inside · ESP + FPC inside the link (the "do nothing" case, expect it to fail) |
| 5 | Orientation | node whip vertical · horizontal · pointing at master, with master linear, then master RHCP |
| 6 | Master position | on the Mac · USB extension at desk height · 2 m up looking down |
| 7 | Node count | 1 · 2 · 3 nodes streaming (open question 15) |

Promotion rule: whatever wins cells 1–6 becomes a **[verified]** row in `truth/robot.md` with the log
path, and D-019 gets a successor decision naming the band and channel.

## Conflicts and open items to flag

- **C5 vs C6.** `truth/` and the bench note assume XIAO ESP32-C6 for the final modules; the 2026-10-16
  plan and this note assume C5. Needs a decision row.
- **Master on robot vs offboard.** Already flagged in the one-pager note; it changes section D vs E.
- **Firmware channel 1** contradicts the tethersmall channel-11 finding, independent of the 5 GHz move.
- **Antenna gain and certification.** Over 3.65 dBi on 5 GHz leaves the module's certification. Irrelevant
  for a lab demo, relevant if the project ever ships.
- **Open question 14** (is ESP-NOW's margin enough) and **15** (three nodes on one channel) are what the
  test matrix answers.

## Sources

- ESP32-C5 series datasheet (Espressif): `ANT_2G` / `ANT_5G` pins, 1T1R, antenna diversity via external
  switch. https://documentation.espressif.com/esp32-c5_datasheet_en.pdf
- ESP32-C5-WROOM-1 / 1U datasheet v1.3: diplexer, connector types, TX power and RX sensitivity tables,
  antenna requirements, placement pointer. https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf
- ESP-IDF v6.1 (ESP32-C5) Wi-Fi driver overview: band mode, DFS, LR mode 2.4 GHz only.
  https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c5/api-guides/wifi-driver/overview.html
- ESP-IDF v6.1 (ESP32-C5) ESP-NOW reference: 5 GHz peer channels, rate config, peer limits.
  https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c5/api-reference/network/esp_now.html
- ESP-IDF v6.1 (ESP32-C5) Wi-Fi API: `esp_wifi_set_band_mode`, `esp_wifi_set_max_tx_power`, protocols.
  https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c5/api-reference/network/esp_wifi.html
- ESP-IDF v6.1 (ESP32-C5) PHY guide: multiple-antenna switch API and its limits.
  https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c5/api-guides/phy.html
- ESP32-C5 hardware design guidelines, PCB layout: 15 mm housing clearance, keep-outs.
  https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/pcb-layout-design.html
- ESP32-C5 hardware design guidelines, schematic checklist: separate 2G/5G matching, duplexer.
  https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html
- Seeed XIAO ESP32-C5 getting started (U.FL, pinout) and Wi-Fi usage (band-mode calls).
  https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/ , https://wiki.seeedstudio.com/xiao_esp32c5_wifi_usage/
- Zephyr board page for XIAO ESP32-C5 (module and U.FL). https://docs.zephyrproject.org/latest/boards/seeed/xiao_esp32c5/doc/index.html
- A-01 vs A-02 antenna note (A-01 dual band 2400–2500 / 5100–5900 MHz, 2.8 dBi).
  https://www.unmannedtechshop.co.uk/de/blogs/knowledge-base/xiao-fpc-antenna-a01-vs-a02-esp32-c3-c5-s3
- Third-party first looks (U.FL only, don't run without antenna): https://tech.scargill.net/seeed-studio-xiao-esp32-c5-first-look/ ,
  https://dronebotworkshop.com/xiao-esp32-c5/
- Waveshare ESP32-C5-WIFI6-KIT (WROOM-1 based, PCB or external antenna variants, LiPo charger).
  https://docs.waveshare.com/ESP32-C5-WIFI6-KIT
- tethersmall `docs/ESPNOW_BRINGUP.md` (channel, near-far, rate and power findings); tether_controls
  `firmware/tether_control_arduino/{Config.h,tether_control_arduino.ino}` (channel 1, C5 migration stubs).
