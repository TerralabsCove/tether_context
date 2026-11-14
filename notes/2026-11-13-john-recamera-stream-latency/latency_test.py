# Measures how far behind real time the reCamera video stream is when it reaches the Mac, and how steady it is.
# The Mac draws a moving time code full screen. The camera looks at the screen. The Mac reads the time code back
# out of each video frame and compares it with its own clock. Delay = time the frame arrived - time it shows.
# The delay includes the screen's own lag (about one or two refreshes), so treat it as a slight overestimate.
# Frame arrival times are logged even when the camera cannot see the screen, so rate and stalls are always measured.
# Usage: latency_test.py --out=<folder> --label=<name> [--url=rtsp://192.168.42.1:554/live] [--seconds=30] [--wait=300]
#        [--giveup=150] [--ffopts=<OpenCV ffmpeg capture options>]
#        latency_test.py --selftest
import json, os, socket, statistics as st, subprocess, sys, threading, time
# Decoder settings matter: by default ffmpeg decodes on many threads and holds one frame back per thread.
FFOPTS = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--ffopts=")),
              "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay|threads;1|allowed_media_types;video")
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = FFOPTS
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import cv2
import numpy as np

CW, CH = 1000, 500                       # the pattern's own coordinate system
MARKERS = {0: (20, 20), 1: (860, 20), 2: (20, 360), 3: (860, 360)}   # id -> top-left corner; each is MS wide
MS = 120
BITS_X, BITS_Y, CELL = 180, 30, 64       # 10 cells: white reference, black reference, 8 Gray-code bits
TR_X0, TR_X1, TR_Y0, TR_Y1 = 40, 960, 180, 320   # track the bar sweeps along, once a second
BAR = 28
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
SKIP_S = 5.0                             # the camera sends a few seconds of old video on connect; ignore that


def arg(name, default=None):
    return next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), default)


def base_pattern():
    img = np.full((CH, CW), 255, np.uint8)
    for i, (x, y) in MARKERS.items():
        img[y:y + MS, x:x + MS] = cv2.aruco.generateImageMarker(DICT, i, MS)
    img[TR_Y0:TR_Y1, TR_X0:TR_X1] = 0
    img[BITS_Y:BITS_Y + 100, BITS_X + CELL + 4:BITS_X + 2 * CELL - 4] = 0      # black reference cell
    cv2.rectangle(img, (BITS_X + 4, BITS_Y), (BITS_X + CELL - 4, BITS_Y + 100), 0, 2)   # white reference cell outline
    return img


def draw(base, t):
    # t in seconds. Coarse count flips half way along the sweep, so it is steady when the bar wraps.
    img = base.copy()
    coarse = int(np.floor(t + 0.5)) % 256
    gray_code = coarse ^ (coarse >> 1)
    for b in range(8):
        if not (gray_code >> (7 - b)) & 1:
            x = BITS_X + (b + 2) * CELL
            img[BITS_Y:BITS_Y + 100, x + 4:x + CELL - 4] = 0
    w = TR_X1 - TR_X0
    xc = (t % 1.0) * w
    for x in (xc - w, xc, xc + w):       # draw wrapped copies so the bar leaves one end and enters the other
        a, b = int(round(x - BAR / 2)), int(round(x + BAR / 2))
        a, b = max(a, 0), min(b, w)
        if b > a:
            img[TR_Y0 + 10:TR_Y1 - 10, TR_X0 + a:TR_X0 + b] = 255
    return img


def canon_corners(i):
    x, y = MARKERS[i]
    return np.array([[x, y], [x + MS, y], [x + MS, y + MS], [x, y + MS]], np.float32)


DETECTOR = cv2.aruco.ArucoDetector(DICT)


def decode(gray):
    # Returns the time (0..256 s) shown in this frame, or None.
    corners, ids, _ = DETECTOR.detectMarkers(gray)
    if ids is None:
        return None
    src, dst = [], []
    for c, i in zip(corners, ids.flatten()):
        if int(i) in MARKERS:
            src.append(c.reshape(4, 2)); dst.append(canon_corners(int(i)))
    if len(src) < 3:
        return None
    H, _ = cv2.findHomography(np.concatenate(src), np.concatenate(dst))
    if H is None:
        return None
    flat = cv2.warpPerspective(gray, H, (CW, CH))
    def cell(k):
        x = BITS_X + k * CELL
        return float(flat[BITS_Y + 25:BITS_Y + 75, x + 18:x + CELL - 18].mean())
    white, black = cell(0), cell(1)
    if white - black < 30:
        return None
    g = 0
    for b in range(8):
        g = (g << 1) | (1 if cell(b + 2) > (white + black) / 2 else 0)
    coarse, s = g, g >> 1
    while s:
        coarse ^= s; s >>= 1
    prof = flat[TR_Y0 + 25:TR_Y1 - 25, TR_X0:TR_X1].astype(np.float32).mean(axis=0)
    prof = np.clip(prof - np.percentile(prof, 20) - 0.15 * (white - black), 0, None)
    if prof.max() < 0.15 * (white - black):
        return None
    ang = 2 * np.pi * (np.arange(len(prof)) + 0.5) / len(prof)
    f = (np.arctan2((prof * np.sin(ang)).sum(), (prof * np.cos(ang)).sum()) / (2 * np.pi)) % 1.0
    k = int(np.ceil(coarse - 0.5 - f))
    return (k + f) % 256


def delay_of(t_recv, t_code):
    d = (t_recv - t_code) % 256
    return d - 256 if d > 128 else d


def summarise(arrivals, delays, seconds):
    out = {"frames": len(arrivals)}
    if len(arrivals) > 2:
        gaps = np.diff(arrivals) * 1000
        out.update({"fps": round((len(arrivals) - 1) / (arrivals[-1] - arrivals[0]), 2),
                    "gap_ms_median": round(float(np.median(gaps)), 1), "gap_ms_p95": round(float(np.percentile(gaps, 95)), 1),
                    "gap_ms_p99": round(float(np.percentile(gaps, 99)), 1), "gap_ms_max": round(float(gaps.max()), 1),
                    "stalls_over_200ms": int((gaps > 200).sum()), "stalls_over_500ms": int((gaps > 500).sum())})
    if len(delays) > 5:
        d = np.array(delays) * 1000
        med = float(np.median(d))
        # A misread coarse bit moves a reading by exactly one second. Put those back.
        fixed = np.where(np.abs(d - med - 1000) < 300, d - 1000, np.where(np.abs(d - med + 1000) < 300, d + 1000, d))
        out.update({"delay_samples": len(d), "delay_fixed_by_1s": int((fixed != d).sum()),
                    "delay_ms_median": round(float(np.median(fixed)), 1), "delay_ms_p5": round(float(np.percentile(fixed, 5)), 1),
                    "delay_ms_p95": round(float(np.percentile(fixed, 95)), 1), "delay_ms_p99": round(float(np.percentile(fixed, 99)), 1),
                    "delay_ms_max": round(float(fixed.max()), 1), "delay_ms_min": round(float(fixed.min()), 1)})
    return out


def run():
    out, label = arg("out", "latency_run"), arg("label", "run")
    url, seconds, wait = arg("url", "rtsp://192.168.42.1:554/live"), float(arg("seconds", 30)), float(arg("wait", 0))
    os.makedirs(out, exist_ok=True)
    host = url.split("//")[1].split("/")[0].split(":")[0]
    t_end = time.time() + wait
    need, local_ip, told = arg("need-local-prefix", ""), "", False
    while wait:                           # for the Wi-Fi run: wait for the camera to become reachable
        try:
            c = socket.create_connection((host, 554), timeout=2)
            local_ip = c.getsockname()[0]; c.close()
            # The Mac also has a route to the camera through the USB cable. Only accept the path we mean to test.
            if local_ip.startswith(need):
                break
            if not told:
                subprocess.Popen(["say", "The camera answers, but through the cable, not Wi-Fi. Still waiting."]); told = True
        except OSError:
            pass
        if time.time() > t_end:
            subprocess.run(["say", "Could not reach the camera over Wi-Fi. Giving up."]); sys.exit(1)
        time.sleep(2)
    T0 = time.time()
    state = {"frame": None, "t": 0.0, "n": 0, "stop": False, "size": None}
    arrivals = []

    def reader():
        while not state["stop"]:
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG, [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000, cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000,
                                                         cv2.CAP_PROP_N_THREADS, int(arg("threads", 1))])
            while cap.isOpened() and not state["stop"]:
                ok, fr = cap.read()
                if not ok:
                    break
                t = time.time() - T0
                arrivals.append(t)
                state["frame"], state["t"], state["n"], state["size"] = fr, t, state["n"] + 1, fr.shape[:2]
            cap.release()
            arrivals.append(float("nan"))  # marks a reconnect
            time.sleep(0.5)

    threading.Thread(target=reader, daemon=True).start()
    pings = []                             # (time, round trip ms), to tell a radio outage from a stalled stream

    def pinger():
        import re
        p = subprocess.Popen(["ping", "-i", "0.2", host], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        for line in p.stdout:
            m = re.search(r"time=([0-9.]+) ms", line)
            if m:
                pings.append((time.time() - T0, float(m.group(1))))
            if state["stop"]:
                break
        p.terminate()

    threading.Thread(target=pinger, daemon=True).start()
    samples, misses = [], 0

    def worker():                          # decodes the newest frame; skips frames if it falls behind
        nonlocal misses
        last = 0
        while not state["stop"]:
            if state["n"] == last or state["frame"] is None:
                time.sleep(0.002); continue
            last, fr, t = state["n"], state["frame"], state["t"]
            code = decode(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY))
            if code is None:
                misses += 1
            else:
                samples.append((t, delay_of(t, code)))

    threading.Thread(target=worker, daemon=True).start()
    name = f"stream delay test: {label} (q to stop)"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    probe = np.full((100, 100), 255, np.uint8)
    cv2.imshow(name, probe); cv2.waitKey(50)
    try:
        _, _, W, H = cv2.getWindowImageRect(name)
    except cv2.error:
        W, H = 0, 0
    if W < 800 or H < 500:
        W, H = 1512, 982
    s = min(W / CW, (H - 90) / CH)
    pw, ph = int(CW * s), int(CH * s)
    ox, oy = (W - pw) // 2, 10
    base = base_pattern()
    page = np.full((H, W), 255, np.uint8)
    started, said, frames_drawn = None, 0.0, 0
    subprocess.Popen(["say", "Point the camera at the screen so it sees all four corner squares."])
    while True:
        now = time.time() - T0
        page[oy:oy + ph, ox:ox + pw] = cv2.resize(draw(base, now), (pw, ph), interpolation=cv2.INTER_NEAREST)
        page[H - 70:H] = 255
        recent = [d for t, d in samples if now - t < 1.0]
        if started is None:
            msg = f"waiting for the camera to see the pattern. frames in: {state['n']}  read: {len(samples)}"
            if len(recent) >= 10:
                started = now
                subprocess.Popen(["say", f"Recording for {seconds:.0f} seconds. Keep the camera still."])
            elif now > float(arg("giveup", 150)):
                break
        else:
            msg = f"recording {max(0, seconds - (now - started)):.0f} s left. delay now {1000 * st.median(recent):.0f} ms" if recent else "pattern lost"
            if now - started >= seconds:
                break
        cv2.putText(page, msg + f"   [{label}, {state['size']}]", (20, H - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
        cv2.imshow(name, page)
        frames_drawn += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    t_stop = time.time() - T0
    state["stop"] = True
    cv2.destroyAllWindows(); cv2.waitKey(1)
    t_from = (started if started is not None else 0.0) + (0.0 if started is not None and started > SKIP_S else SKIP_S)
    arr = [a for a in arrivals if a == a and a >= t_from]
    result = {"label": label, "url": url, "mac_address_used": local_ip, "ffmpeg_options": FFOPTS, "decoder_threads": int(arg("threads", 1)), "frame_size": state["size"], "measured_s": round(t_stop - t_from, 1),
              "pattern_seen": started is not None, "frames_not_decoded": misses, "reconnects": max(0, sum(1 for a in arrivals if a != a) - 1),
              "screen_draw_fps": round(frames_drawn / max(t_stop, 1e-6), 1),
              **summarise(arr, [d for t, d in samples if t >= t_from], seconds)}
    pg = np.array([q for q in pings if q[0] >= t_from])
    if len(pg) > 5:
        gaps = np.diff(pg[:, 0])
        result.update({"ping_replies": len(pg), "ping_ms_median": round(float(np.median(pg[:, 1])), 1),
                       "ping_ms_p95": round(float(np.percentile(pg[:, 1], 95)), 1), "ping_ms_max": round(float(pg[:, 1].max()), 1),
                       "ping_longest_silence_s": round(float(gaps.max()), 2), "ping_silences_over_1s": int((gaps > 1.0).sum())})
    json.dump(result, open(f"{out}/{label}.json", "w"), indent=1)
    np.savez_compressed(f"{out}/{label}_raw.npz", arrivals=np.array(arrivals), samples=np.array(samples), pings=np.array(pings))
    print(json.dumps(result, indent=1))
    subprocess.run(["say", "Test done."])


def selftest():
    base = base_pattern()
    rng = np.random.default_rng(4)
    errs, fails = [], 0
    for trial in range(300):
        t = rng.uniform(0, 250)
        exposure = rng.uniform(0.005, 0.033)
        shots = [draw(base, t + dt).astype(np.float32) for dt in np.linspace(-exposure / 2, exposure / 2, 7)]
        screen = np.full((640, 1100), 255, np.float32)
        screen[70:70 + CH, 50:50 + CW] = np.mean(shots, axis=0)
        W, H = (1920, 1080) if trial % 2 else (640, 480)
        scale = rng.uniform(0.45, 0.8) * W / 1100
        src = np.float32([[0, 0], [1100, 0], [1100, 640], [0, 640]])
        dst = src * scale + [rng.uniform(0, W - 1100 * scale), rng.uniform(0, max(1, H - 640 * scale))]
        dst += rng.uniform(-0.04, 0.04, (4, 2)) * 1100 * scale
        frame = cv2.warpPerspective(screen, cv2.getPerspectiveTransform(src, dst.astype(np.float32)), (W, H), borderValue=120)
        frame = np.clip(cv2.GaussianBlur(frame, (5, 5), 1.2) * rng.uniform(0.6, 1.0) + rng.normal(0, 4, frame.shape), 0, 255).astype(np.uint8)
        code = decode(frame)
        if code is None:
            fails += 1; continue
        e = (code - t + 128) % 256 - 128
        errs.append(e * 1000)
    errs = np.array(errs)
    print(f"selftest: decoded {len(errs)} of 300, failed {fails}; error ms median {np.median(errs):+.1f}, "
          f"p95 abs {np.percentile(np.abs(errs), 95):.1f}, max abs {np.abs(errs).max():.1f}")
    # At 640 x 480 with the screen small in view, one camera pixel is about 4 ms of bar travel, so allow 15 ms.
    ok = len(errs) > 270 and abs(np.median(errs)) < 3 and np.percentile(np.abs(errs), 95) < 15 and np.abs(errs).max() < 30
    print("SELFTEST", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else run()
