# Manufacturing guide (v0.2, one unit)

```
PRINT ──► BENCH (visor electronics) ──► BRICK ──► OPTICS ──► ASSEMBLE ──► SAFETY TEST ──► QA SHEET
```

## 0 · You need
- **Parts:** [`BOM.md`](BOM.md)
- **Tools:**
  - Bambu Lab P1S (or A1 / A1 Mini)
  - Soldering iron + heat-set tip
  - Wire strippers for 30 AWG, multimeter, calipers
  - Razor saw or tube cutter, 4.0 / 4.2 / 4.35 mm drills, conical punch
  - CA glue, Kapton, 1 mm foam tape
- **Software:** OpenSCAD, Bambu Studio, `esptool` (or ESP-IDF 5.5), Raspberry Pi OS on the brick

## 1 · Print
| Plate | File | Material |
|---|---|---|
| 0 | `cad/plates/plate_0_tolerance_coupon.3mf` | PETG. **Print first.** Copy the fits that work into `config.scad`, then run `./tools/build.sh`. |
| 1 | `cad/plates/plate_1_frame_temples_petg.3mf` | PETG, 0.16 mm, 4 walls |
| 2 | `cad/plates/plate_2_visor_petg.3mf` | **Black** PETG (stops light leaking in) |
| 3 | `cad/plates/plate_3_tpu_grips.3mf` | TPU 95A, external spool |

**Post-process:**
- Frame: ream the temple knuckles to 4.35 mm (they turn) and the visor knuckles to 4.2 mm (friction holds the visor up).
- Temples and visor knuckles: drill to 4.05 mm (the tubes are glued here).
- Visor: heat-set 4 M2 inserts in the back bosses.
- Frame: press the 6 × 3 magnet into the brow center.

## 2 · Bench: visor electronics (before anything goes into plastic)
1. Wire the XIAO to both 1.69″ screens, the IMU, the hall switch, the button and the battery divider exactly as in [`pinout.md`](pinout.md). Tie the screen RST pins to 3V3.
2. Flash the firmware:
   ```bash
   pip install esptool
   esptool.py --chip esp32s3 write_flash 0x0 firmware/glasses_mcu/prebuilt/asg_glasses_mcu_merged.bin
   ```
3. The serial monitor should show the self-test: IMU PASS and a battery voltage.
4. Both screens should show animated eyes.
5. Press the button to cycle designs. A magnet near the hall switch toggles visor DOWN/UP.
6. Open the web app's **Glasses** tab, connect, and change the design and text from your phone.

## 3 · Brick
```bash
git clone https://github.com/<you>/adaptive-smart-glasses && cd adaptive-smart-glasses
bash brick/setup_brick.sh                 # OpenCV + the ASG-BRICK hotspot the visor joins
python3 brick/passthrough.py              # camera -> side-by-side 3840x1080 fullscreen
```
- Test on a normal monitor first.
- Unplug the camera: a red LIFT VISOR screen should appear in under 0.25 s.

## 4 · Optics (EXPERIMENTAL)
- Connect the dual micro-OLED kit's HDMI board to the Pi and set 3840×1080. Check the board's supported modes first.
- Measure the eyepiece (diameter, length) and the driver board. Set `eyepiece_d`, `eyepiece_len` and `hdmi_board` in `config.scad`, then rebuild `visor_back` and `visor_shell`.
- Set `ipd` to your pupil distance so the sleeves center on your eyes.

## 5 · Assemble
1. **Earpieces:**
   - Charge both cells to 4.2 V separately.
   - Lay each cell in its bay, leads toward the ear bend.
   - Run the leads along the groove to the temple tube.
2. **Hinges:**
   - Thread the wires first.
   - Glue a tube into each temple knuckle (13.5 mm) and each visor knuckle (12 mm).
   - Push the tubes into the frame knuckles and flare the ends.
   - The right cell's wires cross the brow groove to the left visor tube.
3. **Visor:**
   - Screens into their corner stops, facing out.
   - Camera board behind the lens hole.
   - LED + 1k next to the camera.
   - Switches and button into the crest slots.
   - XIAO + IMU in the bridge, HDMI board on the rails.
   - Hall switch on the back plate, centered, facing the brow magnet.
   - Eyepieces in the back-plate sleeves.
   - Back plate on with 4 × M2×6.
4. **Cable:** HDMI + USB into the crest, zip-tied to the internal bar, then clipped along the left temple.
5. **Finish:** grips over the earpieces, nose pads on.

## 6 · Safety test + QA sheet
| # | Check | Pass when | ☐ |
|---|---|---|---|
| 1 | Self-test | IMU PASS, battery 3.0–4.3 V | ☐ |
| 2 | Designs | Eyes, rings, rainbow, text and off all work from both the button and the app | ☐ |
| 3 | Camera kill | SW2 off: the LED is off and the brick sees no camera | ☐ |
| 4 | Camera LED | On every time the camera has power | ☐ |
| 5 | Stall fail-safe | Unplug the camera: red LIFT VISOR in under 0.25 s | ☐ |
| 6 | Visor up | Both screen pairs go dark. The visor stays up by friction. | ☐ |
| 7 | Hinges | 20 folds of each temple and 20 flips of the visor with battery continuity held | ☐ |
| 8 | Latency | Film a stopwatch through the eyepiece: ≤ 120 ms | ☐ |
| 9 | Comfort | 15 min seated, no hot spots, no pressure points | ☐ |
