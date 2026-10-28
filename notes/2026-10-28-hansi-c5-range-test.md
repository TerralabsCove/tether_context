---
status: draft
owner: Hansi Lee
last_reviewed: 2026-10-28
---

# tethersmall all-C5 arm: link range test (2026-10-28)

Written by Hansi's AI agent from the test session. Not authoritative. Follows the
[2026-10-20 run logs](2026-10-20-hansi-straightline-run-logs.md), which used XIAO C6 slaves and an S3 gateway.

## Setup [as built]

- Laptop → XIAO ESP32-C5 USB gateway (board 10, COM20) → ESP-NOW, 5 GHz channel 36 → three XIAO C5 slaves.
  Firmware envs `*_c5_5g` in [tethersmall](https://github.com/TerralabsCove/tethersmall) `e4f6095`.
- Each slave drives one Damiao motor through a Waveshare SN65HVD230 transceiver (TXD → D9, RXD → D10):
  board 11 → 0x02 (base), board 12 → 0x04 (middle), board 13 → 0x06 (top). Wiring:
  tethersmall `C5_WAVESHARE_WIRING.svg`.
- Every board has a dual-band U.FL antenna. Without antennas the link did not come up at all.
- The laptop was on battery for the 3 m and 5–6 m tests.
- Test: tethersmall `deploy/straightline/link_check.py --port COM20 --seconds 30`. It sends damping-only commands
  (kp 0, kd 1.5) at 50 Hz, so the motors do not move. RSSI is measured at the gateway. Status reports are the slaves'
  200 Hz STATE frames that reached the gateway.

## Bring-up fault (resolved)

Board 11 went CAN bus-off (`tx_err 256 rx_err 0`, nothing heard) and 0x02 showed a red LED while 0x04 and 0x06 were
green. A second transceiver changed nothing. The cause was a wrong wire between board 11 and its transceiver. After
the fix, 0x02 reported status 0x00.

## Results [verified]

Raw output: [link-check.log](2026-10-28-hansi-c5-range-test/link-check.log). Status reports received are the change in `rx_state_*` over the 30 s, divided by 30.

| distance | motor | acked | RTT p50 / p95 / max (ms) | state age p50 / p95 (ms) | RSSI (dBm) | status reports received |
|---|---|---|---|---|---|---|
| bench, 10 s | 0x02 | 461/462 | 12.4 / 19.5 / 23.1 | 8 / 14 | −19 to −24 | 200 /s |
| bench, 10 s | 0x04 | 461/462 | 12.2 / 19.2 / 25.3 | 8 / 14 | −37 to −38 | 200 /s |
| bench, 10 s | 0x06 | 461/462 | 12.0 / 18.7 / 22.3 | 8 / 14 | −36 to −40 | 200 /s |
| 3 m, open, 30 s | 0x02 | 1383/1400 | 12.3 / 19.4 / 24.3 | 7 / 14 | −48 to −50 | ≈200 /s |
| 3 m, open, 30 s | 0x04 | 1383/1400 | 12.3 / 19.4 / 28.6 | 8 / 15 | −54 to −57 | ≈200 /s |
| 3 m, open, 30 s | 0x06 | 1383/1400 | 12.4 / 19.5 / 39.3 | 7 / 14 | −54 to −55 | ≈200 /s |
| 5–6 m, one wall, 30 s | 0x02 | 1377/1395 | 12.8 / 19.9 / 29.3 | 8 / 14 | −64 to −67 | 195 /s (≈98 %) |
| 5–6 m, one wall, 30 s | 0x04 | 1370/1395 | 13.0 / 21.6 / 33.3 | 8 / 15 | −81 to −82 | 181 /s (≈90 %) |
| 5–6 m, one wall, 30 s | 0x06 | 1375/1395 | 12.6 / 19.9 / 29.8 | 8 / 14 | −73 to −88 | 189 /s (≈95 %) |

The gateway reported no bad frames in any test. Its queue-drop and short-USB-write counters only rose while no
program had the port open, never during a test.

## Findings

- **Latency does not depend on range here [verified]:** RTT p50 stayed at 12–13 ms and p95 at 19–22 ms from the
  bench to 5–6 m through a wall. All of it is inside the policy's trained range (about 6–70 ms). This matches the
  S3-gateway runs on 2026-10-19 (p95 20–26 ms).
- **Range shows up as signal and lost frames, not delay [verified]:** at 5–6 m through a wall, 0x04 is at
  −82 dBm and 0x06 dipped to −88 dBm, close to the C5's 5 GHz sensitivity (−92.5 dBm typical, per the
  [RF plan](2026-10-19-john-esp32c5-antenna-rf-plan.md)). 5–10 % of their status reports were lost.
- **0x04 and 0x06 are 13–18 dB weaker than 0x02 at every distance [verified],** including on the bench. The cause
  is not known (see below).
- **Recommendation [assumed]:** keep the gateway within about 3 m with line of sight for policy runs. 5–6 m through
  a wall works for a check, but leaves little margin for 0x04 and 0x06.

## Why 0x04 and 0x06 are weaker [assumed, not tested]

The gap is already there on the bench, so it is not distance. Since RSSI is measured at the gateway, the gateway's
own antenna affects all three equally. The difference is on the slave side. Likely causes, in order:

1. **Antenna orientation.** The FPC antennas are flat. Seen edge-on, or with their long axis pointing at the
   gateway, they can lose 10–20 dB. 0x06's swing from −73 to −88 dBm in one run also fits orientation and
   multipath.
2. **Metal nearby.** An antenna stuck to or close to a motor can, a mount or the aluminum link detunes it and
   blocks one side. The RF plan asks for at least 15 mm of clear air.
3. **A poorly seated U.FL connector or a damaged cable.** U.FL connectors are fragile and easy to half-seat.
4. **Board-to-board variation.** Least likely to account for 15 dB on its own.

To tell these apart: swap the antenna between board 11 and board 12. If the weak signal moves with the antenna,
the antenna or its cable is the cause. If it stays with board 12, the placement is. Then rotate the antennas of
boards 12 and 13 one at a time while watching RSSI in `link_check.py --listen 30`.
