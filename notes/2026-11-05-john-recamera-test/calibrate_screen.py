# Lens calibration using a ChArUco board drawn full screen on the Mac, seen by the reCamera stream.
# Move the camera, not the screen. It speaks what view it needs next and beeps when one is saved.
# Usage: calibrate_screen.py --out=<folder> [--square-mm=<measured square size>] [--analyze-only] [--selftest]
import ctypes, ctypes.util, glob, json, os, subprocess, sys, threading, time
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|allowed_media_types;video"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import cv2
import numpy as np

URL = "rtsp://192.168.42.1:554/live"
SQUARES = (16, 10)
TARGET_VIEWS = 45
KGUESS = np.array([[2240.0, 0, 960], [0, 2240, 540], [0, 0, 1]])
MIN_CORNERS = 20
BAND = 70  # status strip height, in window pixels


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


def detect(detector, gray):
    corners, ids, _, _ = detector.detectBoard(gray)
    if ids is None or len(ids) < MIN_CORNERS:
        return None, None
    return corners, ids


def edge_sharpness(gray, corners):
    # Sharpness only around the board, so background clutter doesn't count.
    x, y, w, h = cv2.boundingRect(corners.astype(np.float32))
    roi = gray[max(y, 0):y + h, max(x, 0):x + w]
    return float(cv2.Laplacian(roi, cv2.CV_64F).var()) if roi.size else 0.0


def calibrate(folder, square_mm):
    board = make_board(square_mm)
    detector = cv2.aruco.CharucoDetector(board)
    obj, img, names, sharp = [], [], [], []
    size = None
    for f in sorted(glob.glob(f"{folder}/view_*.png")):
        gray = cv2.imread(f, 0)
        size = gray.shape[::-1]
        corners, ids = detect(detector, gray)
        if corners is None:
            continue
        o, i = board.matchImagePoints(corners, ids)
        obj.append(o); img.append(i); names.append(os.path.basename(f)); sharp.append(edge_sharpness(gray, corners))
    if len(obj) < 8:
        sys.exit(f"only {len(obj)} usable views; need at least 8")
    flags = cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_FIX_K3  # k1 and k2 only; this lens does not support more
    rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj, img, size, None, None, flags=flags)
    # Drop the worst views once, then refit.
    def errors():
        out = []
        for o, i, r, t in zip(obj, img, rvecs, tvecs):
            p, _ = cv2.projectPoints(o, r, t, K, dist)
            out.append(float(np.sqrt(np.mean(np.sum((p - i) ** 2, axis=2)))))
        return np.array(out)
    e = errors()
    keep = e < max(1.0, 2.5 * np.median(e))
    if keep.sum() >= 8 and not keep.all():
        obj = [x for x, k in zip(obj, keep) if k]; img = [x for x, k in zip(img, keep) if k]
        names = [x for x, k in zip(names, keep) if k]; sharp = [x for x, k in zip(sharp, keep) if k]
        rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj, img, size, None, None, flags=flags)
    # Uncertainty on the intrinsics: refit on resampled views.
    rng = np.random.default_rng(1)
    boot = []
    for _ in range(20):
        idx = rng.choice(len(obj), len(obj), replace=True)
        boot.append(cv2.calibrateCamera([obj[i] for i in idx], [img[i] for i in idx], size, None, None, flags=flags)[1][0, 0])
    tilts = []
    for r in rvecs:
        R, _ = cv2.Rodrigues(r)
        tilts.append(float(np.degrees(np.arccos(abs(R[2, 2])))))
    w, h = size
    pts = np.concatenate(img).reshape(-1, 2)
    result = {
        "image_size": [w, h], "views_used": len(obj), "views_rejected": int((~keep).sum()),
        "rms_px": round(float(rms), 3), "square_mm": square_mm,
        "fx": round(float(K[0, 0]), 1), "fy": round(float(K[1, 1]), 1),
        "cx": round(float(K[0, 2]), 1), "cy": round(float(K[1, 2]), 1),
        "dist_k1_k2_p1_p2_k3": [round(float(x), 4) for x in dist.ravel()[:5]],
        "hfov_deg": round(float(2 * np.degrees(np.arctan(w / 2 / K[0, 0]))), 1),
        "vfov_deg": round(float(2 * np.degrees(np.arctan(h / 2 / K[1, 1]))), 1),
        "fx_resampled_mean_sd": [round(float(np.mean(boot)), 1), round(float(np.std(boot)), 1)],
        "tilt_deg_median_max": [round(float(np.median(tilts)), 1), round(float(np.max(tilts)), 1)],
        "corner_coverage_px": [[round(float(pts[:, 0].min())), round(float(pts[:, 0].max()))],
                               [round(float(pts[:, 1].min())), round(float(pts[:, 1].max()))]],
    }
    # Distortion size: how far a point near the image corner moves.
    corner = np.array([[[w - 1.0, h - 1.0]]], np.float64)
    und = cv2.undistortPoints(corner, K, dist, P=K)
    result["corner_shift_px"] = round(float(np.linalg.norm(und - corner)), 1)
    # Focus curve: board sharpness against distance.
    curve = sorted((float(t[2][0]) / 10, s) for t, s in zip(tvecs, sharp))
    bins = {}
    for d, s in curve:
        bins.setdefault(int(d // 5 * 5), []).append(s)
    result["focus_by_distance_cm"] = {str(k): round(float(np.median(v)), 1) for k, v in sorted(bins.items())}
    with open(f"{folder}/calibration.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


def run_capture(folder, square_mm):
    state = {"frame": None, "n": 0, "stop": False}

    def reader():
        while not state["stop"]:
            cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG,
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
    name = "calibration board (q to finish)"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    side = min(W // SQUARES[0], (H - BAND) // SQUARES[1])
    drawn_mm = side * width_mm / W
    board = make_board(float(drawn_mm))
    detector = cv2.aruco.CharucoDetector(board)
    with open(f"{folder}/board.json", "w") as f:
        json.dump({"page": [W, H], "side_points": side, "square_mm_computed": round(drawn_mm, 3)}, f)
    bw, bh = side * SQUARES[0], side * SQUARES[1]
    art = board.generateImage((bw, bh), marginSize=0, borderBits=1)
    page = np.full((H, W, 3), 255, np.uint8)
    x0, y0 = (W - bw) // 2, BAND + (H - BAND - bh) // 2
    page[y0:y0 + bh, x0:x0 + bw] = art[..., None]

    # What the calibration still needs: spoken and shown until each is met.
    needs = [
        ("top left", 3, "Aim the camera right and down, so the board sits in the top left of its view"),
        ("top right", 3, "Aim the camera left and down, so the board sits in the top right of its view"),
        ("bottom left", 3, "Aim the camera right and up, so the board sits in the bottom left of its view"),
        ("bottom right", 3, "Aim the camera left and up, so the board sits in the bottom right of its view"),
        ("from left", 4, "Move to the left of the screen and angle the camera back at it, about 30 degrees"),
        ("from right", 4, "Move to the right of the screen and angle the camera back at it, about 30 degrees"),
        ("from above", 4, "Move above the screen and angle the camera down at it, about 30 degrees"),
        ("from below", 4, "Move below the screen and angle the camera up at it, about 30 degrees"),
        ("close", 4, "Move in close, about 20 centimeters"),
        ("far", 4, "Move back, about 60 centimeters"),
    ]
    got = {k: 0 for k, _, _ in needs}
    seen, count, last_n, last_save, last_say, said = [], 0, 0, 0.0, 0.0, ""
    history, status, frames, preview = [], "waiting for video", [], None
    while count < TARGET_VIEWS:
        todo = next(((k, s) for k, q, s in needs if got[k] < q), None)
        show = page.copy()
        show[:BAND] = 235
        if preview is not None:
            show[0:BAND, 0:124] = cv2.resize(preview, (124, BAND))
        cv2.putText(show, f"Captured {count}/{TARGET_VIEWS}  {status}", (140, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(show, todo[1] if todo else "All covered. Keep adding varied views, or press q.", (140, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.imshow(name, show)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
        if todo and (todo[1] != said or time.time() - last_say > 15) and time.time() - last_say > 4:
            subprocess.Popen(["say", todo[1]])
            said, last_say = todo[1], time.time()
        if state["n"] == last_n or state["frame"] is None:
            continue
        last_n = state["n"]
        frame = state["frame"]
        preview = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids = detect(detector, gray)
        if corners is None:
            status, history, frames = "board not seen", [], []
            continue
        pts = {int(i): c for i, c in zip(ids.flatten(), corners.reshape(-1, 2))}
        history.append(pts); frames.append(gray)
        history, frames = history[-4:], frames[-4:]
        if len(history) < 4:
            continue
        common = set(history[0]) & set(history[-1])
        moved = np.median([np.linalg.norm(history[0][i] - history[-1][i]) for i in common]) if len(common) > 8 else 99
        if moved > 1.0:
            status = "hold still"
            continue
        o, i = board.matchImagePoints(corners, ids)
        ok, r, tv = cv2.solvePnP(o, i, KGUESS, None)
        R, _ = cv2.Rodrigues(r)
        n = R[:, 2]
        ax, ay = np.degrees(np.arctan2(n[0], n[2])), np.degrees(np.arctan2(n[1], n[2]))
        c = corners.reshape(-1, 2)
        cx, cy = c.mean(axis=0) / [1920, 1080]
        z = float(tv[2][0]) / 10
        sig = np.array([cx, cy, z / 40, ax / 40, ay / 40])
        if not all(np.linalg.norm(sig - s) > 0.15 for s in seen):
            status = "move to a new view"
            continue
        if time.time() - last_save < 0.6:
            continue
        seen.append(sig)
        avg = np.mean(np.stack(frames), axis=0).astype(np.uint8)  # averaging still frames removes video noise
        cv2.imwrite(f"{folder}/view_{count:03d}.png", avg)
        count += 1; last_save = time.time(); history, frames = [], []
        status = f"saved: {len(ids)} corners, {z:.0f} cm, tilt {max(abs(ax), abs(ay)):.0f} deg"
        subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
        if cy < .45 and cx < .45: got["top left"] += 1
        if cy < .45 and cx > .55: got["top right"] += 1
        if cy > .55 and cx < .45: got["bottom left"] += 1
        if cy > .55 and cx > .55: got["bottom right"] += 1
        if ax > 18: got["from left"] += 1
        if ax < -18: got["from right"] += 1
        if ay > 18: got["from above"] += 1
        if ay < -18: got["from below"] += 1
        if z < 28: got["close"] += 1
        if z > 50: got["far"] += 1
    state["stop"] = True
    cv2.destroyAllWindows(); cv2.waitKey(1)
    print("coverage:", got)
    return count


def selftest(folder, square_mm):
    # Render the board through known lens values and check that calibration recovers them.
    os.makedirs(folder, exist_ok=True)
    board = make_board(square_mm)
    art = board.generateImage((3200, 2000), marginSize=0, borderBits=1)
    K = np.array([[1980.0, 0, 955], [0, 1985, 545], [0, 0, 1]])
    dist = np.array([-0.32, 0.12, 0, 0, 0.0])
    W, H = 1920, 1080
    rng = np.random.default_rng(3)
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    # Inverse map: for each output pixel find its undistorted ray, then the board point.
    und = cv2.undistortPoints(np.stack([gx, gy], -1).reshape(-1, 1, 2), K, dist).reshape(H, W, 2)
    bw, bh = SQUARES[0] * square_mm, SQUARES[1] * square_mm
    n = 0
    for _ in range(24):
        rvec = rng.uniform(-0.45, 0.45, 3) * np.array([1, 1, 0.3])
        z = rng.uniform(300, 600)
        tvec = np.array([rng.uniform(-90, 90) - bw / 2, rng.uniform(-60, 60) - bh / 2, z])
        R, _ = cv2.Rodrigues(rvec)
        # Plane z=0 in board frame: solve the ray-plane intersection per pixel.
        rays = np.dstack([und, np.ones((H, W))]).astype(np.float64)
        nrm = R[:, 2]
        s = (nrm @ tvec) / (rays @ nrm)
        pts = rays * s[..., None] - tvec
        b = pts @ R  # world to board coordinates (R transpose applied on the right)
        mx = (b[..., 0] / bw * 3200).astype(np.float32); my = (b[..., 1] / bh * 2000).astype(np.float32)
        im = cv2.remap(art, mx, my, cv2.INTER_LINEAR, borderValue=200)
        im = np.clip(cv2.GaussianBlur(im, (3, 3), 0.7) + rng.normal(0, 3, im.shape), 0, 255).astype(np.uint8)
        cv2.imwrite(f"{folder}/view_{n:03d}.png", im); n += 1
    r = calibrate(folder, square_mm)
    print(json.dumps(r, indent=1))
    ok = abs(r["fx"] - 1980) < 15 and abs(r["cx"] - 955) < 15 and abs(r["dist_k1_k2_p1_p2_k3"][0] + 0.32) < 0.05 and r["rms_px"] < 1
    print("SELFTEST", "PASS" if ok else "FAIL", "true fx=1980 cx=955 k1=-0.32")


if __name__ == "__main__":
    out = arg("out", "calib_run")
    os.makedirs(out, exist_ok=True)
    square = float(arg("square-mm", 18.0))
    if "--selftest" in sys.argv:
        selftest(out, 18.0)
        sys.exit()
    if "--analyze-only" not in sys.argv:
        n = run_capture(out, square)
        print(f"captured {n} views in {out}")
    if arg("square-mm") is None and os.path.exists(f"{out}/board.json"):
        square = json.load(open(f"{out}/board.json"))["square_mm_computed"]
    print(json.dumps(calibrate(out, square), indent=1))
