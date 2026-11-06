"""Latency spread vs the 70 ms limit, as range bars: median dot, bar to p95, whisker to the worst command.

Challenge: 2026-10-11 first policy test, 2.4 GHz (tethersmall run-20261011-013601.npz, per motor).
Solution: 2026-10-28 all-C5 arm link test, 5 GHz channel 36 (Hansi's link-check.log in
tether_context notes/2026-10-28-hansi-c5-range-test/, worst motor at each distance).

usage: make_range.py OUT_DIR BEFORE.npz
"""
import sys
import numpy as np

OUT, BEFORE = sys.argv[1], sys.argv[2]

BG, INK, INK2, MUTED, GRID, AXIS = "#EEEEEE", "#24585B", "#5F7E80", "#8FA4A5", "#E0E5E5", "#9DB0B0"
TEAL, CORAL = "#1E9E8C", "#E0674F"
FONT = "Avenir Next"
W = H = 1200
LIMIT, XMAX = 70.0, 220.0


def t(x, y, s, size, fill, weight=500, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{s}</text>')


def chart(rows, subtitle):
    b = []
    x0, x1, top, bot = 300, 1120, 250, 900
    sx = lambda v: x0 + v / XMAX * (x1 - x0)

    b.append(t(80, 130, subtitle, 36, INK2, 500))

    for v in (0, 50, 100, 150, 200):
        b.append(f'<path d="M{sx(v):.1f} {top} V{bot}" stroke="{GRID}" stroke-width="2"/>')
        b.append(t(sx(v), bot + 54, f"{v}", 36, MUTED, 500, "middle"))
    b.append(f'<path d="M{x0} {bot} H{x1}" stroke="{AXIS}" stroke-width="3"/>')
    b.append(t((x0 + x1) / 2, bot + 112, "round-trip latency (ms)", 38, INK2, 500, "middle"))

    lx = sx(LIMIT)
    b.append(f'<path d="M{lx:.1f} {top - 40} V{bot}" stroke="{INK}" stroke-width="3" stroke-dasharray="12 9"/>')
    b.append(t(lx + 18, top - 14, "70 ms limit", 36, INK, 600))

    step = (bot - top) / (len(rows) + 1)
    for i, (label, p50, p95, worst) in enumerate(rows):
        y = top + step * (i + 1)
        b.append(t(80, y + 13, label, 38, INK, 500))
        # whisker to the worst command, coral past the limit
        b.append(f'<path d="M{sx(p95):.1f} {y} H{sx(min(worst, LIMIT)):.1f}" stroke="{TEAL}" stroke-width="5"/>'
                 if p95 < LIMIT else "")
        if worst > LIMIT:
            b.append(f'<path d="M{sx(max(p95, LIMIT)):.1f} {y} H{sx(worst):.1f}" stroke="{CORAL}" stroke-width="5"/>')
        b.append(f'<path d="M{sx(worst):.1f} {y - 18} V{y + 18}" stroke="{CORAL if worst > LIMIT else TEAL}" '
                 f'stroke-width="5" stroke-linecap="round"/>')
        # bar: 95 % of commands land between 0 and p95
        b.append(f'<rect x="{x0}" y="{y - 20}" width="{sx(min(p95, LIMIT)) - x0:.1f}" height="40" fill="{TEAL}"/>')
        if p95 > LIMIT:
            b.append(f'<rect x="{sx(LIMIT):.1f}" y="{y - 20}" width="{sx(p95) - sx(LIMIT):.1f}" height="40" fill="{CORAL}"/>')
        b.append(f'<circle cx="{sx(p50):.1f}" cy="{y}" r="13" fill="{BG}" stroke="{INK}" stroke-width="5"/>')
        b.append(t(sx(worst) + 22, y + 13, f"{worst:.0f}", 34, INK2, 600))

    # key
    ky = bot + 200
    b.append(f'<circle cx="94" cy="{ky - 12}" r="11" fill="{BG}" stroke="{INK}" stroke-width="4"/>'
             + t(118, ky, "median", 32, INK2))
    b.append(f'<rect x="268" y="{ky - 30}" width="56" height="34" fill="{TEAL}"/>'
             + t(338, ky, "95% of commands", 32, INK2))
    b.append(f'<path d="M670 {ky - 12} H730 M730 {ky - 30} V{ky + 6}" stroke="{TEAL}" stroke-width="5" '
             f'stroke-linecap="round"/>' + t(752, ky, "worst command", 32, INK2))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}"><rect width="{W}" height="{H}" fill="{BG}"/>\n' + "\n".join(b) + "\n</svg>\n")


d = np.load(BEFORE)
before = []
for i, k in enumerate(("cmd_latency_a", "cmd_latency_b")):
    x = d[k] * 1e3
    before.append((f"motor {i + 1}", np.median(x), np.percentile(x, 95), x.max()))

# 2026-10-28 link-check.log, worst motor at each distance (p50, p95, max in ms)
after = [("bench", 12.4, 19.5, 25.3),
         ("3 m", 12.4, 19.5, 39.3),
         ("5–6 m, wall", 13.0, 21.6, 33.3)]

open(f"{OUT}/latency-challenge.svg", "w").write(chart(before, "First test: 2.4 GHz, two motors (Oct 11)"))
open(f"{OUT}/latency-solution.svg", "w").write(chart(after, "ESP32-C5 at 5 GHz, three motors (Oct 28)"))
