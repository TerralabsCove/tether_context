"""Generate the two square latency graphics for the challenges / solutions slides."""
import sys
import numpy as np

LOG, OUT = sys.argv[1], sys.argv[2]

BG = "#EEEEEE"
CARD = "#FFFFFF"
INK = "#24585B"        # dark teal, matches slide headings
INK2 = "#5F7E80"       # secondary text
MUTED = "#98AEAF"
GRID = "#E6ECEC"
TEAL = "#1E9E8C"
TEAL_SOFT = "#D7EFEA"
TEAL_TINT = "#F1F9F7"
CORAL = "#E0674F"
CORAL_SOFT = "#FBE3DD"
FONT = "Avenir Next"
W = H = 1200


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n'
            '<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%">'
            '<feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#1c3d3f" flood-opacity="0.07"/>'
            '</filter>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1 L9 5 L1 9" fill="none" stroke="{TEAL}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker>'
            '</defs>\n'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>\n{body}\n</svg>\n')


def text(x, y, s, size=28, fill=INK, weight=500, anchor="start", ls=0, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{s}</text>')


def card(x, y, w, h, r=28, fill=CARD):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" filter="url(#sh)"/>'


def kicker(s, color=TEAL):
    return (f'<circle cx="72" cy="78" r="9" fill="{color}"/>' +
            text(94, 88, s, 26, color, 600, ls=3))


# ---- icons (drawn at a centre point, ~64 px) ----
def icon_laptop(cx, cy, c=INK):
    return (f'<rect x="{cx-30}" y="{cy-24}" width="60" height="38" rx="5" fill="none" stroke="{c}" stroke-width="4"/>'
            f'<path d="M{cx-40} {cy+22} H{cx+40}" stroke="{c}" stroke-width="5" stroke-linecap="round"/>')


def icon_chip(cx, cy, c=INK):
    pins = "".join(
        f'<path d="M{cx+d} {cy-30} V{cy-22} M{cx+d} {cy+22} V{cy+30} M{cx-30} {cy+d} H{cx-22} M{cx+22} {cy+d} H{cx+30}" '
        f'stroke="{c}" stroke-width="4" stroke-linecap="round"/>' for d in (-10, 0, 10))
    return (f'<rect x="{cx-22}" y="{cy-22}" width="44" height="44" rx="7" fill="none" stroke="{c}" stroke-width="4"/>'
            f'<rect x="{cx-9}" y="{cy-9}" width="18" height="18" rx="3" fill="{c}"/>' + pins)


def icon_motor(cx, cy, c=INK):
    return (f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="{c}" stroke-width="4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{c}"/>'
            + "".join(f'<circle cx="{cx+18*np.cos(a):.1f}" cy="{cy+18*np.sin(a):.1f}" r="2.6" fill="{c}"/>'
                      for a in np.linspace(0, 2*np.pi, 6, endpoint=False)))


def icon_sim(cx, cy, c=INK):
    # a cube in perspective: simulation
    return (f'<path d="M{cx} {cy-28} L{cx+26} {cy-14} L{cx+26} {cy+16} L{cx} {cy+30} L{cx-26} {cy+16} L{cx-26} {cy-14} Z" '
            f'fill="none" stroke="{c}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M{cx-26} {cy-14} L{cx} {cy} L{cx+26} {cy-14} M{cx} {cy} V{cy+30}" fill="none" stroke="{c}" '
            f'stroke-width="4" stroke-linejoin="round"/>')


def icon_brain(cx, cy, c=INK):
    # small neural net: policy
    L = [(-24, -18), (-24, 18)]
    M = [(0, -26), (0, 0), (0, 26)]
    R = [(24, 0)]
    lines = "".join(f'<path d="M{cx+a[0]} {cy+a[1]} L{cx+b[0]} {cy+b[1]}" stroke="{c}" stroke-width="2.4"/>'
                    for p, q in ((L, M), (M, R)) for a in p for b in q)
    dots = "".join(f'<circle cx="{cx+x}" cy="{cy+y}" r="6.5" fill="{CARD}" stroke="{c}" stroke-width="3.6"/>'
                   for x, y in L + M + R)
    return lines + dots


def node(cx, cy, icon, label, sub, ring=TEAL_SOFT, fill=TEAL_TINT):
    return (f'<circle cx="{cx}" cy="{cy}" r="58" fill="{fill}" stroke="{ring}" stroke-width="3"/>' + icon(cx, cy) +
            text(cx, cy + 98, label, 29, INK, 600, "middle") +
            text(cx, cy + 132, sub, 23, INK2, 500, "middle"))


# =====================================================================
# 1. The problem
# =====================================================================
def problem(lat_ms):
    b = [kicker("THE PROBLEM  ·  FIRST HARDWARE TEST", CORAL)]

    # --- link card ---
    b.append(card(48, 124, 1104, 300))
    cy = 222
    xs = [140, 392, 808, 1060]
    # wires
    b.append(f'<path d="M{xs[0]+64} {cy} H{xs[1]-64}" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>')
    b.append(f'<path d="M{xs[2]+64} {cy} H{xs[3]-64}" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>')
    b.append(text((xs[0]+xs[1])/2, cy - 18, "USB", 21, MUTED, 600, "middle", 2))
    b.append(text((xs[2]+xs[3])/2, cy - 18, "CAN", 21, MUTED, 600, "middle", 2))
    # wireless hop: dotted air path with packets, one lost
    x0, x1 = xs[1] + 72, xs[2] - 72
    b.append(f'<path d="M{x0} {cy} H{x1}" stroke="{MUTED}" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>')
    for i, px in enumerate(np.linspace(x0 + 30, x1 - 30, 5)):
        if i == 3:
            b.append(f'<rect x="{px-13}" y="{cy-13}" width="26" height="26" rx="6" fill="{CORAL_SOFT}" stroke="{CORAL}" stroke-width="3"/>'
                     f'<path d="M{px-6} {cy-6} L{px+6} {cy+6} M{px+6} {cy-6} L{px-6} {cy+6}" stroke="{CORAL}" stroke-width="3.4" stroke-linecap="round"/>')
        else:
            b.append(f'<rect x="{px-11}" y="{cy-11}" width="22" height="22" rx="5" fill="{TEAL}"/>')
    b.append(text((x0+x1)/2, cy - 30, "ESP-NOW · WIRELESS", 21, CORAL, 600, "middle", 2))
    b.append(text((x0+x1)/2, cy + 46, "packets drop in bursts", 22, INK2, 500, "middle"))

    b.append(node(xs[0], cy, icon_laptop, "Laptop", "RL policy, 50 Hz"))
    b.append(node(xs[1], cy, icon_chip, "Master ESP32", "on the laptop"))
    b.append(node(xs[2], cy, icon_chip, "Module ESP32", "on the robot"))
    b.append(node(xs[3], cy, icon_motor, "Motor", "Damiao"))

    # --- stat row ---
    mean, worst = lat_ms.mean(), lat_ms.max()
    stats = [(f"{mean:.0f}", "ms", "average round trip", INK),
             (f"{worst:.0f}", "ms", "worst spike", CORAL),
             ("6–9", "%", "of commands lost", CORAL)]
    for i, (num, unit, lab, col) in enumerate(stats):
        x = 48 + i * 376
        b.append(card(x, 452, 352, 172, 24))
        b.append(f'<text x="{x+34}" y="{452+100}" font-size="76" font-weight="600" fill="{col}" letter-spacing="-1">'
                 f'{num}<tspan font-size="36" font-weight="500" dx="6">{unit}</tspan></text>')
        b.append(text(x + 36, 452 + 144, lab, 25, INK2, 500))

    # --- needle chart ---
    cx0, cy0, cw, ch = 48, 652, 1104, 500
    b.append(card(cx0, cy0, cw, ch))
    b.append(text(cx0 + 40, cy0 + 60, "Round trip of every command", 31, INK, 600))
    b.append(text(cx0 + 40, cy0 + 96, f"one motor, {len(lat_ms):,} commands over a 20 s run", 23, INK2, 500))
    px0, px1 = cx0 + 104, cx0 + cw - 170
    py0, py1 = cy0 + ch - 64, cy0 + 150            # baseline, top
    ymax = 220.0
    sy = lambda v: py0 - (v / ymax) * (py0 - py1)
    for v in (0, 50, 100, 150, 200):
        y = sy(v)
        b.append(f'<path d="M{px0} {y:.1f} H{px1}" stroke="{GRID if v else "#C9D6D6"}" stroke-width="{1.5 if v else 2}"/>')
        b.append(text(px0 - 16, y + 8, f"{v}", 22, MUTED, 500, "end"))
    b.append(text(px0 - 16, sy(220) + 6, "ms", 22, MUTED, 600, "end"))
    n = len(lat_ms)
    xs_ = np.linspace(px0 + 4, px1 - 4, n)
    calm = "".join(f"M{x:.1f} {py0} V{sy(v):.1f}" for x, v in zip(xs_, lat_ms) if v <= 70)
    spk = "".join(f"M{x:.1f} {py0} V{sy(v):.1f}" for x, v in zip(xs_, lat_ms) if v > 70)
    b.append(f'<path d="{calm}" stroke="{TEAL}" stroke-width="1.3" opacity="0.85"/>')
    b.append(f'<path d="{spk}" stroke="{CORAL}" stroke-width="2"/>')
    # median line + label
    med = float(np.median(lat_ms))
    b.append(f'<path d="M{px0} {sy(med):.1f} H{px1}" stroke="{INK}" stroke-width="2" stroke-dasharray="8 6"/>')
    b.append(text(px1 + 16, sy(med) - 6, "typical", 22, INK2, 500))
    b.append(text(px1 + 16, sy(med) + 22, f"{med:.0f} ms", 24, INK, 600))
    # worst annotation
    i = int(np.argmax(lat_ms))
    wx, wy = xs_[i], sy(lat_ms[i])
    b.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="7" fill="{CORAL}" stroke="{CARD}" stroke-width="3"/>')
    lx = wx + 22 if wx < px1 - 260 else wx - 22
    anc = "start" if wx < px1 - 260 else "end"
    b.append(text(lx, wy + 8, f"{worst:.0f} ms spike", 24, CORAL, 600, anc))
    # legend
    lgx = cx0 + cw - 370
    b.append(f'<rect x="{lgx}" y="{cy0+44}" width="18" height="18" rx="4" fill="{TEAL}"/>' +
             text(lgx + 28, cy0 + 60, "on time", 22, INK2, 500) +
             f'<rect x="{lgx+138}" y="{cy0+44}" width="18" height="18" rx="4" fill="{CORAL}"/>' +
             text(lgx + 166, cy0 + 60, "over 70 ms", 22, INK2, 500))
    return svg("\n".join(b))


# =====================================================================
# 2. The fix
# =====================================================================
def fix():
    b = [kicker("THE FIX  ·  A POLICY THAT EXPECTS LAG", TEAL)]

    # --- pipeline card: sim -> policy -> robot ---
    b.append(card(48, 124, 1104, 300))
    cy = 222
    xs = [200, 600, 1000]
    for a, c in ((xs[0], xs[1]), (xs[1], xs[2])):
        b.append(f'<path d="M{a+80} {cy} H{c-84}" stroke="{TEAL}" stroke-width="4" stroke-linecap="round" marker-end="url(#arr)"/>')
    b.append(text((xs[0]+xs[1])/2, cy - 18, "TRAIN", 21, TEAL, 600, "middle", 2))
    b.append(text((xs[1]+xs[2])/2, cy - 18, "DEPLOY", 21, TEAL, 600, "middle", 2))
    b.append(node(xs[0], cy, icon_sim, "Simulation", "with a model of the radio"))
    b.append(node(xs[1], cy, icon_brain, "RL policy", "runs on the laptop"))
    b.append(node(xs[2], cy, icon_motor, "Real robot", "gait matched sim"))

    # --- two checklist cards ---
    lists = [("Trained against", ["4–40 ms delays", "40–300 ms dropouts", "lost packets, laptop stalls"]),
             ("Built into every module", ["each command sent twice", "goes limp after 200 ms of silence", "local speed and torque limits"])]
    for i, (title, items) in enumerate(lists):
        x = 48 + i * 564
        b.append(card(x, 452, 540, 232, 24))
        b.append(text(x + 36, 452 + 56, title, 27, INK, 600))
        for j, it in enumerate(items):
            y = 452 + 106 + j * 46
            b.append(f'<circle cx="{x+48}" cy="{y-8}" r="13" fill="{TEAL_SOFT}"/>'
                     f'<path d="M{x+41} {y-8} l5 5 l9 -10" fill="none" stroke="{TEAL}" stroke-width="3.2" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
            b.append(text(x + 74, y, it, 24, INK2, 500))

    # --- bar chart: success vs delay ---
    cx0, cy0, cw, ch = 48, 712, 1104, 440
    b.append(card(cx0, cy0, cw, ch))
    b.append(text(cx0 + 40, cy0 + 60, "Success rate as wireless delay grows", 31, INK, 600))
    b.append(text(cx0 + 40, cy0 + 96, "3-module arm in simulation", 23, INK2, 500))
    b.append(f'<text x="{cx0+cw-40}" y="{cy0+74}" text-anchor="end" font-size="62" font-weight="600" fill="{TEAL}">100'
             f'<tspan font-size="32" dx="4">%</tspan></text>')
    b.append(text(cx0 + cw - 40, cy0 + 104, "up to 60 ms", 23, INK2, 600, "end"))

    delays = [0, 20, 40, 60, 80, 100]
    succ = [100, 100, 100, 100, 94, 94]
    px0, px1 = cx0 + 104, cx0 + cw - 40
    py0, py1 = cy0 + ch - 70, cy0 + 160
    sy = lambda v: py0 - v / 100 * (py0 - py1)
    slot = (px1 - px0) / len(delays)
    bw = slot * 0.58
    # trained-range band behind first three slots (0-40 ms)
    b.append(f'<rect x="{px0+4}" y="{py1-34}" width="{slot*3-8:.1f}" height="{py0-py1+34}" rx="14" fill="{TEAL_TINT}"/>')
    b.append(text(px0 + 20, py1 - 10, "TRAINED RANGE", 19, TEAL, 600, ls=2))
    for v in (0, 50, 100):
        y = sy(v)
        b.append(f'<path d="M{px0} {y:.1f} H{px1}" stroke="{GRID if v else "#C9D6D6"}" stroke-width="{1.5 if v else 2}"/>')
        b.append(text(px0 - 16, y + 8, f"{v}%", 22, MUTED, 500, "end"))
    for k, (d, s) in enumerate(zip(delays, succ)):
        x = px0 + slot * k + (slot - bw) / 2
        top = sy(s)
        # rounded top, square baseline
        r = 8
        b.append(f'<path d="M{x:.1f} {py0} V{top+r:.1f} Q{x:.1f} {top:.1f} {x+r:.1f} {top:.1f} H{x+bw-r:.1f} '
                 f'Q{x+bw:.1f} {top:.1f} {x+bw:.1f} {top+r:.1f} V{py0} Z" fill="{TEAL}"/>')
        b.append(text(x + bw / 2, top + 34, f"{s}%", 22, CARD, 600, "middle"))
        b.append(text(x + bw / 2, py0 + 36, f"{d} ms", 22, INK2, 500, "middle"))
    return svg("\n".join(b))


lat = np.load(LOG)["cmd_latency_b"] * 1e3
open(f"{OUT}/latency-problem.svg", "w").write(problem(lat))
open(f"{OUT}/latency-fix.svg", "w").write(fix())
