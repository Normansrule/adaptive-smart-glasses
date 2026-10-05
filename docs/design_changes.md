# v0.2: why it looks like this

v0.1 was camera-free with sensor-stuffed temple pods. It was bulky (temple pods 23 × 12 mm) and didn't do what you wanted.
v0.2 follows your direction: **a center camera, two screens per eye (outward designs + inward view), and the Apple Vision Pro / Google approach of moving weight and compute off the face.**

| Decision | Why |
|---|---|
| **Camera passthrough** (inner screens show the camera view) | Your choice. It lets the inside screens "help you see" with zoom, edge highlight and low-light boost, while the outside screens can be fully opaque design screens. |
| **Flip-up visor** on a brow hinge | A passthrough display blinds you when power or the camera fails. Flipping the visor up gives normal glasses in one motion. A hall sensor turns the screens off when it's up. |
| **Everything electronic in the visor** | Only battery wires cross hinges (2 per temple). The display flex cables, camera and screens never bend. |
| **Batteries in the earpieces** | As you asked. They also counterbalance the front-heavy visor. |
| **Pocket brick (Pi 5) for passthrough + AR, phone for control and AI** | Vision Pro puts its battery in a pocket. Here the brick also does the image processing, which an ESP32 cannot. The phone talks to the visor over BLE. |
| **XIAO ESP32-S3 stays the on-glasses chip** | It drives the design screens, reads the IMU, hall sensor, button and battery, and handles BLE and Wi-Fi. It is cheap and already known. |
| **Hardware camera privacy** | SW2 cuts the camera's 5 V. The CAMERA LIVE LED sits on that rail. No face recognition, and no recording by default. |

## Removed since v0.1
ToF depth sensor, BME280, microphone + PTT, 2 audio amps, bone transducer, speaker, bq25185 charger board, HUD tower, combiner.
Audio comes from your phone or earbuds. Depth comes from the camera (later).
Printed parts went from **10 to 7**. Temples went from **23 × 12.4 mm pods to 5 × 10 mm arms**.

## Known trade-offs (and the next step for each)
| Trade-off | Next step |
|---|---|
| Mono passthrough (one camera, same image to both eyes) gives no true depth | Add a stereo pair of cameras at eye spacing (v0.3) |
| 30 fps and an estimated 60–120 ms latency | 38 mm 60 fps camera board, GStreamer zero-copy, or an RK3588 brick |
| 400 mAh in the earpieces covers about 1.5 h of designs-only standby | Passthrough runs from the brick's power bank over the cable |
| About 150 g | Custom flex PCB + 0.49″ panels (option in the BOM) |
| Eyepiece and driver-board sizes not yet confirmed | Measure, set `[MEASURE]` values, rebuild |
