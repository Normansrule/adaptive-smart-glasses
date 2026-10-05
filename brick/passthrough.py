#!/usr/bin/env python3
"""Adaptive Smart Glasses v0.2: pocket-brick passthrough (Raspberry Pi 5).  Status: EXPERIMENTAL.

camera (UVC, MJPEG 1080p30) -> enhance (normal / zoom / edges / low-light) -> AR HUD overlay
-> side-by-side 3840x1080 frame -> HDMI -> dual micro-OLED board in the visor.

Head pose, battery, visor state and the AR mode arrive as UDP packets from the visor MCU
(firmware/glasses_mcu/main/net.c). The phone picks the AR mode over BLE.

SAFETY (read docs/requirements.md):
  * camera frames late by more than 250 ms -> the screen turns red with "LIFT VISOR" (you are blind otherwise)
  * visor up -> black frame (inner screens dark)
  * expect 60-120 ms motion-to-photon latency: use seated or walking slowly. Never while driving.
No face recognition and no recording are done here. Frames are processed in memory and dropped.

usage:  python3 passthrough.py                     # camera 0, fullscreen on the HDMI display
        python3 passthrough.py --demo --frames 30 --out /tmp/sbs.png   # no hardware: synthetic test
"""
import argparse, socket, struct, threading, time
import numpy as np
import cv2

PKT = struct.Struct("<4sIIffffffHBBB3x")          # must match pose_pkt_t in net.c (44 bytes)
MODES = ["NORMAL", "ZOOM 2x", "EDGES", "LOW-LIGHT"]

class Pose:
    def __init__(self):
        self.yaw = self.pitch = self.roll = 0.0; self.vbat = 0; self.visor_up = 0; self.design = 0
        self.mode = 0; self.last = 0.0
    def listen(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(("0.0.0.0", port)); s.settimeout(0.5)
        while True:
            try: data, _ = s.recvfrom(64)
            except socket.timeout: continue
            if len(data) != PKT.size: continue
            m, seq, t, yaw, pitch, roll, ax, ay, az, vbat, up, design, mode = PKT.unpack(data)
            if m != b"ASG2": continue
            self.yaw, self.pitch, self.roll, self.vbat, self.visor_up, self.design, self.mode, self.last = \
                yaw, pitch, roll, vbat, up, design, mode % len(MODES), time.time()

def enhance(img, mode):
    if mode == 1:                                     # zoom 2x (centre crop)
        h, w = img.shape[:2]; c = img[h//4:h*3//4, w//4:w*3//4]
        return cv2.resize(c, (w, h), interpolation=cv2.INTER_LINEAR)
    if mode == 2:                                     # edge highlight for low-contrast scenes
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 60, 140)
        out = img.copy(); out[e > 0] = (0, 255, 255); return out
    if mode == 3:                                     # low-light: CLAHE on luminance
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB); l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(l)
        return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
    return img

def hud(img, pose, fps):
    h, w = img.shape[:2]; cx, cy = w // 2, h // 2
    # horizon line from head roll/pitch (keeps you oriented in passthrough)
    r = np.radians(-pose.roll); dy = int(pose.pitch * h / 60)
    dx1, dy1 = int(np.cos(r) * 220), int(np.sin(r) * 220)
    cv2.line(img, (cx - dx1, cy + dy - dy1), (cx - 70, cy + dy - int(np.sin(r) * 70)), (0, 255, 0), 3)
    cv2.line(img, (cx + 70, cy + dy + int(np.sin(r) * 70)), (cx + dx1, cy + dy + dy1), (0, 255, 0), 3)
    t = time.strftime("%H:%M")
    bat = f"{pose.vbat/1000:.2f}V" if pose.vbat else "--"
    link = "OK" if time.time() - pose.last < 1 else "NO IMU"
    for i, s in enumerate([t, f"{MODES[pose.mode]}", f"BAT {bat}", f"{fps:4.1f} fps", link]):
        cv2.putText(img, s, (60, 90 + i * 46), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(img, s, (60, 90 + i * 46), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    return img

def side_by_side(img, ipd_shift):
    """Mono camera -> both eyes. ipd_shift (px) moves the images apart to set a comfortable convergence."""
    eye = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_LINEAR)
    M = np.float32([[1, 0, ipd_shift], [0, 1, 0]]); N = np.float32([[1, 0, -ipd_shift], [0, 1, 0]])
    return np.hstack([cv2.warpAffine(eye, M, (1920, 1080)), cv2.warpAffine(eye, N, (1920, 1080))])

def warning(text, color):
    f = np.zeros((1080, 1920, 3), np.uint8); f[:] = color
    cv2.putText(f, text, (330, 560), cv2.FONT_HERSHEY_SIMPLEX, 3.2, (255, 255, 255), 8, cv2.LINE_AA)
    return np.hstack([f, f])

def synthetic(i):
    f = np.zeros((1080, 1920, 3), np.uint8)
    cv2.rectangle(f, (200 + i * 10 % 1200, 300), (600 + i * 10 % 1200, 800), (40, 120, 220), -1)
    cv2.circle(f, (1500, 540), 200, (60, 200, 90), -1); return f

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", default=0); ap.add_argument("--port", type=int, default=5005)
    ap.add_argument("--ipd-shift", type=int, default=0); ap.add_argument("--demo", action="store_true")
    ap.add_argument("--frames", type=int, default=0); ap.add_argument("--out", default="")
    ap.add_argument("--mode", type=int, default=-1, help="force AR mode 0-3 (else from the phone)")
    a = ap.parse_args()
    pose = Pose(); threading.Thread(target=pose.listen, args=(a.port,), daemon=True).start()
    cap = None
    if not a.demo:
        cap = cv2.VideoCapture(int(a.camera) if str(a.camera).isdigit() else a.camera, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080); cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)               # always the newest frame (lower latency)
    show = not a.out
    if show:
        cv2.namedWindow("asg", cv2.WINDOW_NORMAL); cv2.setWindowProperty("asg", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    last_ok, n, total, t0, fps, sbs = time.time(), 0, 0, time.time(), 0.0, None
    while True:
        ok, img = (True, synthetic(n)) if a.demo else cap.read()
        now = time.time()
        if ok: last_ok = now
        if a.mode >= 0: pose.mode = a.mode
        if pose.visor_up and now - pose.last < 1:
            sbs = np.zeros((1080, 3840, 3), np.uint8)                       # visor up: inner screens dark
        elif not ok or now - last_ok > 0.25:
            sbs = warning("LIFT VISOR - NO CAMERA", (0, 0, 200))           # fail-safe
        else:
            sbs = side_by_side(hud(enhance(img, pose.mode), pose, fps), a.ipd_shift)
        n += 1; total += 1
        if now - t0 >= 1: fps, t0, n = n / (now - t0), now, 0
        if show:
            cv2.imshow("asg", sbs)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")): break
        if a.frames and total >= a.frames: break
    if a.out: cv2.imwrite(a.out, cv2.resize(sbs, (1920, 540))); print("wrote", a.out)

if __name__ == "__main__":
    main()
