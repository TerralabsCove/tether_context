# Lens calibration using a ChArUco board drawn full screen on the Mac, seen by the reCamera stream.
# Follows ../2026-11-05-john-recamera-test/calibrate_screen.py. Differences: it fits two lens models and says
# which fits better (OpenCV fisheye k1..k4, and normal pinhole k1 k2 p1 p2 k3), it works at whatever size the
# stream is, it accepts a handheld camera, and it logs why frames were not saved.
# Move the camera, not the screen. It speaks what view it needs next and beeps when one is saved.
# Usage: calibrate_lens.py --out=<folder> [--url=<rtsp url>] [--square-mm=<measured square>] [--analyze-only] [--selftest]
import ctypes, ctypes.util, glob, json, os, subprocess, sys, threading, time
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|allowed_media_types;video"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import cv2
import numpy as np

URL = "rtsp://192.168.42.1:554/live"
SQUARES = (10, 6)        # big squares, so the board still reads when small or at the image edge
TARGET_VIEWS = 40
# Focal length guesses as a fraction of image width, only used to steer the capture.
F_GUESS = {"pinhole": 0.547, "fisheye": 0.335}   # 2.9 mm stock lens and 1.8 mm fisheye, 2.8 um pixels at 1920
MIN_CORNERS = 12
BAND = 150               # status strip height, in window pixels
STILL_PX = 3.0           # most the board may move between frames, in pixels at 1920 wide
FISHEYE_FLAGS = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC | cv2.fisheye.CALIB_FIX_SKEW
CRIT = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 200, 1e-7)


def arg(name, default=None):
    return next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), default)


def screen_mm():
    cg = ctypes.CDLL(ctypes.util.find_library("CoreGraphics"))
    class Size(ctypes.Structure):
        _fields_ = [("w", ctypes.c_double), ("h", ctypes.c_double)]
    cg.CGMainDisplayID.restype = ctypes.c_uint32
    cg.CGDisplayScreenSize.restype = Size
    cg.CGDisplayScreenSize.argtypes = [ctypes.c_uint32]
    cg.CGDisplayPixelsWide.argtypes = [ctypes.c_uint32]
    cg.CGDisplayPixelsHigh.argtypes = [ctypes.c_uint32]
    d = cg.CGMainDisplayID()
    return cg.CGDisplayScreenSize(d).w, cg.CGDisplayPixelsWide(d), cg.CGDisplayPixelsHigh(d)


def make_board(square_mm):
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    return cv2.aruco.CharucoBoard(SQUARES, square_mm, square_mm * 0.72, d)


def make_detector(board):
    dp = cv2.aruco.DetectorParameters()
    dp.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    dp.adaptiveThreshWinSizeMin, dp.adaptiveThreshWinSizeMax, dp.adaptiveThreshWinSizeStep = 3, 43, 8
    dp.minMarkerPerimeterRate = 0.015
    dp.polygonalApproxAccuracyRate = 0.06  # a wide lens bends marker edges
    cp = cv2.aruco.CharucoParameters()
    cp.tryRefineMarkers = True
    return cv2.aruco.CharucoDetector(board, cp, dp)


def detect(detector, gray):
    corners, ids, _, _ = detector.detectBoard(gray)
    if ids is None or len(ids) < MIN_CORNERS:
        return None, None
    return corners, ids


def rough_pose(o, i, w, h):
    # Board pose from a guessed lens, good enough to steer the capture. Tries both lens types, keeps the better.
    o64, i64 = o.reshape(-1, 1, 3).astype(np.float64), i.reshape(-1, 1, 2).astype(np.float64)
    best = None
    for model, frac in F_GUESS.items():
        K = np.array([[frac * w, 0, w / 2], [0, frac * w, h / 2], [0, 0, 1.0]])
        if model == "fisheye":
            ok, r, t = cv2.solvePnP(o64, cv2.fisheye.undistortPoints(i64, K, np.zeros(4)), np.eye(3), None)
            p, _ = cv2.fisheye.projectPoints(o64.reshape(1, -1, 3), r, t, K, np.zeros(4))
        else:
            ok, r, t = cv2.solvePnP(o64, i64, K, None)
            p, _ = cv2.projectPoints(o64, r, t, K, None)
        e = float(np.sqrt(np.mean(np.sum((p.reshape(-1, 2) - i64.reshape(-1, 2)) ** 2, axis=1))))
        if best is None or e < best[0]:
            best = (e, r, t, model)
    return best[1], best[2], best[3]


def edge_sharpness(gray, corners):
    # Sharpness only around the board, so background clutter doesn't count.
    x, y, w, h = cv2.boundingRect(corners.astype(np.float32))
    roi = gray[max(y, 0):y + h, max(x, 0):x + w]
    return float(cv2.Laplacian(roi, cv2.CV_64F).var()) if roi.size else 0.0


def theta_of(rd, D):
    # Invert the fisheye model: rd = theta * (1 + k1 t^2 + k2 t^4 + k3 t^6 + k4 t^8). Returns nan if it folds back.
    k1, k2, k3, k4 = [float(x) for x in np.ravel(D)[:4]]
    t = float(rd)
    for _ in range(50):
        t2 = t * t
        f = t * (1 + k1 * t2 + k2 * t2**2 + k3 * t2**3 + k4 * t2**4) - rd
        df = 1 + 3 * k1 * t2 + 5 * k2 * t2**2 + 7 * k3 * t2**3 + 9 * k4 * t2**4
        if df <= 1e-6:
            return float("nan")
        step = f / df
        t -= step
        if abs(step) < 1e-10:
            break
    return t if 0 <= t < np.pi else float("nan")


def active_rows(gray):
    # Seeed's scaler letterboxes 16:9 into 4:3 with flat grey bars. Find the rows that hold picture.
    flat = (gray.std(axis=1) < 3.0)
    top = 0
    while top < gray.shape[0] // 3 and flat[top]:
        top += 1
    bot = gray.shape[0] - 1
    while bot > 2 * gray.shape[0] // 3 and flat[bot]:
        bot -= 1
    return top, bot


class Fisheye:
    name, label = "fisheye", "OpenCV fisheye (equidistant, k1 k2 k3 k4)"

    @staticmethod
    def fit(obj, img, size):
        o = [x.reshape(1, -1, 3).astype(np.float64) for x in obj]
        i = [x.reshape(1, -1, 2).astype(np.float64) for x in img]
        rms, K, D, rv, tv = cv2.fisheye.calibrate(o, i, size, np.zeros((3, 3)), np.zeros((4, 1)), flags=FISHEYE_FLAGS, criteria=CRIT)
        return float(rms), K, D.ravel(), rv, tv

    @staticmethod
    def project(o, r, t, K, D):
        return cv2.fisheye.projectPoints(o.reshape(1, -1, 3).astype(np.float64), r, t, K, D)[0].reshape(-1, 2)

    @staticmethod
    def off_axis_deg(x, y, K, D):
        return float(np.degrees(theta_of(np.hypot((x - K[0, 2]) / K[0, 0], (y - K[1, 2]) / K[1, 1]), D)))

    @staticmethod
    def straighten(gray, K, D, size):
        Knew = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, size, np.eye(3), balance=0.6)
        return cv2.fisheye.undistortImage(gray, K, D, Knew=Knew)


class Pinhole:
    name, label = "pinhole", "OpenCV pinhole (k1 k2 p1 p2 k3)"

    @staticmethod
    def fit(obj, img, size):
        rms, K, D, rv, tv = cv2.calibrateCamera([x.astype(np.float32) for x in obj], [x.astype(np.float32) for x in img], size, None, None, criteria=CRIT)
        return float(rms), K, D.ravel()[:5], rv, tv

    @staticmethod
    def project(o, r, t, K, D):
        return cv2.projectPoints(o.astype(np.float64), r, t, K, D)[0].reshape(-1, 2)

    @staticmethod
    def off_axis_deg(x, y, K, D):
        n = cv2.undistortPoints(np.array([[[float(x), float(y)]]]), K, D).reshape(2)
        return float(np.degrees(np.arctan(np.hypot(n[0], n[1]))))

    @staticmethod
    def straighten(gray, K, D, size):
        Knew, _ = cv2.getOptimalNewCameraMatrix(K, D, size, 0.6)
        return cv2.undistort(gray, K, D, None, Knew)


def pick(fits):
    # fits: name -> (model, fit result). The fisheye model can also describe a normal lens, so a tie goes to
    # the simpler pinhole model. Fisheye wins only when it fits clearly better.
    if "pinhole" in fits and "fisheye" in fits:
        return fits["pinhole"] if fits["pinhole"][1][0] <= 1.1 * fits["fisheye"][1][0] else fits["fisheye"]
    return next(iter(fits.values()))


def fit_dropping(model, obj, img, size):
    # A calibration can throw on one awkward view. Drop views one at a time until it runs.
    keep = list(range(len(obj)))
    for _ in range(6):
        try:
            return model.fit([obj[k] for k in keep], [img[k] for k in keep], size) + (keep,)
        except cv2.error:
            for j in range(len(keep)):
                trial = keep[:j] + keep[j + 1:]
                try:
                    model.fit([obj[k] for k in trial], [img[k] for k in trial], size)
                    keep = trial
                    break
                except cv2.error:
                    continue
            else:
                break
    return None


def view_errors(model, obj, img, K, D, rv, tv):
    return np.array([float(np.sqrt(np.mean(np.sum((model.project(o, r, t, K, D) - i.reshape(-1, 2)) ** 2, axis=1))))
                     for o, i, r, t in zip(obj, img, rv, tv)])


def describe(model, obj, img, size, rows, fitres):
    rms, K, D, rv, tv = fitres
    w, h = size
    fx, fy, cx, cy = float(K[0, 0]), float(K[1, 1]), float(K[0, 2]), float(K[1, 2])
    pts = np.concatenate([i.reshape(-1, 2) for i in img])
    far = float(np.max([model.off_axis_deg(x, y, K, D) for x, y in pts[::3]]))   # widest angle a corner was seen at
    top, bot = rows
    def span(a, b):
        return model.off_axis_deg(*a, K, D) + model.off_axis_deg(*b, K, D)
    def inside(a, b):
        return bool(max(model.off_axis_deg(*a, K, D), model.off_axis_deg(*b, K, D)) <= far * 1.03)
    H, V, Dg = ((0, cy), (w - 1, cy)), ((cx, top), (cx, bot)), ((0, top), (w - 1, bot))
    e = view_errors(model, obj, img, K, D, rv, tv)
    out = {
        "model": model.label, "rms_px": round(rms, 3), "worst_view_px": round(float(e.max()), 3),
        "fx": round(fx, 2), "fy": round(fy, 2), "cx": round(cx, 2), "cy": round(cy, 2),
        "dist": [round(float(x), 5) for x in D],
        "hfov_deg": round(span(*H), 1), "vfov_deg": round(span(*V), 1), "dfov_deg": round(span(*Dg), 1),
        # FOV is only measured where board corners were seen. False means the number is extrapolated.
        "hfov_inside_measured_area": inside(*H), "vfov_inside_measured_area": inside(*V), "dfov_inside_measured_area": inside(*Dg),
        "measured_out_to_deg_off_axis": round(far, 1),
    }
    # The same lens values at the camera's other stream sizes. The scaler shrinks the whole 1920x1080 picture and
    # letterboxes 4:3. Derived, not measured.
    if (w, h) == (1920, 1080):
        def scaled(s, pad):
            return {"fx": round(fx * s, 2), "fy": round(fy * s, 2), "cx": round((cx + 0.5) * s - 0.5, 2),
                    "cy": round((cy + 0.5) * s - 0.5 + pad, 2), "dist": out["dist"]}
        out["derived_not_measured"] = {"1280x720": scaled(2 / 3, 0), "640x480_letterboxed": scaled(1 / 3, 60)}
    return out


def calibrate(folder, square_mm):
    board = make_board(square_mm)
    detector = make_detector(board)
    obj, img, sharp = [], [], []
    size, rows, first = None, None, None
    files = sorted(glob.glob(f"{folder}/view_*.png"))
    for f in files:
        gray = cv2.imread(f, 0)
        size = gray.shape[::-1]
        if rows is None:
            rows, first = active_rows(gray), gray
        corners, ids = detect(detector, gray)
        if corners is None:
            continue
        o, i = board.matchImagePoints(corners, ids)
        obj.append(o); img.append(i); sharp.append(edge_sharpness(gray, corners))
    detected = len(obj)
    if detected < 10:
        sys.exit(f"only {detected} usable views of {len(files)}; need at least 10")
    w, h = size
    result = {
        "image_size": [w, h], "picture_rows": [int(rows[0]), int(rows[1])], "square_mm": round(square_mm, 3),
        "views_captured": len(files), "views_detected": detected,
    }
    # Each model: fit, drop its own worst views once, refit.
    fits = {}
    for mm in (Pinhole, Fisheye):
        r = fit_dropping(mm, obj, img, size)
        if r is None:
            result[mm.name] = None
            continue
        keep = r[5]
        e = view_errors(mm, [obj[k] for k in keep], [img[k] for k in keep], *r[1:5])
        good = e < max(1.0 * w / 1920, 2.5 * np.median(e))
        fitres = r[:5]
        if good.sum() >= 10 and not good.all():
            keep2 = [k for k, g in zip(keep, good) if g]
            try:
                fitres, keep = mm.fit([obj[k] for k in keep2], [img[k] for k in keep2], size), keep2
            except cv2.error:
                pass
        fits[mm.name] = (mm, fitres, keep)
        result[mm.name] = describe(mm, [obj[k] for k in keep], [img[k] for k in keep], size, rows, fitres)
        result[mm.name]["views_used"] = len(keep)
        result[mm.name]["corners_used"] = int(sum(len(img[k]) for k in keep))
    if not fits:
        sys.exit("calibration did not converge with either lens model; capture more varied views")
    bm, (rms, K, D, rv, tv), keep = pick(fits)
    obj, img, sharp = ([x[k] for k in keep] for x in (obj, img, sharp))
    result["better_fit"] = bm.name
    # Uncertainty on the focal length: refit the better model on resampled views.
    rng = np.random.default_rng(1)
    boot = []
    for _ in range(20):
        idx = rng.choice(len(obj), len(obj), replace=True)
        try:
            boot.append(bm.fit([obj[j] for j in idx], [img[j] for j in idx], size)[1][0, 0])
        except cv2.error:
            pass
    result["fx_resampled_mean_sd"] = [round(float(np.mean(boot)), 2), round(float(np.std(boot)), 2)] if boot else None
    tilts = []
    for rr in rv:
        R, _ = cv2.Rodrigues(rr)
        tilts.append(float(np.degrees(np.arccos(min(1.0, abs(R[2, 2]))))))
    pts = np.concatenate([i.reshape(-1, 2) for i in img])
    result["tilt_deg_median_max"] = [round(float(np.median(tilts)), 1), round(float(np.max(tilts)), 1)]
    result["corner_coverage_px"] = [[round(float(pts[:, 0].min())), round(float(pts[:, 0].max()))],
                                    [round(float(pts[:, 1].min())), round(float(pts[:, 1].max()))]]
    # Focus curve: board sharpness against distance.
    bins = {}
    for t, s in zip(tv, sharp):
        bins.setdefault(int(float(np.linalg.norm(t)) / 10 // 5 * 5), []).append(s)
    result["focus_by_distance_cm"] = {str(k): round(float(np.median(v)), 1) for k, v in sorted(bins.items())}
    with open(f"{folder}/calibration.json", "w") as f:
        json.dump(result, f, indent=2)
    # A straightened copy of the first view, to check by eye that straight things come out straight.
    cv2.imwrite(f"{folder}/undistort_check.png", bm.straighten(first, K, D, size))
    cover = np.full((h, w, 3), 40, np.uint8)
    for p in pts:
        cv2.circle(cover, (int(p[0]), int(p[1])), max(3, w // 240), (80, 255, 80), -1)
    cv2.imwrite(f"{folder}/coverage.png", cover)
    return result


def run_capture(folder, url):
    state = {"frame": None, "n": 0, "stop": False}

    def reader():
        while not state["stop"]:
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG,
                                   [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000, cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000])
            while cap.isOpened() and not state["stop"]:
                ok, fr = cap.read()
                if not ok:
                    break
                state["frame"], state["n"] = fr, state["n"] + 1
            cap.release()
            time.sleep(0.5)

    threading.Thread(target=reader, daemon=True).start()
    width_mm, W, H = screen_mm()
    name = "lens calibration board (q to finish)"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    side = min(W // SQUARES[0], (H - BAND) // SQUARES[1])
    drawn_mm = side * width_mm / W
    board = make_board(float(drawn_mm))
    detector = make_detector(board)
    with open(f"{folder}/board.json", "w") as f:
        json.dump({"page": [W, H], "squares": SQUARES, "side_points": side, "square_mm_computed": round(drawn_mm, 3)}, f)
    bw, bh = side * SQUARES[0], side * SQUARES[1]
    art = board.generateImage((bw, bh), marginSize=0, borderBits=1)
    page = np.full((H, W, 3), 255, np.uint8)
    x0, y0 = (W - bw) // 2, BAND + (H - BAND - bh) // 2
    page[y0:y0 + bh, x0:x0 + bw] = art[..., None]
    log = open(f"{folder}/capture_log.csv", "a")
    log.write("t,frame,status,corners,moved_px,dist_cm,lens_guess\n")

    # What the calibration still needs: spoken and shown until each is met.
    needs = [
        ("center", 3, "Point the camera straight at the screen from about 30 centimeters"),
        ("left edge", 3, "Turn the camera to the right, until the board sits at the left edge of its view"),
        ("right edge", 3, "Turn the camera to the left, until the board sits at the right edge of its view"),
        ("top edge", 3, "Tilt the camera down, until the board sits at the top edge of its view"),
        ("bottom edge", 3, "Tilt the camera up, until the board sits at the bottom edge of its view"),
        ("top left", 2, "Aim the camera right and down, so the board sits in the top left corner of its view"),
        ("top right", 2, "Aim the camera left and down, so the board sits in the top right corner of its view"),
        ("bottom left", 2, "Aim the camera right and up, so the board sits in the bottom left corner of its view"),
        ("bottom right", 2, "Aim the camera left and up, so the board sits in the bottom right corner of its view"),
        ("from left", 3, "Move to the left of the screen and angle the camera back at it, about 30 degrees"),
        ("from right", 3, "Move to the right of the screen and angle the camera back at it, about 30 degrees"),
        ("from above", 3, "Move above the screen and angle the camera down at it, about 30 degrees"),
        ("from below", 3, "Move below the screen and angle the camera up at it, about 30 degrees"),
        ("close", 3, "Move in close, about 20 centimeters"),
        ("far", 3, "Move back, about 50 centimeters"),
    ]
    got = {k: 0 for k, _, _ in needs}
    seen, count, last_n, last_save, last_say, said = [], 0, 0, 0.0, 0.0, ""
    history, status, preview, cover = [], "waiting for video", None, None
    pw = BAND * 16 // 9
    t0 = time.time()
    while count < TARGET_VIEWS:
        todo = next(((k, s) for k, q, s in needs if got[k] < q), None)
        show = page.copy()
        show[:BAND] = 235
        if preview is not None:
            show[0:BAND, 0:pw] = cv2.resize(preview, (pw, BAND))
            show[0:BAND, pw + 6:2 * pw + 6] = cv2.resize(cover, (pw, BAND))
        tx = 2 * pw + 24
        cv2.putText(show, f"Saved {count}/{TARGET_VIEWS}", (tx, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        cv2.putText(show, status, (tx, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
        cv2.putText(show, todo[1] if todo else "All covered. Keep adding varied views, or press q.", (tx, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)
        cv2.imshow(name, show)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
        if todo and (todo[1] != said or time.time() - last_say > 20) and time.time() - last_say > 5:
            subprocess.Popen(["say", todo[1]])
            said, last_say = todo[1], time.time()
        if state["n"] == last_n or state["frame"] is None:
            continue
        last_n = state["n"]
        frame = state["frame"]
        fh, fw = frame.shape[:2]
        if cover is None:
            cover = np.full((fh, fw, 3), 40, np.uint8)  # dots show where corners have been saved
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids = detect(detector, gray)
        preview = frame.copy()
        def note(s, n=0, moved=-1.0, z=-1.0, lens=""):
            log.write(f"{time.time() - t0:.2f},{last_n},{s},{n},{moved:.2f},{z:.1f},{lens}\n"); log.flush()
        if corners is None:
            status, history = "board not seen", []
            note(status)
            continue
        c = corners.reshape(-1, 2)
        for p in c:
            cv2.circle(preview, (int(p[0]), int(p[1])), max(6, fw // 120), (80, 255, 80), -1)
        pts = {int(i): p for i, p in zip(ids.flatten(), c)}
        history.append(pts)
        history = history[-3:]
        if len(history) < 3:
            continue
        # Still enough: the board moved little between each of the last three frames.
        moved = 0.0
        for a, b in zip(history, history[1:]):
            common = set(a) & set(b)
            moved = max(moved, float(np.median([np.linalg.norm(a[i] - b[i]) for i in common])) if len(common) > 6 else 99.0)
        if moved > STILL_PX * fw / 1920:
            status = "hold still"
            note(status, len(ids), moved)
            continue
        o, i = board.matchImagePoints(corners, ids)
        r, tv, lens = rough_pose(o, i, fw, fh)
        R, _ = cv2.Rodrigues(r)
        n = R[:, 2]
        ax, ay = np.degrees(np.arctan2(n[0], n[2])), np.degrees(np.arctan2(n[1], n[2]))
        cx, cy = c.mean(axis=0) / [fw, fh]
        z = float(np.linalg.norm(tv)) / 10
        sig = np.array([cx, cy, z / 40, ax / 40, ay / 40])
        if not all(np.linalg.norm(sig - s) > 0.12 for s in seen):
            status = "got this one, move to a new view"
            note("repeat view", len(ids), moved, z, lens)
            continue
        if time.time() - last_save < 0.5:
            continue
        seen.append(sig)
        cv2.imwrite(f"{folder}/view_{count:03d}.png", gray)
        for p in c:
            cv2.circle(cover, (int(p[0]), int(p[1])), max(4, fw // 160), (80, 255, 80), -1)
        count += 1; last_save = time.time(); history = []
        status = f"saved: {len(ids)} corners, {z:.0f} cm, tilt {max(abs(ax), abs(ay)):.0f} deg"
        note("saved", len(ids), moved, z, lens)
        subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
        if 0.38 < cx < 0.62 and 0.35 < cy < 0.65: got["center"] += 1
        if cx < 0.30: got["left edge"] += 1
        if cx > 0.70: got["right edge"] += 1
        if cy < 0.33: got["top edge"] += 1
        if cy > 0.67: got["bottom edge"] += 1
        if cy < .42 and cx < .38: got["top left"] += 1
        if cy < .42 and cx > .62: got["top right"] += 1
        if cy > .58 and cx < .38: got["bottom left"] += 1
        if cy > .58 and cx > .62: got["bottom right"] += 1
        if ax > 18: got["from left"] += 1
        if ax < -18: got["from right"] += 1
        if ay > 18: got["from above"] += 1
        if ay < -18: got["from below"] += 1
        if z < 24: got["close"] += 1
        if z > 42: got["far"] += 1
    state["stop"] = True
    log.close()
    cv2.destroyAllWindows(); cv2.waitKey(1)
    print("coverage:", got)
    return count


def selftest(folder, square_mm, kind, size=(1920, 1080)):
    # Render the board through known lens values and check that calibration recovers them and names the lens type.
    folder = f"{folder}/{kind}"
    os.makedirs(folder, exist_ok=True)
    for f in glob.glob(f"{folder}/view_*.png"):
        os.remove(f)
    board = make_board(square_mm)
    AW, AH = SQUARES[0] * 300, SQUARES[1] * 300
    art = board.generateImage((AW, AH), marginSize=0, borderBits=1)
    W, H = size
    s = W / 1920
    rng = np.random.default_rng(3)
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))
    if kind == "fisheye":
        fx, fy, cx, cy = 640.0 * s, 642.0 * s, 955.0 * s, 548.0 * s
        D = np.array([-0.035, 0.012, -0.006, 0.001])
        xn, yn = (gx - cx) / fx, (gy - cy) / fy
        rd = np.hypot(xn, yn)
        th = rd.copy()
        for _ in range(25):  # invert the lens model per pixel
            t2 = th * th
            th -= (th * (1 + D[0] * t2 + D[1] * t2**2 + D[2] * t2**3 + D[3] * t2**4) - rd) / \
                  (1 + 3 * D[0] * t2 + 5 * D[1] * t2**2 + 7 * D[2] * t2**3 + 9 * D[3] * t2**4)
        sc = np.where(rd > 1e-9, np.sin(th) / np.maximum(rd, 1e-9), 1.0)
        rays = np.dstack([xn * sc, yn * sc, np.cos(th)])
        max_off = 62
    else:
        fx, fy, cx, cy = 1050.0 * s, 1052.0 * s, 955.0 * s, 548.0 * s
        D = np.array([-0.30, 0.10, 0.0, 0.0, -0.015])
        K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]])
        und = cv2.undistortPoints(np.stack([gx, gy], -1).reshape(-1, 1, 2), K, D).reshape(H, W, 2)
        rays = np.dstack([und, np.ones((H, W))])
        max_off = 30
    bw, bh = SQUARES[0] * square_mm, SQUARES[1] * square_mm
    n = 0
    for k in range(34):
        off = np.radians(rng.uniform(0, max_off)) if k > 3 else 0.0   # how far off axis the board centre sits
        phi = rng.uniform(0, 2 * np.pi)
        d = np.array([np.sin(off) * np.cos(phi), np.sin(off) * np.sin(phi), np.cos(off)])
        axis = np.cross([0, 0, 1.0], d)
        R0 = cv2.Rodrigues(axis / np.linalg.norm(axis) * off)[0] if off > 1e-6 else np.eye(3)
        R = R0 @ cv2.Rodrigues(rng.uniform(-0.45, 0.45, 3) * np.array([1, 1, 0.5]))[0]
        tvec = d * rng.uniform(150, 380) * (1.0 if kind == "fisheye" else 1.5) - R @ np.array([bw / 2, bh / 2, 0])
        nrm = R[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (nrm @ tvec) / (rays @ nrm)
        b = (rays * t[..., None] - tvec) @ R
        mx = np.where(t > 0, b[..., 0] / bw * AW, -1).astype(np.float32)
        my = np.where(t > 0, b[..., 1] / bh * AH, -1).astype(np.float32)
        im = cv2.remap(art, mx, my, cv2.INTER_AREA, borderValue=90)
        im = np.clip(cv2.GaussianBlur(im, (3, 3), 0.8).astype(np.float64) + rng.normal(0, 3, im.shape), 0, 255).astype(np.uint8)
        cv2.imwrite(f"{folder}/view_{n:03d}.png", im); n += 1
    r = calibrate(folder, square_mm)
    got = r[kind]
    ok = (r["better_fit"] == kind and abs(got["fx"] - fx) < 0.01 * fx and abs(got["cx"] - cx) < 5 * s + 1
          and abs(got["cy"] - cy) < 5 * s + 1 and got["rms_px"] < 0.6)
    print(f"SELFTEST {kind}", "PASS" if ok else "FAIL", f"| true fx={fx:.1f} cx={cx:.1f} cy={cy:.1f} | got better_fit={r['better_fit']}",
          f"fx={got['fx']} cx={got['cx']} cy={got['cy']} rms={got['rms_px']} hfov={got['hfov_deg']}",
          f"| views {got['views_used']}/{r['views_captured']} | other model rms:",
          {k: (r[k] or {}).get("rms_px") for k in ("pinhole", "fisheye") if k != kind})
    return ok


if __name__ == "__main__":
    out = arg("out", "calib_run")
    os.makedirs(out, exist_ok=True)
    if "--selftest" in sys.argv:
        w = int(arg("width", 1920))
        results = [selftest(out, 30.0, kind, (w, w * 9 // 16)) for kind in ("pinhole", "fisheye")]
        sys.exit(0 if all(results) else 1)
    square = float(arg("square-mm", 30.0))
    if "--analyze-only" not in sys.argv:
        n = run_capture(out, arg("url", URL))
        print(f"captured {n} views in {out}")
    if arg("square-mm") is None and os.path.exists(f"{out}/board.json"):
        square = json.load(open(f"{out}/board.json"))["square_mm_computed"]
    print(json.dumps(calibrate(out, square), indent=1))
