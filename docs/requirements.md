# Requirements and verification (v0.2)

Method: **I** = inspection · **A** = analysis/CAD · **T** = test.
Status: ✅ verified in CAD/analysis/compile · 🧪 needs a hardware test · ⏳ not built yet.

> v0.2 deliberately replaces the v0.1 "camera-free" rule (owner's decision, 2026-10). The privacy rules below take its place.

## Privacy
| ID | Requirement | Method | How it's met | Status |
|---|---|---|---|---|
| PRV-1 | The camera can only get power from a physical switch | I/T | SW2 is the only path from VBUS to CAM_5V ([pinout](pinout.md)). Test: SW2 off means the brick sees no USB camera. | 🧪 |
| PRV-2 | The CAMERA LIVE light is on whenever the camera has power, and software can't hide it | A/T | D1 + R1 sit on CAM_5V and nowhere else. | ✅ wiring · 🧪 |
| PRV-3 | No face recognition, and no recording by default | I | `brick/passthrough.py` processes frames in memory and drops them. | ✅ |
| PRV-4 | Outward designs can be turned off at once | T | Long-press the button, or choose Off in the app. Backlight goes to 0. | 🧪 |

## Safety
| ID | Requirement | Method | How it's met | Status |
|---|---|---|---|---|
| SAF-1 | One action restores normal vision | A/T | The visor flips up through 100° with no collisions (`tools/check_fit.py`), and the frame has open lenses. | ✅ CAD · 🧪 |
| SAF-2 | If the camera fails or stalls, warn within 250 ms | T | The brick shows a red LIFT VISOR screen after 250 ms with no frame. | ✅ synthetic · 🧪 |
| SAF-3 | Visor up turns the inner and outer screens off | T | Hall switch (D7) → firmware blanks the designs; the UDP flag → brick shows black. | ✅ code · 🧪 |
| SAF-4 | Never use passthrough while driving, cycling or on stairs | I | README + app warning. Owner's responsibility. | ✅ doc |
| SAF-5 | Battery safety | A/T | Protected cells at 0.25C charge (XIAO 100 mA), away from the skin behind a 1.4 mm wall + TPU grip. | 🧪 |
| SAF-6 | Design animations stay under 3 flashes per second (photosensitivity) | A | Rings ≈ 0.8 Hz, rainbow is a smooth drift, the eyes blink about every 3–5 s. | ✅ |
| SAF-7 | No sharp edges against the skin | I | Chamfered visor, TPU grips, nose pads. Deburr the tubes. | 🧪 |

## Manufacturability
| ID | Requirement | Method | Status |
|---|---|---|---|
| MFG-1 | All parts print on a P1S with no supports | A (`cad/part_stats.json`) | ✅ |
| MFG-2 | All meshes are manifold | A (`tools/postprocess.py`) | ✅ |
| MFG-3 | No collisions: visor at 0/35/70/100°, temple folded to 80° | A (`tools/check_fit.py`) | ✅ |
| MFG-4 | Only battery wires cross hinges, through the brass tubes | A ([pinout](pinout.md)) | ✅ |
| MFG-5 | Firmware builds from a clean checkout | T (`idf.py build`, ESP-IDF 5.5.1) | ✅ |
| MFG-6 | Optics and driver-board pockets match the real parts | I (`[MEASURE]`) | 🧪 |

## Performance targets
| ID | Target | Status |
|---|---|---|
| PRF-1 | Passthrough at ≥ 30 fps, latency ≤ 120 ms (measure by filming a stopwatch through the eyepiece) | 🧪 |
| PRF-2 | Design screens at ≥ 15 fps on both | 🧪 |
| PRF-3 | Head pose to the brick at 100 Hz | ✅ code · 🧪 |
| PRF-4 | Designs-only standby ≥ 1 h on the earpiece cells | 🧪 |
