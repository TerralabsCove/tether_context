"""Prototype battery state estimator for a Tether module, tested on a simulated pack.

Inputs it is allowed to use (all exist today):
  - per-motor tau (Nm) and qd (rad/s) at ~200 Hz        -> modelled power P_model
  - an occasional resting pack voltage (LiPo checker typed in, or T_POWER VBus if it ever works)
  - the 0x09 undervoltage fault when UV_Value is raised to 19.8 V (hard 0 % anchor)
Estimator = energy counting with a learned gain g (capacity + loss mismatch) and a 1-D Kalman SoC.

Run: python3 -I soc_estimator.py
"""
import numpy as np

rng = np.random.default_rng(11)
CURVE = np.array([(19.8, 0), (21.0, 5), (22.1, 15), (22.5, 25), (22.8, 40), (23.1, 50), (23.5, 60),
                  (23.9, 70), (24.3, 80), (24.7, 90), (24.9, 95), (25.2, 100)])
v2s = lambda v: float(np.interp(v, CURVE[:, 0], CURVE[:, 1])) / 100
s2v = lambda s: float(np.interp(s * 100, CURVE[:, 1], CURVE[:, 0]))

BIG = {1}  # motor idx on module 11 that is a 10010; motors 0,2 are 4340
WH_NOM = 6 * 3.7 * 5.0
K_BIG, K_SMALL = 0.025, 0.12

# ---- activity: random segments of standby / hold-mid / step on module 11 (stance end) ----
SEG = {"standby": ([0.3, 5, 1], [0, 0, 0]),
       "hold": ([1, 30, 6], [0, 0, 0]),
       "step": ([2, 57, 12], [.3, .4, .8])}
PROB = {"standby": .20, "hold": .45, "step": .35}


def make_session(hours=3.0):
    tau, qd = [], []
    t = 0
    while t < hours * 3600:
        name = rng.choice(list(PROB), p=list(PROB.values()))
        dur = int(rng.uniform(60, 300))
        base_t, base_q = SEG[name]
        scale = rng.uniform(.8, 1.2)
        for _ in range(dur):
            tau.append([x * scale for x in base_t])
            qd.append(base_q)
        t += dur
    return np.array(tau), np.array(qd)


def power(tau, qd, idle, eta, kscale):
    p = idle + np.abs(tau * qd).sum(1) / eta
    k = np.array([K_SMALL, K_BIG, K_SMALL]) * kscale
    return p + (k * tau ** 2).sum(1)


def run(seed, anchors, sigma_v=0.07):
    """anchors: 'none' (repo today) | 'start' (one typed voltage at plug-in) | 'periodic' (+ rest readings)"""
    global rng
    rng = np.random.default_rng(seed)
    tau_true, qd = make_session()
    # ---- hidden truth ----
    cap = WH_NOM * rng.uniform(.85, 1.0)
    idle_t, eta_t, k_t = rng.uniform(2, 9), rng.uniform(.6, .9), rng.uniform(.5, 2.0)
    R = rng.uniform(.05, .15)
    p_true = power(tau_true, qd, idle_t, eta_t, k_t)
    soc0_true = rng.uniform(.85, 1.0)
    tau_meas = tau_true * (1 + 0.03 * rng.standard_normal(tau_true.shape))
    p_model = power(tau_meas, qd, 4.0, .80, 1.0)  # repo constants
    n = len(p_true)

    # truth SoC trajectory, cutoff when loaded voltage reaches 19.8 V
    soc_t = np.empty(n); s = soc0_true; cut = n
    for i in range(n):
        soc_t[i] = s
        v = s2v(s); I = p_true[i] / v
        if v - I * R <= 19.8 and s < .12:
            cut = i; break
        s -= p_true[i] / 3600 / cap
    soc_t = soc_t[:cut]
    p_model = p_model[:cut]; p_true = p_true[:cut]

    # ---- estimator ----
    g, var_g = 1.0, 0.5 ** 2                  # gain on modelled power, prior 1 +- 0.5
    soc, var = 1.0 if anchors == 'none' else None, 0.05 ** 2
    cum_model = 0.0                            # cumulative modelled Wh since first anchor
    soc_first = None
    est_soc = np.empty(cut); est_sig = np.empty(cut); gs = np.empty(cut)
    pavg = 30.0; rest_s = 0; last_anchor_i = -10 ** 9
    cs = np.cumsum(p_model) / 3600.0
    for i in range(cut):
        v_true = s2v(soc_t[i]); I = p_true[i] / v_true
        # anchor: resting voltage (low power for 2 min) or plug-in
        want = False
        if anchors != 'none' and i == 0:
            want = True
        elif anchors == 'periodic':
            rest_s = rest_s + 1 if p_model[i] < 12 else 0
            # prompt the operator for a reading after a 60 s low-power pause, at most every 10 min
            if rest_s == 60 and i - last_anchor_i > 600:
                want = True
        if want:
            last_anchor_i = i
        if want:
            v_meas = v_true - I * R + sigma_v * rng.standard_normal()
            v_meas += (p_model[i] / max(v_meas, 19)) * 0.10   # compensate with assumed R=0.10
            s_meas = v2s(v_meas)
            sig_s = max(sigma_v * 0.1 / 0.35, 0.02)  # volts -> SoC through the flat middle of the curve (~0.35 V per 10 %)
            sig_s = sigma_v / 0.035 / 100 if 0.15 < s_meas < 0.9 else 0.02
            if soc is None:
                soc, var = s_meas, sig_s ** 2; soc_first = s_meas; cum_model = 0.0
            else:
                K = var / (var + sig_s ** 2); soc += K * (s_meas - soc); var *= (1 - K)
                if cum_model > 2.0:                       # >= 2 Wh counted since the first anchor
                    g_meas = (soc_first - s_meas) * WH_NOM / cum_model
                    var_meas = (np.sqrt(2) * sig_s * WH_NOM / cum_model) ** 2
                    Kg = var_g / (var_g + var_meas)
                    g += Kg * (g_meas - g); var_g *= (1 - Kg)
                    g = max(g, .3)
        if soc is None: soc, var = 1.0, 0.3 ** 2  # no information at all: assume full, wide
        # predict
        e = p_model[i] / 3600
        cum_model += e
        soc -= g * e / WH_NOM
        var += (np.sqrt(var_g) * e / WH_NOM) ** 2 + 1e-9
        pavg += (p_model[i] * g - pavg) / 600
        # floor for what the model cannot see: voltage->SoC ambiguity (3 %), and 12 % error on energy since the last reading
        since = cs[i] - (cs[last_anchor_i] if last_anchor_i >= 0 else 0.0)
        floor2 = 0.03 ** 2 + (0.12 * since / WH_NOM) ** 2
        est_soc[i] = soc; est_sig[i] = np.sqrt(var + (np.sqrt(var_g) * cum_model / WH_NOM) ** 2 + floor2); gs[i] = g

    def tte(i, conservative=False):  # minutes to cutoff from sample i
        s_ = est_soc[i] - (1.28 * est_sig[i] if conservative else 0)
        return max(s_, 0) * WH_NOM / max(pavg_arr[i] * (1 + (0.2 if conservative else 0)), 1) * 60
    # recent-average power (g applied)
    pa = np.convolve(p_model, np.ones(600) / 600, mode='full')[:cut] * gs
    pavg_arr = pa
    true_left = (cut - np.arange(cut)) / 60.0
    return dict(cut_min=cut / 60, soc_t=soc_t, est=est_soc, sig=est_sig, tte=lambda i, c=False: tte(i, c), true_left=true_left)


late_wasted = {}


def evaluate(mode, N=300):
    wasted = []; rows = {30: [], 60: [], 90: []}; unsafe = []; soc_err = {30: [], 60: [], 90: []}
    for k in range(N):
        r = run(1000 + k, mode)
        for m in rows:
            i = m * 60
            if i < len(r['est']) - 300:
                rows[m].append(r['tte'](i) - r['true_left'][i])
                soc_err[m].append(100 * (r['est'][i] - r['soc_t'][i]))
        # SoC-threshold warning: raise "land now" when (estimate - 1.28 sigma) <= 20 %.
        # Failure = never raised, or raised with < 5 min of true runtime left. Also record the true SoC at the warning
        # (a high number means usable battery was wasted).
        cons = r['est'] - 1.28 * r['sig']
        hit = np.where(cons <= 0.20)[0]
        if len(hit) == 0 or (len(r['est']) - hit[0]) / 60 < 5:
            unsafe.append(True)
        else:
            unsafe.append(False); wasted.append(100 * r['soc_t'][hit[0]])
    late_wasted[mode] = np.median(wasted) if wasted else float('nan')
    return rows, soc_err, np.mean(unsafe)


if __name__ == "__main__":
    print("Simulated pack: true capacity 85-100 % of nominal, true loss model differs from repo constants,")
    print("start charge 85-100 %, 3 h walking-style session, 300 random packs per row.\n")
    for mode, label in (("none", "A. repo today: count energy from 100 %, never corrected"),
                        ("start", "B. one typed voltage at plug-in, then counting"),
                        ("periodic", "C. B plus a resting voltage about every 15 min, learns gain g")):
        rows, serr, late = evaluate(mode)
        print(label)
        for m in (30, 60, 90):
            a = np.array(rows[m]); s = np.array(serr[m])
            print(f"   at {m:>2} min: SoC error median {np.median(s):+5.1f} % (|err| P90 {np.percentile(abs(s),90):4.1f} %)   "
                  f"time-left error median {np.median(a):+6.1f} min (|err| P90 {np.percentile(abs(a),90):5.1f} min)")
        print(f"   'land now' at conservative SoC <= 20 %: failed (no warning, or < 5 min left) in {100*late:4.1f} % of runs; "
              f"true SoC when it fired: median {late_wasted[mode]:.0f} %\n")
