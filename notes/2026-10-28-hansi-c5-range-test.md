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

## Repeatability at 3 m, no wall: three back-to-back runs [verified]

Same setup, 30 s each, run one after another. Raw output: the "3 m repeat" sections of
[link-check.log](2026-10-28-hansi-c5-range-test/link-check.log).

| run | motor | acked | RTT p50 / p95 / max (ms) | state age p50 / p95 (ms) | RSSI (dBm) | status reports received |
|---|---|---|---|---|---|---|
| 1 | 0x02 | 1386/1391 (99.6 %) | 12.3 / 19.3 / 28.0 | 7 / 15 | −49 to −51 | 199.7 /s |
| 1 | 0x04 | 1385/1391 (99.6 %) | 12.4 / 19.5 / 28.0 | 7 / 15 | −62 to −64 | 198.5 /s |
| 1 | 0x06 | 1385/1391 (99.6 %) | 12.4 / 19.5 / 27.9 | 8 / 15 | −47 to −51 | 199.8 /s |
| 2 | 0x02 | 1380/1390 (99.3 %) | 12.3 / 19.2 / 24.2 | 8 / 15 | −52 to −53 | 199.8 /s |
| 2 | 0x04 | 1380/1390 (99.3 %) | 12.3 / 19.3 / 25.3 | 7 / 14 | −62 to −63 | 199.0 /s |
| 2 | 0x06 | 1379/1390 (99.2 %) | 12.3 / 19.5 / 23.8 | 8 / 15 | −48 to −49 | 199.8 /s |
| 3 | 0x02 | 1361/1386 (98.2 %) | 12.6 / 19.4 / 28.0 | 8 / 14 | −54 | 198.9 /s |
| 3 | 0x04 | 1361/1386 (98.2 %) | 12.4 / 19.3 / 34.5 | 8 / 14 | −62 to −64 | 196.4 /s |
| 3 | 0x06 | 1361/1386 (98.2 %) | 12.5 / 19.4 / 27.9 | 8 / 14 | −47 to −49 | 199.3 /s |

- **RTT is very consistent:** p50 12.3–12.6 ms and p95 19.2–19.5 ms across all nine motor-runs (spread 0.3 ms).
  The max varies more, 23.8–34.5 ms, as single outliers do.
- **Ack rate varies most:** 99.6 %, 99.3 % and 98.2 %. In each run all three motors lost the same number of
  commands (±1). That points to losses before the commands split per motor (laptop → gateway USB, or the
  gateway's send), not on one radio path. [assumed: not traced]
- **Status reports:** 196–200 /s per motor, so at most 2 % lost on the slave → gateway path.
- **RSSI is stable within this session** (±3 dB per motor), but differs from the earlier 3 m run in the table above:
  0x06 went from −54/−55 to −47/−51 dBm and 0x04 from −54/−57 to −62/−64. The setup was not re-measured between
  sessions, so the laptop's exact position or angle likely differed.

## Findings

- **Latency does not depend on range here [verified]:** RTT p50 stayed at 12–13 ms and p95 at 19–22 ms from the
  bench to 5–6 m through a wall. All of it is inside the policy's trained range (about 6–70 ms). This matches the
  S3-gateway runs on 2026-10-19 (p95 20–26 ms).
- **Range shows up as signal and lost frames, not delay [verified]:** at 5–6 m through a wall, 0x04 is at
  −82 dBm and 0x06 dipped to −88 dBm, close to the C5's 5 GHz sensitivity (−92.5 dBm typical, per the
  [RF plan](2026-10-19-john-esp32c5-antenna-rf-plan.md)). 5–10 % of their status reports were lost.
- **0x04 is the weakest radio in every test [verified]:** 4–19 dB below 0x02, including on the bench. 0x06 was
  12–21 dB below 0x02 on the bench, 6–24 dB below through the wall, about 5 dB below at the first 3 m test, and
  0–7 dB *above* 0x02 in the three repeat runs. So 0x06's gap depends on position; 0x04's does not go away. The cause is
  not known (see below).
- **Recommendation [assumed]:** keep the gateway within about 3 m with line of sight for policy runs. 5–6 m through
  a wall works for a check, but leaves little margin for 0x04 and 0x06.

## Why 0x04 and 0x06 are weaker [assumed, not tested]

The gap is already there on the bench, so it is not distance. 0x06 matching 0x02 in the repeat runs fits
orientation or placement (cause 1 or 2) for 0x06; 0x04 staying weak in every position points more toward its
antenna, cable or mount (cause 2 or 3). Since RSSI is measured at the gateway, the gateway's
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

## Dry checks before a hardware run (no arm motion) [verified]

Run in [tethersmall](https://github.com/TerralabsCove/tethersmall) `e4f6095` after the link tests. Raw output:
[dry-checks.log](2026-10-28-hansi-c5-range-test/dry-checks.log).

| check | result |
|---|---|
| `calibrate.py show`, straight-line and stand-up configs (listens only) | All three motors report, steady for 5 s. Both configs hold the same 2026-10-19 calibration; the arm reads +1.2 / +1.0 / +4.1° (0x02 / 0x04 / 0x06). |
| Straight-line runner, simulator, wireless link | Straight, settled 2.00 s, path deviation 6.7° (pass ≤ 8.6°). |
| Stand-up runner, simulator, `--controller ramp` | Straight, settled 2.18 s, path deviation 2.9° (pass). |
| Stand-up runner, simulator, RL policy | Straight, settled 1.56 s, path deviation 11.1° (**fails** coordination). Consistent with the policy's 86 % coordinated rate in tethersmall `docs/STANDUP.md`, which recommends the ramp. |
| tethersmall pytest | 70 passed. |

The calibration was measured with the C6 boards. It should still hold, because the angles come from the motors'
encoders and the motors did not change. [assumed]
