---
status: draft
owner: John Peng
last_reviewed: 2026-10-28
---

# Latency slides: software challenge and solution (2026-10-22)

Graphics for the software column of the "challenges" and "solutions" slides. Written by John's AI agent.
Files are in [2026-10-22-john-latency-slides/](2026-10-22-john-latency-slides/): a PNG and an SVG for each,
plus `make_range.py`, which rebuilds them. Earlier drafts are in `archive/2026-10-22-john-latency-slides-v1/`
and `-v2/`.

## Captions

- **Challenge:** Wireless lag past the 70 ms limit
- **Solution:** 5 GHz ESP32-C5 link: under 40 ms

## What the charts show

Command→state round trip on a shared 0–220 ms axis. The bar runs from 0 to the 95th percentile, the dot is
the median, and the whisker ends at the slowest command. Coral marks anything past 70 ms.

- **The 70 ms limit** is the policy's trained worst-case round trip (tethersmall `docs/ESPNOW_BRINGUP.md`:
  "trained 6–70 ms"). It is not a formal project requirement.
- **Challenge:** two-motor crawler, 2026-10-11, 2.4 GHz channel 11, C3 master and C3/C6 slaves. Tethersmall
  `deploy/hardware_logs/run-20261011-013601.npz`, computed per motor: median 13 / 14 ms, p95 73 / 68 ms,
  max 201 / 212 ms. This was a policy run.
- **Solution:** all-C5 three-motor arm, 2026-10-28, 5 GHz channel 36, from Hansi's
  [C5 range test](2026-10-28-hansi-c5-range-test.md). Each row is the worst motor at that distance: bench 12.4 / 19.5 / 25.3 ms,
  3 m 12.4 / 19.5 / 39.3 ms, 5–6 m through a wall 13.0 / 21.6 / 33.3 ms (median / p95 / max). Acked
  98–99.6 %. The three 3 m repeat runs agree (max 23.8–34.5 ms).

## Caveats

- The C5 test is `link_check.py` with damping-only commands at 50 Hz. The motors did not move and no policy ran.
  The round trip is measured the same way as in the policy runs.
- The C5 log has only per-motor summaries (median, p95, max), not every command. That is why these are
  range charts and not histograms.
- Between the two tests the band, the radio boards, the gateway and the motor count all changed. Nothing
  isolates the 5 GHz move on its own.
