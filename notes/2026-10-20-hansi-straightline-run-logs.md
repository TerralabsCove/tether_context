---
status: draft
owner: Hansi Lee
last_reviewed: 2026-10-20
---

# tethersmall straight-line arm: hardware run logs and link statistics (2026-10-19 to 2026-10-20)

Written by Hansi's AI agent from the test sessions. Not authoritative. Raw data is in
[2026-10-20-hansi-straightline-run-logs/](2026-10-20-hansi-straightline-run-logs/), because the runner writes its logs to
`deploy/straightline/logs/` in [tethersmall](https://github.com/TerralabsCove/tethersmall), which is gitignored.

## What was tested

A 3-motor straight-line arm (Damiao motors A base, B middle, C top, one XIAO ESP32-C6 per motor). The RL policy
`deploy/straightline/policy.npz` drives the arm from a bent pose to straight. Each run is 325 ticks (6.5 s at 50 Hz).
A run passes when every joint ends within 2.9° of straight and the arm stays within 8.6° of the straight
joint-space path.

Two control links were used:

- **USB gateway** (2026-10-19, arm lying flat): laptop → ESP32-S3 gateway on USB (COM18) → ESP-NOW → three slave C6s.
- **Wi-Fi** (2026-10-19 night and 2026-10-20, arm standing): laptop → Wi-Fi SoftAP on the middle C6 (B, master,
  `udp:192.168.4.1:4210`) → ESP-NOW → A and C. B drives its own motor directly. PR
  [tethersmall#4](https://github.com/TerralabsCove/tethersmall/pull/4).

## Results per run [verified]

RTT is command → motor state round trip, measured by the runner per motor. The trained policy assumes act 4–40 ms
plus obs 2–30 ms (about 6–70 ms total). Ranges below span the three motors. Full per-motor numbers, state age and
command counts are in [runs.csv](2026-10-20-hansi-straightline-run-logs/runs.csv).

| run | link | layout | start (deg, A B C) | final (deg) | straight | settled (s) | path dev (deg) | RTT p50 (ms) | RTT p95 (ms) | RTT max (ms) | overruns |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `20261019-134810` | USB gateway | flat | 0.1 -0.5 0.9 | 0.11 -0.52 0.29 | YES | 0.00 | 0.3 | 12-13 | 20-23 | 116 | 0 |
| `20261019-134844` | USB gateway | flat | 0.1 -45.3 0.3 | 0.11 0.29 0.29 | YES | 1.28 | 0.5 | 11-13 | 20-24 | 110 | 0 |
| `20261019-134925` | USB gateway | flat | -34.8 33.5 -23.0 | 0.69 0.23 -0.11 | YES | 1.04 | 6.2 | 12-12 | 20-22 | 50 | 0 |
| `20261019-135755` | USB gateway | flat | 67.6 -26.5 -0.1 | -0.46 -0.63 -0.11 | YES | 1.52 | 4.2 | 14-14 | 22-26 | 108 | 0 |
| `20261019-140034` | USB gateway | flat | -28.8 -45.9 -34.7 | -0.57 0.69 0.57 | YES | 1.34 | 3.0 | 11-12 | 23-24 | 115 | 0 |
| `20261019-140440` | USB gateway | flat | 53.5 52.8 49.6 | -0.57 -0.80 0.46 | YES | 1.70 | 2.1 | 12-15 | 22-23 | 49 | 0 |
| `20261019-140853` | USB gateway | flat | 119.6 -111.4 0.5 | -0.46 0.11 0.46 | YES | 2.42 | 1.1 | 10-11 | 20-21 | 32 | 0 |
| `20261019-141028` | USB gateway | flat | -106.7 105.8 -103.4 | 0.57 -0.40 1.15 | YES | 2.30 | 6.5 | 12-14 | 22-23 | 38 | 0 |
| `20261019-141529` | USB gateway | flat | -50.3 -77.3 -49.1 | -0.29 0.06 0.86 | YES | 1.98 | 5.0 | 12-14 | 21-22 | 33 | 0 |
| `20261019-141759` | USB gateway | flat | -47.0 -86.6 -1.5 | 0.29 1.32 -0.40 | YES | 4.58 | **8.9** | 11-13 | 20-22 | 224 | 0 |
| `20261019-142226` | USB gateway | flat | -34.5 -99.5 1.9 | 0.69 0.34 0.40 | YES | 3.70 | 7.4 | 11-14 | 20-23 | 40 | 0 |
| `20261019-230541` | Wi-Fi | standing | 55.3 -0.2 -13.4 | -0.97 -0.34 -0.69 | YES | 1.52 | 2.9 | 21-34 | 189-250 | 371 | 0 |
| `20261019-233910` | Wi-Fi | standing | -87.2 31.5 -74.9 | -1.26 -2.06 0.97 | YES | 2.22 | 6.0 | 12-24 | 159-175 | 339 | 0 |
| `20261020-134631` | Wi-Fi | standing | 46.1 -4.4 44.7 | -0.74 **-4.07** 0.70 | NO | — | 5.4 | 27-47 | 216-351 | 713 | 0 |
| `20261020-134856` | Wi-Fi | standing | -13.6 0.0 -13.4 | -1.38 -0.97 0.98 | YES | 4.94 | 6.7 | 28-55 | 357-642 | 909 | 5 |
| `20261020-144256` | Wi-Fi | standing | 74.6 -0.5 39.7 | -0.69 **-2.92** -0.10 | NO | — | 4.0 | 25-42 | 257-261 | 404 | 0 |

Not hardware: `20261019-171319` ran against a fake UDP master on the laptop (software check of the UDP path).
The `-sim` files are simulator runs. Both are in the folder and the CSV, labelled.

`20261019-141759` reached straight but failed coordination (8.9° > 8.6°): motor A stopped acking commands from
3.1 s while its state kept arriving, so commands to A were being lost (A had the weakest radio in the flat
layout, RSSI about −82 dBm).

## Link findings

- **USB gateway [verified]:** 11/11 runs straight, 10/11 passed coordination. RTT p95 20–26 ms, inside the
  trained range.
- **Wi-Fi [verified]:** 3/5 runs passed. RTT p95 159–642 ms and spikes to 909 ms, 3–10× the trained range. The
  delay is on the laptop's Wi-Fi side (ping to the AP alone shows 100–180 ms p95 with p50 4–9 ms), not ESP-NOW.
- **Failure mode on Wi-Fi:** both failures leave B (middle) a few degrees off straight. A and C stall short of their
  targets, the policy's accumulated target for B drifts while B stick-slips, and stale commands (0.6–0.9 s
  old in the worst ticks) make the correction overshoot or stop short.
- **Master firmware fix (2026-10-20, tethersmall `9c1019c`):** failed UDP sends dropped from about 170/s to
  about 14/s after batching sends, retrying on `ERR_MEM`, making USB serial non-blocking and setting DTIM 1.
  [from session output; the raw counters were not saved]
- **Recommendation from these sessions [assumed]:** use the USB gateway for closed-loop control on the climber.
  Wi-Fi to the laptop adds latency the policy wasn't trained for.

## Antenna test on master B (2026-10-20) [verified]

B has a U.FL antenna fitted. The XIAO C6 selects onboard vs U.FL with GPIO14 (`ANT_EXTERNAL`). B was reflashed
alternately with each build, 3 tests each. Raw output:
[antenna-compare.log](2026-10-20-hansi-straightline-run-logs/antenna-compare.log). The motors were unpowered, so
this measures the radio only (no command RTT).

| | onboard ceramic | external U.FL |
|---|---|---|
| laptop signal to B | 85 / 87 / 86 % | 97 / 96 / 97 % |
| RSSI of A as heard by B | −49 to −50 dBm | −40 to −42 dBm |
| RSSI of C as heard by B | −28 to −29 dBm | −28 to −30 dBm |
| ping to B, p50 / p95 / max (ms) | 4–8 / 103–177 / 124–189 | 4–9 / 103–140 / 122–162 |

External gives about 8 dB more to the far motor (A) and about 11 points more laptop signal. Ping latency is about the
same, which fits the delay being on the laptop side. Since tethersmall `87c46ba`, `master_b_c6` builds with
`-DANT_EXTERNAL=1`. Run `20261020-144256` was the first policy run with the external antenna. One run is not
enough to say whether it changed policy latency.

## Files

- `logs/run-*.npz`: one per run, written by `deploy/straightline/runner.py`. Keys: `t`, `seq`, `q`, `qd`
  (rad, rad/s, robot frame), `a` (policy actions), `target`, `age` (s since each motor's last state), `lag`,
  `overrun`, `cmd_latency_a/b/c` (s, one entry per acked command), `meta` (JSON: policy, calibration, stop reason).
- `runs.csv`: the per-run summary above, with per-motor RTT p50/p95/max, ack counts and state age p95/max.
- `antenna-compare.log`: the onboard vs external test output.

## Relevance to open questions

- **Master radio location** ([open-questions](../truth/open-questions.md)): these runs compare both options on the same
  arm. The on-robot SoftAP master (D-026 layout) had 6–25× the p95 RTT of the master at the laptop (USB gateway).
  The arm layout also differed (standing vs flat), so this is not a controlled comparison.
- **ESP-NOW margin (open question 14):** ESP-NOW itself was not the bottleneck in the Wi-Fi runs. The laptop ↔ AP
  hop was. The boards here are C6s, not the C5s in D-029.

Not promoted to `truth/`.
