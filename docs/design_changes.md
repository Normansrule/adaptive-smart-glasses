# Design changes vs the master brief (`build_brief.md`)

Goal of this revision: **the fewest components and printed parts that still meet every §0 invariant, with everything printable on a P1S.**

## Invariants: all preserved
| Invariant | How it's met |
|---|---|
| Camera-free | Depth comes only from the VL53L5CX (8×8 ranges). XIAO non-Sense. |
| Mic powered only while PTT held | The PTT switch is the only path from 3V3 to MIC_3V3. The 1N4148 blocks any GPIO back-feed. |
| Privacy LED tied to the mic rail | The LED + 1k hang directly on MIC_3V3. No GPIO can reach it. |
| ESP32 is safety authority / MEDIA_EN | D6 = MEDIA_EN, owned by safety_policy. The Pi (future) is gated by it. |
| Invalid ToF ≠ clear path; GNSS loss safe | Firmware rules (unchanged, not in this delivery). |

## Component count
| Brief | Now | Why |
|---|---|---|
| BMP390 + SHT40 (2 boards) | 1 × BME280 | One sensor does temperature, humidity and pressure (±1 hPa, fine for the 820 hPa flight prompt). It sits in its own vented pocket. |
| BQ24074 board + TPS61023 board (2) | 1 × Adafruit 6106 (bq25185 + TPS61023) | The BQ24074 board is 38 × 33 mm and can't fit a temple. The 6106 is 29 × 19 mm, has power-path and a thermistor input, and includes the 5 V boost. |
| DPST momentary PTT | 6 × 6 tact (SPST) + 1N4148 | Same hardware guarantee, much smaller and cheaper. Small DPST momentaries are rare and about 12 mm tall. |
| ICM-42688-P breakout | LSM6DSOX on Qwiic | No major vendor sells an ICM-42688-P on Qwiic. Qwiic means no soldering on the sensor chain. |
| 2 bone + 2 speakers | 1 + 1 (2nd optional) | Each MAX98357A is mono, so the second unit adds wires across the frame for no new channel. |
| 1200 mAh, 34 mm-wide pack | 800 mAh, 8 × 20 × 46 | Fits inside a temple pod. 1100 mAh is possible with a longer pod (see customization). |

## Printed parts: 17 → 10 (+ coupon)
| Removed / merged | Into |
|---|---|
| sensor_pod | frame (bridge pocket, open back so the Qwiic plugs can exit) |
| rear_battery_pod + cover, rear_compute_pod + cover, temple_cover_left/right | the temple pods + 2 sliding lids (1 screw each) |
| decorative_brow_insert | dropped. The browline brow *is* the sensor/harness carrier. |
| combiner_blank | dropped. The combiner is always purchased glass. |
| optics_pod_left/right + optics_pod_cover | one optics_tower (mirror with `hud_side`) + display_slider (also closes the top) + combiner_arm |

## Mechanical improvements
- **Hollow-pin hinge:** a 4 mm brass tube is the pin and the harness runs through it, so folding twists the wires instead of bending them. The temple knuckle stays unsplayed while the body splays 6° (from `head_width`). The open stop sits about 1.5° past splay. Fold is about 90°.
- **No trapped boards:** every frame pocket is open at the back. Pod boards sit on locating pins, fences or foam, and every USB-C exits through a wall of 1.6 mm or less.
- **Print-first geometry:** each part has one flat datum face (frame front, temple head side, lid outside, grip end), so nothing needs supports.
- **Serviceability:** each pod opens with one screw (front hook + M2 into a heat-set insert). The grips pull off. The HUD is 2 screws.
- **Cooling:** lid vents over the charger and the XIAO. The BME280 is kept away from both.
- **Comfort:** silicone stick-on nose pads on printed lands. A TPU interference sleeve on the earpiece. The bone transducer stands 0.8 mm proud in a compliant TPU cradle.
