"""Two latency-spread charts: before (2026-10-11) and after (2026-10-19), vs the 70 ms limit.

usage: make_simple.py OUT_DIR BEFORE.npz AFTER1.npz [AFTER2.npz ...]
"""
import sys
import numpy as np

OUT, BEFORE, AFTER = sys.argv[1], sys.argv[2], sys.argv[3:]

BG, INK, INK2, MUTED, GRID, AXIS = "#EEEEEE", "#24585B", "#5F7E80", "#8FA4A5", "#E0E5E5", "#9DB0B0"
TEAL, CORAL = "#1E9E8C", "#E0674F"
FONT = "Avenir Next"
W = H = 1200
LIMIT = 70.0
XMAX, BIN = 220.0, 5.0
YMAX = 35.0


def latencies(paths):
    out = []
    for p in paths:
        d = np.load(p, allow_pickle=True)
        out += [np.asarray(d[k], float) * 1e3 for k in d.files if k.startswith("cmd_latency_")]
    return np.concatenate(out)


def t(x, y, s, size, fill, weight=500, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def chart(lat, note):
    b = []
    x0, x1, y0, y1 = 170, 1130, 960, 140
    sx = lambda v: x0 + v / XMAX * (x1 - x0)
    sy = lambda v: y0 - v / YMAX * (y0 - y1)

    # y grid and ticks
    for v in (0, 10, 20, 30):
        b.append(f'<path d="M{x0} {sy(v):.1f} H{x1}" stroke="{GRID if v else AXIS}" stroke-width="{2 if v else 3}"/>')
        b.append(t(x0 - 22, sy(v) + 13, f"{v}%", 36, MUTED, 500, "end"))
    b.append(t(60, (y0 + y1) / 2, "share of commands", 36, INK2, 500, "middle",
               f'transform="rotate(-90 60 {(y0 + y1) / 2})"'))

    # histogram, % of commands per 5 ms bin
    edges = np.arange(0, XMAX + BIN, BIN)
    pct = np.histogram(np.clip(lat, 0, XMAX - 1e-6), edges)[0] / len(lat) * 100
    bw = sx(BIN) - sx(0) - 3
    for lo, v in zip(edges[:-1], pct):
        if v <= 0:
            continue
        h = max(v / YMAX * (y0 - y1), 5)
        b.append(f'<rect x="{sx(lo) + 1.5:.1f}" y="{y0 - h:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                 f'fill="{CORAL if lo >= LIMIT else TEAL}"/>')

    # x ticks and label
    for v in (0, 50, 100, 150, 200):
        b.append(f'<path d="M{sx(v):.1f} {y0} v12" stroke="{AXIS}" stroke-width="3"/>')
        b.append(t(sx(v), y0 + 54, f"{v}", 36, MUTED, 500, "middle"))
    b.append(t((x0 + x1) / 2, y0 + 112, "round-trip latency (ms)", 38, INK2, 500, "middle"))

    # the limit
    lx = sx(LIMIT)
    b.append(f'<path d="M{lx:.1f} {y1} V{y0}" stroke="{INK}" stroke-width="3" stroke-dasharray="12 9"/>')
    b.append(t(lx + 20, y1 + 36, "70 ms limit", 38, INK, 600))
    for i, line in enumerate(note):
        b.append(t(lx + 20, y1 + 84 + i * 46, line, 34, INK2, 500))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}"><rect width="{W}" height="{H}" fill="{BG}"/>\n' + "\n".join(b) + "\n</svg>\n")


def note(lat):
    late = (lat > LIMIT).mean() * 100
    return [f"{late:.1f}% of commands over it" if late < 1 else f"{late:.0f}% of commands over it",
            f"median {np.median(lat):.0f} ms, worst {lat.max():.0f} ms"]


before, after = latencies([BEFORE]), latencies(AFTER)
open(f"{OUT}/latency-challenge.svg", "w").write(chart(before, note(before)))
open(f"{OUT}/latency-solution.svg", "w").write(chart(after, note(after)))
