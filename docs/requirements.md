# Requirements and how each one is verified

Source: the master brief ([`build_brief.md`](build_brief.md)).
Method: **I** = inspection · **A** = analysis/CAD · **T** = test · **D** = demonstration.
Status: ✅ verified in CAD/analysis · 🧪 needs a hardware test · ⏳ not built yet (firmware/app).

## Privacy (non-negotiable)
| ID | Requirement | Method | How it is met / checked | Status |
|---|---|---|---|---|
| PRV-1 | No camera, no image capture | I | The only optical sensor is the VL53L5CX 8×8 rangefinder. The XIAO is the non-Sense (no camera) model. | ✅ |
| PRV-2 | Mic is powered **only** while PTT is held | T | MIC_3V3 exists only after SW2. The factory test checks the mic is silent when released and live when held. | 🧪 |
| PRV-3 | Firmware has no path that can power the mic | A | D3 (1N4148) points MIC_3V3 → GPIO, so a GPIO cannot drive the rail. There is no other connection to MIC_3V3 ([pinout](pinout.md)). | ✅ |
| PRV-4 | Privacy LED lit whenever the mic is powered, and never otherwise | T | D1 + R1 hang on MIC_3V3 only. Check by eye during the factory test. | 🧪 |
| PRV-5 | No wake word, no rolling audio buffer | I | Without PTT the mic has no power, so the firmware has nothing to buffer. | ✅ by hardware |

## Safety
| ID | Requirement | Method | How it is met / checked | Status |
|---|---|---|---|---|
| SAF-1 | ESP32 owns MEDIA_EN. DRIVE_SAFE forces it LOW and the app cannot override it | T | D6 is driven LOW at boot (factory test checks this). The DRIVE_SAFE logic is firmware. | ⏳ |
| SAF-2 | An invalid ToF reading never counts as a clear path | T | Firmware rule. Test with glass, black and reflective targets in Phase 4. | ⏳ |
| SAF-3 | Losing GNSS while moving doesn't restore media | T | Firmware rule (brief §4). | ⏳ |
| SAF-4 | Battery stays within safe temperature and current | T | The NTC on the bq25185 TS pin cuts charging in hardware. Charge current 500 mA (0.6C). Protected cell. | 🧪 |
| SAF-5 | Real mechanical main switch | I | SW1 (5 A slide switch) breaks 5V_SW. Charging keeps working with it off. | ✅ |
| SAF-6 | Safe listening level | T | TONE_AMPL / volume cap in firmware. Measure SPL at the ear in Phase 6. | 🧪 |
| SAF-7 | No sharp edges against skin | I | Chamfered pods, TPU grips. Deburr the brass tubes. | 🧪 |
| SAF-8 | HUD never permanently covers central vision | A/T | Combiner is 30R/70T, centred 6 mm above the pupil line, and the tower is removable (2 screws). | 🧪 |

## Manufacturability
| ID | Requirement | Method | How it is met / checked | Status |
|---|---|---|---|---|
| MFG-1 | Every part prints on a Bambu P1S without supports | A | `cad/part_stats.json`: all fit P1S/A1/A1 Mini. Each part has a flat datum face. | ✅ |
| MFG-2 | All meshes are manifold | A | `tools/postprocess.py` checks watertightness on every build. | ✅ |
| MFG-3 | No part collisions at rest; temples fold | A | Checked by OpenSCAD intersection: 0 mm³ at rest, folds to about 90°. | ✅ |
| MFG-4 | Pockets sized from real module outlines | A/I | Vendor Eagle/STEP outlines where confirmed. The rest are tagged `[MEASURE]`. | 🧪 |
| MFG-5 | Boards are not trapped behind walls where connectors must exit | I | Frame pockets are open at the back. Pod USB-C ports go through walls of 1.6 mm or less. | ✅ |
| MFG-6 | Serviceable: lids reopen repeatedly | I | M2 heat-set insert + front hook, 1 screw per lid. | ✅ |
| MFG-7 | Hinge wiring survives folding | T | Hollow brass pin, wires twist instead of bend. Test: 2,000 folds with continuity on every wire. | 🧪 |
| MFG-8 | Minimum part count | A | 10 printed parts (was 17) and 17 electronic part types. See [design_changes](design_changes.md). | ✅ |

## Performance targets (from the brief)
| ID | Target | Status |
|---|---|---|
| PRF-1 | Obstacle warning when an object is closer than 0.8 m; urgent when closer than 0.45 m, or closer than 1.5 m and closing; L/C/R zone | ⏳ firmware |
| PRF-2 | DRIVE_SAFE on above 8.0 m/s for 10 s with motion evidence; off below 2.5 m/s for 30 s | ⏳ firmware |
| PRF-3 | Flight-mode *prompt* when pressure stays below 820 hPa for 120 s | ⏳ firmware |
| PRF-4 | Runtime: measure in Phase 2 (estimate 4–6 h on 800 mAh) | 🧪 |
