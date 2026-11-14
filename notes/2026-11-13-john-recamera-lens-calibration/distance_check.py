# Distance check for the on-camera tag loop: compares the depth the camera reports with a tape measure.
# The camera must be running start_tags.sh (it broadcasts tag poses on UDP port 5005).
# It draws three tags full screen on the Mac at the sizes tagstream assumes, plus a 100 mm bar to check with a
# ruler. Point the camera square at the screen. Measure from the front of the lens straight to the screen.
# It speaks each distance. Press 1 when the camera is in place. It records the next 2 seconds.
# Keys: 1 = record, r = redo the last one, s = skip this distance, q = finish.
# Usage: distance_check.py --out=<folder> [--stations=30,50,75,100,150]
import ctypes, ctypes.util, json, os, socket, statistics as st, subprocess, sys, threading, time
import cv2
import numpy as np

TAG_MM = {0: 29.8, 2: 79.9}   # what tagstream assumes; every other id is 50.1 mm
RECORD_S = 2.0               # seconds of readings taken after the key press


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


def tag_page(out):
    # White page the size of the screen, with tags 2, 1 and 0 drawn at true size on the right and a 100 mm bar.
    width_mm, W, H = screen_mm()
    mm = width_mm / W                      # millimetres per screen point
    page = np.full((H, W, 3), 255, np.uint8)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    x0, drawn = W - 510, {}
    for tag_id, (x, y) in {2: (x0, 50), 1: (x0, 520), 0: (x0 + 300, 570)}.items():
        side = round(TAG_MM.get(tag_id, 50.1) / mm)
        tag = cv2.resize(cv2.aruco.generateImageMarker(d, tag_id, 8 * 40), (side, side), interpolation=cv2.INTER_NEAREST)
        page[y:y + side, x:x + side] = tag[..., None]
        drawn[str(tag_id)] = round(side * mm, 2)
    bar = round(100 / mm)
    page[H - 110:H - 98, x0 - 60:x0 - 60 + bar] = 0
    cv2.putText(page, "this bar must measure 100 mm", (x0 - 60, H - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    json.dump({"screen_points": [W, H], "mm_per_point": round(mm, 5), "drawn_black_square_mm": drawn,
               "bar_mm_if_scale_is_right": round(bar * mm, 2)}, open(f"{out}/screen_tags.json", "w"), indent=1)
    return page


def main():
    out = arg("out", "distance_check")
    os.makedirs(out, exist_ok=True)
    page = tag_page(out)
    stations = [float(x) for x in arg("stations", "30,50,75,100,150").split(",")]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("0.0.0.0", 5005))
    sock.settimeout(0.5)
    state = {"tags": [], "hb": None, "stop": False}   # tags: (time, message)
    raw = open(f"{out}/raw.jsonl", "a")

    def listen():
        while not state["stop"]:
            try:
                data, _ = sock.recvfrom(2048)
            except socket.timeout:
                continue
            for line in data.splitlines():
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                m["mac_t"] = round(time.time(), 3)
                raw.write(json.dumps(m) + "\n")
                if m.get("hb"):
                    state["hb"] = m
                else:
                    state["tags"].append((time.time(), m))
                    state["tags"] = state["tags"][-400:]

    threading.Thread(target=listen, daemon=True).start()

    def window(seconds):
        now = time.time()
        by = {}
        for t, m in state["tags"]:
            if now - t <= seconds:
                by.setdefault(m["id"], []).append(m)
        return by

    def summarise(by):
        res = {}
        for i, ms in sorted(by.items()):
            z = [m["z_cm"] for m in ms]
            res[str(i)] = {"n": len(z), "z_cm": round(st.median(z), 2), "z_sd_cm": round(st.pstdev(z), 3),
                           "x_cm": round(st.median(m["x_cm"] for m in ms), 2), "y_cm": round(st.median(m["y_cm"] for m in ms), 2),
                           "px": round(st.median(m["px"] for m in ms), 1), "margin": round(st.median(m["margin"] for m in ms), 1),
                           "assumed_tag_mm": TAG_MM.get(i, 50.1)}
        return res

    name = "tag distance check (1 = record, r = redo, s = skip, q = finish)"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    results, k, said, rec_until, note = [], 0, None, 0.0, ""
    while k < len(stations):
        target = stations[k]
        if said != k:
            subprocess.Popen(["say", f"{target:.0f} centimeters. Press 1 when it is in place."])
            said = k
        live = window(1.0)
        img = page.copy()
        cv2.putText(img, f"Step {k + 1} of {len(stations)}: {target:.0f} cm, lens front to screen", (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        y = 130
        if not live:
            cv2.putText(img, "no tag seen", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 200), 3)
        for i, ms in sorted(live.items()):
            z = st.median(m["z_cm"] for m in ms)
            cv2.putText(img, f"tag {i}: {z:6.1f} cm", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 110, 0), 3)
            cv2.putText(img, f"{st.median(m['px'] for m in ms):.0f} px wide, {TAG_MM.get(i, 50.1):.1f} mm tag, {len(ms)} readings/s",
                        (30, y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1)
            y += 95
        recording = rec_until > 0
        msg = f"recording, hold still {max(0.0, rec_until - time.time()):.1f} s" if recording else f"press 1 to record {target:.0f} cm"
        cv2.putText(img, msg, (30, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 200), 2)
        cv2.putText(img, note, (30, 505), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
        hb = state["hb"]
        if hb:
            cv2.putText(img, f"camera: video {hb['in_fps']:.1f} fps, detector {hb['det_fps']:.1f} per second", (30, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1)
        cv2.putText(img, "1 = record this distance, r = redo last, s = skip, q = finish", (30, 575), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1)
        yy = 630
        for r in results[-5:]:
            cv2.putText(img, f"recorded {r['tape_cm']:.0f} cm: " + (", ".join(f"tag {i} {v['z_cm']:.1f}" for i, v in r["tags"].items()) or "skipped"),
                        (30, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            yy += 28
        cv2.imshow(name, img)
        key = cv2.waitKey(100) & 0xFF
        if key == ord("q"):
            break
        if recording:
            if time.time() >= rec_until:      # the two seconds after the key press are the reading
                rec_until = 0.0
                got = window(RECORD_S)
                if not got:
                    note = "no tag was seen while recording. Press 1 to try again, or s to skip."
                    subprocess.Popen(["afplay", "/System/Library/Sounds/Basso.aiff"])
                    continue
                results.append({"tape_cm": target, "tags": summarise(got), "how": "key"})
                subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
                json.dump(results, open(f"{out}/distance_check.json", "w"), indent=1)
                k += 1
            continue
        if key == ord("s"):
            results.append({"tape_cm": target, "tags": {}, "skipped": True}); k += 1; note = ""
        elif key == ord("r") and results:
            results.pop(); k -= 1; said = None; note = ""
        elif key in (ord("1"), ord(" ")):
            rec_until, note = time.time() + RECORD_S, ""
    state["stop"] = True
    cv2.destroyAllWindows(); cv2.waitKey(1)
    json.dump(results, open(f"{out}/distance_check.json", "w"), indent=1)
    print(f"{'tape cm':>8} {'tag':>4} {'z cm':>8} {'error cm':>9} {'error %':>8} {'sd cm':>6} {'px':>5} {'n':>3}")
    for r in results:
        for i, v in r["tags"].items():
            e = v["z_cm"] - r["tape_cm"]
            print(f"{r['tape_cm']:8.0f} {i:>4} {v['z_cm']:8.1f} {e:+9.1f} {100 * e / r['tape_cm']:+8.1f} {v['z_sd_cm']:6.2f} {v['px']:5.0f} {v['n']:3d}")
        if not r["tags"]:
            print(f"{r['tape_cm']:8.0f}    no tag recorded")


if __name__ == "__main__":
    main()
