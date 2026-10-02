# CAD: build, print, assemble

Source: `cad/adaptive_smart_glasses.scad` (geometry) + `cad/config.scad` (every tunable dimension).
Outputs: `cad/stl/*.stl`, `cad/3mf/*.3mf` (one part each), `cad/plates/*.3mf` (multi-object Bambu plates), `models/*.stl` (assembly-positioned meshes for the web viewer), `cad/part_stats.json`.

Rebuild everything:
```bash
./tools/build.sh                 # all parts, ~1 min
./tools/build.sh frame lid_left  # just these
openscad cad/adaptive_smart_glasses.scad   # interactive; part="assembly" shows everything
```

## Parts: 10 printed + 1 calibration coupon (was 17)

| # | Part | Material | Status | Print orientation | Supports |
|---|---|---|---|---|---|
| 0 | tolerance_coupon | PETG | print first | flat | none |
| 1 | frame | PETG | PROTOTYPE-READY | front face down | none |
| 2 | temple_left (battery + charger pod) | PETG | PROTOTYPE-READY | head face down | none |
| 3 | temple_right (compute + audio pod) | PETG | PROTOTYPE-READY | head face down | none |
| 4–5 | lid_left / lid_right | PETG | PROTOTYPE-READY | outer face down | none |
| 6–7 | ear_grip_left / ear_grip_right | TPU 95A | PROTOTYPE-READY | entry end down | none |
| 8 | optics_tower | black PETG | EXPERIMENTAL | upside down | none |
| 9 | display_slider | black PETG | EXPERIMENTAL | pocket up | none |
| 10 | combiner_arm | PETG | EXPERIMENTAL | flat | none |

Every part fits a Bambu Lab P1S, A1 and A1 Mini bed (largest is the frame at 142 × 53 mm).
All meshes are checked watertight on every build. Settings for each part are in `cad/print_manifest.csv`.

**P1S settings:** Bambu PETG HF, 0.4 mm nozzle, "0.16 mm Optimal", 4 walls, 30% gyroid, textured PEI plate.
TPU 95A at 0.20 mm, 3 walls, fed from the external spool (not the Automatic Material System, AMS).
Open `cad/plates/plate_1_core_petg.3mf` in Bambu Studio and every core part is already laid out on one plate.

## Verified in CAD

- No interference between frame and temples, lids, or HUD parts at rest.
- Each temple folds freely to about 90° (then touches the bridge pod) and stops about 1.5° outward past the 6° splay.
- Pockets are sized from vendor Eagle/STEP outlines where those were confirmed: ToF 25.4 × 12.7, charger 29.21 × 19.05, IMU 25.4 × 17.78, amp 19.05 × 17.78.
- Items tagged `[MEASURE]` in `config.scad` (BME280, battery, mic, speaker, transducer, switch actuator, display) are estimates. **Measure yours, edit, rebuild.**

## Assembly order

1. **Coupon.** Print it and test-fit an insert, the brass tube (glue fit and running fit), a PCB edge and a tact switch. Copy the winning values into `config.scad` and rebuild.
2. **Inserts.** Heat-set one ruthex M2 insert in each temple's centre rib. Fit 2 more in the brow front only if you're adding the HUD.
3. **Hinge pins.** Cut two 13.5 mm pieces of 4 mm brass tube and deburr inside and out.
   Thread the hinge wires through first (see `wiring.md`).
   Push each tube up through the temple knuckle (glue it there with CA) and on through the frame knuckle.
   Flare the top inside the counterbore with a conical punch. A 4 mm-ID washer plus a drop of CA also works.
   The temple is now captive and turns on the tube, so the wires twist rather than bend.
4. **Frame electronics** (all pockets open at the back):
   - ToF: sensor faces forward into the window, Qwiic plugs behind.
   - BME280: slides into the left-brow pocket.
   - PTT tact switch: right endpiece pocket. Check that the flexure tongue clicks it.
   - LED: from the back, flange against the step.
   - Main slide switch: left endpiece, actuator through the side slot.
   Press the wires into the brow groove and cover with Kapton.
5. **Left pod.**
   - Charger: drop it onto its 4 locating pins, USB-C through the rear wall.
   - Battery: in the front bay between 1 mm foam pads, with the NTC taped to it.
6. **Right pod.**
   - Inner layer: amps between the front wall and the fence, speaker inside the ring.
   - Then 1 mm foam, then the outer layer: mic at the front (port lines up with the lid hole), IMU, then the XIAO at the rear with USB-C through the wall.
7. **Lids.** Put 1 mm foam on the underside, hook the front tab under the lip, slide forward and fit 1 × M2×5.
8. **Ear grips.** Push them on (a drop of IPA helps). Press the bone transducer into the right cradle, face out.
9. **Nose pads.** Stick the silicone pads onto the printed lands.
10. **HUD (Phase 5, EXPERIMENTAL).**
    - Press the lens into the tower seat (flat side up toward the display).
    - Glue the combiner into the arm (coated side toward the display) and pivot it on 2 × M2×4.
    - Slide the display carrier in and clamp it with M2×6.
    - Screw the tower to the brow with 2 × M2×6.
    - Focus by sliding the display (about ±6 mm). Set the tilt in the 35–50° range.

## Honest limits of this revision

- Weight is about 40–45 g printed plus about 45 g of dev modules, so roughly 90 g. That's heavy next to normal glasses (25–50 g). The temple pods (23 × 12.4 mm) are sized for dev boards. The custom PCB in Phase 10 is what shrinks them.
- Both temples can't fold flat at the same time because the pods stack. Each folds to about 90° on its own.
- The HUD tower stands about 27 mm above the brow because the light path needs 25 mm of focal length. It is a bench-validation housing, not the final form factor.
- The micro-OLED in the BOM needs an HDMI source, so it can't run from the ESP32 alone (see `BOM.md`).
