# Live AprilTag check on the reCamera RTSP stream. Run on the Mac; press q to quit.
# Each detection is scored at full size and at the two sizes the camera can process quickly.
# Appends to a CSV: time, tag id, px across the tag, and whether each size found it.
import csv, os, sys, threading, time
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|allowed_media_types;video"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import json
import cv2
import numpy as np

URL = "rtsp://192.168.42.1:554/live"
HEADLESS = "--headless" in sys.argv
SECS = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--secs=")), 0)
OUT = next((a.split("=")[1] for a in sys.argv if a.startswith("--csv=")), "tag_log.csv")
SAVE = next((a.split("=")[1] for a in sys.argv if a.startswith("--save=")), None)
CALIB = next((a.split("=")[1] for a in sys.argv if a.startswith("--calib=")), None)
# Printed size of each tag's black square on tag36h11-sheet.pdf, in mm.
TAG_MM = {0: 29.8, 1: 50.1, 2: 79.9}
K, DIST = None, None
if CALIB:
    c = json.load(open(CALIB))
    K = np.array([[c["fx"], 0, c["cx"]], [0, c["fy"], c["cy"]], [0, 0, 1]])
    DIST = np.array(c["dist_k1_k2_p1_p2_k3"])


def distance_cm(tag_id, corners):
    if K is None or tag_id not in TAG_MM:
        return None
    s = TAG_MM[tag_id] / 2
    obj = np.array([[-s, s, 0], [s, s, 0], [s, -s, 0], [-s, -s, 0]], np.float64)
    ok, _, t = cv2.solvePnP(obj, corners.astype(np.float64), K, DIST, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    return float(np.linalg.norm(t)) / 10 if ok else None


params = cv2.aruco.DetectorParameters()
params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11), params)

latest = None
frame_no = 0
reconnects = -1
first_frame_at = None
stop = threading.Event()
t0 = time.time()


def read_stream():
    # Always drain the stream on its own thread so slow detection can't back up the camera.
    global latest, frame_no, reconnects, first_frame_at
    while not stop.is_set():
        reconnects += 1
        cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG,
                               [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000, cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000])
        while cap.isOpened() and not stop.is_set():
            ok, frame = cap.read()
            if not ok:
                break
            latest, frame_no = frame, frame_no + 1
            if first_frame_at is None:
                first_frame_at = time.time() - t0
        cap.release()
        if not stop.is_set():
            time.sleep(1)


def find(gray, width):
    h, w = gray.shape
    s = width / w
    small = cv2.resize(gray, (width, round(h * s)), interpolation=cv2.INTER_AREA) if s != 1 else gray
    corners, ids, _ = det.detectMarkers(small)
    return {} if ids is None else {int(i): c[0] / s for i, c in zip(ids.flatten(), corners)}


threading.Thread(target=read_stream, daemon=True).start()
new = not os.path.exists(OUT) or os.path.getsize(OUT) == 0
log = open(OUT, "a", newline="")
wr = csv.writer(log)
if new:
    wr.writerow(["t", "id", "px_across", "found_1920", "found_640", "found_320", "sharpness", "distance_cm"])
    log.flush()

done = 0; hits = 0; seen = 0; saved = False; sharp = 0.0
waiting = np.zeros((540, 960, 3), np.uint8)
cv2.putText(waiting, "Waiting for camera video...", (180, 270), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
while True:
    if frame_no == seen:
        if not HEADLESS:
            cv2.imshow("reCamera tags (q to quit)", waiting if latest is None else cv2.resize(latest, (960, 540)))
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
        else:
            time.sleep(0.01)
    else:
        seen = frame_no
        frame = latest.copy()
        done += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        full, mid, low = find(gray, 1920), find(gray, 640), find(gray, 320)
        sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
        for i, c in full.items():
            hits += 1
            across = max(cv2.norm(c[0] - c[1]), cv2.norm(c[1] - c[2]))
            dist_cm = distance_cm(i, c)
            wr.writerow([round(time.time() - t0, 2), i, round(across, 1), 1, int(i in mid), int(i in low), round(sharp),
                         "" if dist_cm is None else round(dist_cm, 2)])
            cv2.polylines(frame, [c.astype(int)], True, (0, 255, 0), 3)
            cv2.putText(frame, f"id {i} {'' if dist_cm is None else f'{dist_cm:.1f}cm '}{across:.0f}px 640:{'Y' if i in mid else 'n'} 320:{'Y' if i in low else 'n'}",
                        (int(c[0][0]), int(c[0][1]) - 12), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        log.flush()
        if SAVE and not saved:
            cv2.imwrite(SAVE, frame); saved = True
        if not HEADLESS:
            cv2.imshow("reCamera tags (q to quit)", cv2.resize(frame, (960, 540)))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    if SECS and time.time() - t0 > SECS:
        break
stop.set()
log.close()
ttff = "none" if first_frame_at is None else f"{first_frame_at:.1f}s"
print(f"first_frame={ttff} frames={frame_no} scored={done} detections={hits} reconnects={max(reconnects, 0)} "
      f"secs={time.time() - t0:.1f} sharpness_last={sharp:.0f}")
