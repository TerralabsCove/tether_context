"""Battery runtime estimates for Tether, using the estimator model from
tether_ros/tools/robot_control.py (idle_w + |tau*qd|/0.8 + k*tau^2 per motor).
Torques are ASSUMED from the 10-28 step-reach sim; end-effector loads are ASSUMED.
Run: python3 -I battery_sim.py <tether_ros dir>
"""
import csv, sys, os
import numpy as np

ROOT = sys.argv[1]
rng = np.random.default_rng(7)

# ---- repo constants (robot_control.py) ----
MODS = {
    "mod11": dict(motors=[0, 1, 2], wh=6 * 3.7 * 5.0, idle=4.0),
    "mod12": dict(motors=[3], wh=6 * 3.7 * 6.4, idle=2.5),
    "mod13": dict(motors=[4, 5, 6], wh=6 * 3.7 * 5.0, idle=4.0),
}
BIG = {1, 3, 5}  # span_order idx of Revolute_22/112/29 (10010 pitch motors)
K_BIG, K_SMALL, ETA = 0.025, 0.12, 0.80


def module_watts(mod, tau, qd, idle_scale=1.0, eta=ETA, kscale=1.0):
    w = MODS[mod]["idle"] * idle_scale
    for m in MODS[mod]["motors"]:
        k = (K_BIG if m in BIG else K_SMALL) * kscale
        w += abs(tau[m] * qd[m]) / eta + k * tau[m] ** 2
    return w


# ---- assumed torque scenarios (Nm per motor 0..6), stance end = module 11 ----
S1 = dict(tau=[0.3, 5, 1, 3, 1, 2, 0.3], qd=[0] * 7)                      # standby, holding upright
S2 = dict(tau=[1, 30, 6, 18, 6, 8, 1], qd=[0] * 7)                        # hold, mid reach
S3 = dict(tau=[2, 57, 12, 35, 13, 20, 2], qd=[0] * 7)                     # hold, full reach (sim peak)
S3m = dict(tau=[2, 57, 12, 35, 13, 20, 2], qd=[.3, .4, .8, .4, .8, .4, .3])  # full-reach step, moving
SC = {"standby": S1, "hold-mid": S2, "hold-full": S3, "step": S3m}
# walking mix, averaged over which end is anchored (swap 11 <-> 13 roles)
MIX = {"standby": .20, "hold-mid": .45, "step": .35}


def swap(s):  # anchor on the other end: reverse motor order
    return dict(tau=s["tau"][::-1], qd=s["qd"][::-1])


def scen_watts(name, mod, **kw):
    a = module_watts(mod, SC[name]["tau"], SC[name]["qd"], **kw)
    b = module_watts(mod, swap(SC[name])["tau"], swap(SC[name])["qd"], **kw)
    return 0.5 * (a + b)  # half the time each end anchored


def walking_watts(mod, mix=MIX, **kw):
    return sum(f * scen_watts(n, mod, **kw) for n, f in mix.items())


USABLE = 0.85
print("== 1. Deterministic main-module runtimes (usable = 85% of nominal Wh) ==")
print(f"{'scenario':<12}" + "".join(f"{m:>22}" for m in MODS))
for n in list(SC) + ["walking mix"]:
    row = f"{n:<12}"
    for m in MODS:
        w = walking_watts(m) if n == "walking mix" else scen_watts(n, m)
        h = USABLE * MODS[m]["wh"] / w
        row += f"{w:>9.1f} W {h:>6.2f} h   "
    print(row)

print("\n   module 12 if only ONE 3200 mAh pack is in use (71 Wh nominal):")
for n in list(SC) + ["walking mix"]:
    w = walking_watts("mod12") if n == "walking mix" else scen_watts(n, "mod12")
    print(f"   {n:<12}{w:6.1f} W  {USABLE*6*3.7*3.2/w:5.2f} h")

# ---- Monte Carlo ----
N = 40000
print(f"\n== 2. Monte Carlo, walking mix, {N} draws ==")
print("   varied: torque scale (lognormal, mean x1.08 for unweighed wiring/boards), motor efficiency 0.70-0.90,")
print("   idle draw x0.5-2.0, copper-loss coefficient x0.5-1.5, usable fraction 0.75-0.95, real capacity 0.90-1.00,")
print("   walking mix Dirichlet around 20/45/35")
res = {m: [] for m in MODS}
res["mod12 (1 pack)"] = []
for _ in range(N):
    ts = rng.lognormal(np.log(1.08), 0.2)
    eta = rng.uniform(.7, .9)
    ids = rng.uniform(.5, 2.0)
    ks = rng.uniform(.5, 1.5)
    use = rng.uniform(.75, .95)
    cap = rng.uniform(.9, 1.0)
    f = rng.dirichlet(np.array([.20, .45, .35]) * 20)
    mix = dict(zip(["standby", "hold-mid", "step"], f))
    for m in MODS:
        # scale torques by editing a temp copy via kscale (tau^2) and eta; apply ts through scenario copies
        w = 0.0
        for n, fr in mix.items():
            sc = SC[n]
            tau = [t * ts for t in sc["tau"]]
            a = module_watts(m, tau, sc["qd"], ids, eta, ks)
            tau_r, qd_r = tau[::-1], sc["qd"][::-1]
            b = module_watts(m, tau_r, qd_r, ids, eta, ks)
            w += fr * 0.5 * (a + b)
        res[m].append(use * cap * MODS[m]["wh"] / w)
        if m == "mod12":
            res["mod12 (1 pack)"].append(use * cap * 6 * 3.7 * 3.2 / w)
for m, v in res.items():
    p = np.percentile(v, [10, 50, 90])
    print(f"   {m:<16} P10 {p[0]:5.2f} h   P50 {p[1]:5.2f} h   P90 {p[2]:5.2f} h")

# ---- Replay of measured bench torque through the estimator ----
print("\n== 3. Replay of measured bench data through the estimator (motor 0 = 4340, module 11) ==")
for name in ("2026-11-22_ros_sweep_0x01", "2026-11-22_ros_turn_0x01"):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "bench_results", name, "joint_states.csv"))))
    t = np.array([float(r["t_s"]) for r in rows])
    tau = np.array([float(r["joint_a_effort_nm"]) for r in rows])
    qd = np.array([float(r["joint_a_vel_rads"]) for r in rows])
    w_mot = np.abs(tau * qd) / ETA + K_SMALL * tau ** 2
    w_tot = MODS["mod11"]["idle"] + w_mot
    wh = np.trapezoid(w_tot, t) / 3600
    avgw = w_tot.mean()
    print(f"   {name}: {t[-1]-t[0]:.1f} s, mean module-11 draw {avgw:.2f} W (idle 4.0 + motor {w_mot.mean():.2f}), "
          f"-> {USABLE*MODS['mod11']['wh']/avgw:.1f} h if repeated forever. Only one motor was loaded; this is the bench, not the arm.")

# ---- End effector: 3S 450 mAh via LM2596 ----
print("\n== 4. End effector, 3S 450 mAh (4.995 Wh nominal) ==")
EE_WH = 3 * 3.7 * 0.45
loads = {  # watts at the 5 V rail (camera, C5, ring), servos on pack ~12 V; ASSUMED ranges (lo, hi)
    "C5 radio (ESP-NOW 50 Hz)": (0.35, 0.60),
    "reCamera streaming tags": (1.5, 3.5),
    "2 x STS3215, torque on, light": (0.4, 1.8),
    "LED ring (low brightness)": (0.1, 0.5),
}
SERV_DOCK = (4.0, 9.0)  # extra W while the dock servo drives against load (a few seconds per dock)
def ee_runtime(cam_on, ring_on, dock_frac, n=N):
    w = np.zeros(n)
    for k, (lo, hi) in loads.items():
        if "camera" in k.lower() and not cam_on: continue
        if "ring" in k and not ring_on: continue
        w += rng.uniform(lo, hi, n)
    w += dock_frac * rng.uniform(*SERV_DOCK, n)
    eta = rng.uniform(.72, .88, n)  # LM2596 5 V from ~11 V; applied to everything for simplicity
    w_batt = w / eta + rng.uniform(.05, .15, n)  # buck quiescent
    use = rng.uniform(.75, .92, n)
    cap = rng.uniform(.85, 1.0, n)  # cheap 450 mAh packs under-deliver
    return use * cap * EE_WH / w_batt * 60, w_batt  # minutes
for label, args in {
    "standby (camera off, no ring)": (False, False, 0.0),
    "normal (camera + C5 + servos)": (True, False, 0.02),
    "show mode (camera + ring + docking 10%)": (True, True, 0.10),
}.items():
    mins, wb = ee_runtime(*args)
    p = np.percentile(mins, [10, 50, 90]); pw = np.percentile(wb, 50)
    print(f"   {label:<42} median draw {pw:4.1f} W   P10 {p[0]:5.0f} min   P50 {p[1]:5.0f} min   P90 {p[2]:5.0f} min")

# ---- Pack sag / UV check ----
print("\n== 5. Voltage sag check, worst module (module 11, 'hold-full') ==")
w = scen_watts("hold-full", "mod11")
for v in (25.2, 22.2, 19.8):
    i = w / v
    for r in (0.05, 0.12):  # pack internal resistance (assumed, 6S, includes leads/connectors)
        print(f"   {w:.0f} W at {v:4.1f} V open-circuit: {i:4.1f} A, sag {i*r:4.2f} V at {r*1000:.0f} mOhm -> {v - i*r:5.2f} V under load")
