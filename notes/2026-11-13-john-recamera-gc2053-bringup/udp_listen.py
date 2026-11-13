"""Collects tagstream UDP lines for N seconds and prints a summary.
Usage: udp_listen.py <seconds> <out.jsonl>"""
import json
import socket
import statistics as st
import sys
import time

secs, out = float(sys.argv[1]), sys.argv[2]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except (AttributeError, OSError):
    pass
s.bind(("", 5005))
s.settimeout(0.5)
hb, dets = [], []
end = time.time() + secs
with open(out, "w") as f:
    while time.time() < end:
        try:
            data, _ = s.recvfrom(4096)
        except socket.timeout:
            continue
        for line in data.decode(errors="replace").splitlines():
            f.write(line + "\n")
            try:
                m = json.loads(line)
            except ValueError:
                continue
            (hb if m.get("hb") else dets).append(m)


def med(xs):
    return st.median(xs) if xs else float("nan")


busy = [h for h in hb if h.get("det_fps", 0) > 0]
print(f"heartbeats {len(hb)}, detections {len(dets)}")
print(f"frames in/s median {med([h['in_fps'] for h in busy]):.1f}, detections/s median {med([h['det_fps'] for h in busy]):.1f}, "
      f"ms per detection median {med([h['det_ms'] for h in busy]):.0f}")
if dets:
    print(f"tag px across median {med([d['px'] for d in dets]):.0f}, ids {sorted({d['id'] for d in dets})}, "
          f"margin median {med([d['margin'] for d in dets]):.0f}")
