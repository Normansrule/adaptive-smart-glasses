# CAD: build, print, assemble (v0.2)

Source: `cad/adaptive_smart_glasses.scad` + `cad/config.scad`.
Outputs: `cad/stl/`, `cad/3mf/`, `cad/plates/`, `models/` (web viewer), `cad/part_stats.json`.

```bash
./tools/build.sh                 # all parts (~1 min)
python3 tools/check_fit.py       # collision checks: visor 0/35/70/100 deg, temple fold, shell vs back plate
openscad -D 'part="assembly_up"' cad/adaptive_smart_glasses.scad   # visor-up preview
```

## Parts
| Part | Material | Print orientation | Holds |
|---|---|---|---|
| frame | PETG | front face down | nose pads, temple + visor hinge knuckles, hall magnet |
| temple_left / temple_right | PETG | head face down | slim arm, earpiece battery bay |
| ear_grip_left / ear_grip_right | TPU 95A | entry end down | closes the battery bay, comfort |
| visor_shell | black PETG | front face down | 2 design screens, camera + LED, crest controls, bridge electronics, visor knuckles |
| visor_back | black PETG | eye side down | eyepiece sleeves (at your IPD), driver-board rail |
| tolerance_coupon | PETG | flat | fit tests |

## Checked in CAD
- All parts are watertight and print with no supports.
- No collisions at rest, with the visor at 35, 70 and 100 degrees, or with a temple folded to 80 degrees.
- The visor clears the frame through its whole travel. The hinge axis sits on top of the brow (Y = +3.3 mm, Z = 27.5 mm).

## Hinges
- **Temples:** a vertical brass-tube pin, with that side's cell wires inside it.
- **Visor:** a horizontal brass-tube pin along X at each end.
  - The tube is glued in the visor knuckle and turns snugly in the frame knuckle (4.2 mm bore), so friction holds the visor up.
  - The left tube carries all 4 battery wires.
