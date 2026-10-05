# Pocket brick: Raspberry Pi 5 (EXPERIMENTAL)

```
camera (USB) ─► passthrough.py ─► enhance (normal / zoom / edges / low-light) ─► HUD ─► SBS 3840×1080 ─► HDMI ─► visor
visor XIAO ──Wi-Fi UDP :5005 (head pose, battery, visor state, AR mode)──► passthrough.py
```

```bash
bash brick/setup_brick.sh          # OpenCV + "ASG-BRICK" hotspot (password glasses123, gateway 10.42.0.1)
python3 brick/passthrough.py       # fullscreen on the HDMI output; press q to quit
python3 brick/passthrough.py --demo --frames 30 --out test.png   # no hardware: synthetic check
```

**Fail-safes:**
- No camera frame for 250 ms: red **LIFT VISOR** screen.
- Visor up: black screen.

**Privacy:** nothing is saved, and there is no face recognition. Expect 60–120 ms latency. Use it seated first.
