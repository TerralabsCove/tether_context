# Prints the tag positions the reCamera broadcasts over UDP. Works over USB or Wi-Fi. Ctrl-C to stop.
import json, socket, sys, time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.bind(("0.0.0.0", 5005))
sock.settimeout(3)
print("Listening on UDP 5005. Show the camera a tag36h11 tag.")
print("x = right, y = down, z = distance out of the lens")
last_tag = 0
try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            print("... nothing from the camera for 3 s")
            continue
        for raw in data.splitlines():
            m = json.loads(raw)
            if m.get("hb"):
                if time.time() - last_tag > 1:
                    print(f"[{addr[0]}] camera alive, no tag | video {m['in_fps']:.1f} fps, detector {m['det_fps']:.1f} fps, {m['det_ms']} ms")
            else:
                last_tag = time.time()
                print(f"[{addr[0]}] tag {m['id']:>2} | x {m['x_cm']:7.1f} cm  y {m['y_cm']:7.1f} cm  z {m['z_cm']:7.1f} cm | "
                      f"roll {m['roll']:6.1f}  pitch {m['pitch']:6.1f}  yaw {m['yaw']:6.1f} | {m['px']:.0f} px, {m['det_ms']:.0f} ms", flush=True)
except KeyboardInterrupt:
    pass
