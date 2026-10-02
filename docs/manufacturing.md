# Manufacturing guide (one unit, about one day)

```
 PRINT ──► PREP BOARDS ──► BENCH-WIRE + TEST ──► HARNESS ──► ASSEMBLE ──► FACTORY TEST ──► QA SHEET
 (≈6 h)      (30 min)          (1 h)              (1 h)        (1 h)         (10 min)
```

## 0 · What you need
- **Bill of Materials (BOM):** [`BOM.md`](BOM.md) / [`../bom.csv`](../bom.csv)
- **Tools:**
  - Bambu Lab P1S (or A1 / A1 Mini)
  - Soldering iron with a heat-set insert tip
  - Flush cutters, wire strippers for 28–30 AWG, multimeter
  - Calipers
  - Tube cutter or razor saw, a 4 mm drill bit, a conical punch
  - CA glue, Kapton tape, 1 mm foam tape
- **Software:** OpenSCAD, Bambu Studio, ESP-IDF 5.5 (for the factory test)

## 1 · Print
| Plate | File | Material | Notes |
|---|---|---|---|
| 0 | `cad/plates/plate_0_tolerance_coupon.3mf` | PETG | **First.** Tune `config.scad`, then run `./tools/build.sh`. |
| 1 | `cad/plates/plate_1_core_petg.3mf` | PETG | Frame, 2 temples, 2 lids. 0.16 mm layers, 4 walls. |
| 2 | `cad/plates/plate_2_tpu_grips.3mf` | TPU 95A | Feed from the external spool, not the AMS. |
| 3 | `cad/plates/plate_3_hud_petg_EXPERIMENTAL.3mf` | black PETG | Only for Phase 5. |

**Post-process:**
- Remove brims and stringing.
- Ream the frame knuckle bores to a 4.35 mm running fit.
- Drill the temple knuckle bores to a 4.05 mm glue fit.
- Heat-set 1 M2 insert in each temple rib. Add 2 in the brow front only if you're building the HUD.

## 2 · Prepare the boards
| Board | Action |
|---|---|
| U8 Adafruit 6106 | Cut the **ISET** jumper (500 mA charge). Desolder **R16** and solder the NTC leads to its pads. Don't fit the terminal block. Solder wires to the 5V+ / 5V− pads. |
| U2 ToF | Nothing to do. It plugs in with Qwiic cables. |
| U4 BME280 | Remove header pins if fitted. Check the chip says BME280 (the test reads ID 0x60). |
| U5 Mic | Tie SEL to GND with a short wire. |
| U6, U7 Amps | Leave GAIN open. Don't fit the screw terminals. Solder the speaker wires directly. |
| U1 XIAO | Solder a Qwiic pigtail to 3V3 / GND / D4 / D5. |

## 3 · Bench-wire and test (before anything goes into plastic)
1. Wire everything flat on the bench, exactly per [`pinout.md`](pinout.md), with longer leads.
2. Flash the factory test:
   ```bash
   . ~/esp/esp-idf/export.sh
   cd firmware/factory_test
   idf.py set-target esp32s3 build flash monitor
   ```
3. Every automatic check must PASS and both tones must be heard. Fix it here, not inside the frame.

## 4 · Harness
- Cut the wires from [`../hardware/wire_cut_list.csv`](../hardware/wire_cut_list.csv). Colours: red 5 V, black GND, green VBAT_SENSE, white MIC_3V3, Qwiic colours for I²C.
- Cut two 13.5 mm brass tubes and deburr them inside and out.
- **Thread the hinge wires through each tube before you solder the far ends.** Right tube: 7 wires. Left tube: 3.

## 5 · Assemble (see [`README_CAD.md`](README_CAD.md))
1. Glue each tube into its temple knuckle, push it up through the frame knuckle, and flare the top.
2. Fit the frame electronics: ToF, BME280, PTT switch, LED + 1k, main switch. Press the wires into the brow groove and cover with Kapton.
3. Left pod: charger on its pins (USB-C out the back), battery in its foam bay, NTC taped to the cell.
4. Right pod:
   - Inner layer: amps, speaker.
   - Then a layer of foam.
   - Outer layer: mic, IMU, XIAO, with D2/D3/R2–R4 sleeved in heat-shrink.
5. Lids: hook the front tab, slide forward, fit 1 × M2×5.
6. Push the grips on and press the bone transducer into the right grip.
7. Stick the nose pads on.

## 6 · Factory test + QA sheet (record for every unit)
| # | Check | Pass when | Result |
|---|---|---|---|
| 1 | Factory test firmware | `RESULT: PASS` | ☐ |
| 2 | Bone tone audible | Heard through the bone, not too loud | ☐ |
| 3 | Outward tone audible | Heard, not too loud | ☐ |
| 4 | Privacy LED | ON only while PTT is held | ☐ |
| 5 | Mic rail with a meter (PTT released) | MIC_3V3 below 0.1 V | ☐ |
| 6 | Charging | Orange LED on the charger, cell warm at most, USB-C reachable | ☐ |
| 7 | Main switch | OFF kills the system and charging still works | ☐ |
| 8 | Hinges | 20 folds each with continuity held (production sample: 2,000) | ☐ |
| 9 | Fit | No pressure points after 15 min of wear. Nose and ears comfortable. | ☐ |
| 10 | Edges | No sharp edges or burrs touching skin | ☐ |
