# Wiring overview (v0.2)

**Every pin is in [`pinout.md`](pinout.md)**, generated from [`../hardware/netlist.csv`](../hardware/netlist.csv). This page explains the rules behind it.

![Power and camera privacy](img/wiring_power.svg)

## Rules the wiring enforces
1. **Camera privacy is physical.** VBUS → SW2 → CAM_5V is the camera's only supply. The CAMERA LIVE LED (D1 + R1) sits on that rail. No GPIO touches it.
2. **Only battery wires cross hinges.** Each temple tube carries its cell's BAT+ and GND. The left visor tube carries both pairs. Everything else (screens, camera, flex cables) lives inside the visor and never bends.
3. **The brick powers the heavy parts.** The camera and the micro-OLED board run from the cable's 5 V (power-bank port 2), never from the earpiece cells. The cells only run the XIAO and the design screens.
4. **The XIAO charges the cells.** Cable 5 V goes through a 1N5817 into the XIAO 5V pin, and its charger (≈100 mA) tops up the parallel cells through SW1.

![Signals](img/wiring_signals.svg)

## Data paths
| Path | Link | Rate |
|---|---|---|
| Camera → brick | USB 2.0 UVC, MJPEG 1080p30 | 30 fps |
| Brick → micro-OLEDs | HDMI, side by side 3840×1080 | 30–60 Hz |
| Visor → brick | Wi-Fi UDP to `10.42.0.1:5005`: head pose, battery, visor state, AR mode (44-byte packet) | 100 Hz |
| Phone ↔ visor | BLE GATT `7a1e0000-…` (design, brightness, text, AR mode, status) | on change / 0.5 Hz |
