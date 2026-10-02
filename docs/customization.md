# Customization (`cad/config.scad`)

Edit a value, run `./tools/build.sh`, re-print only the parts that changed.

## Fit to your head
| Parameter | Default | What it does |
|---|---|---|
| `head_width` | 148 | Head breadth just above the ears. The temple splay is calculated from it (prints `splay=` in the console). |
| `ear_y` | 100 | Distance from the hinge axis to the ear bend. Measure from the front hinge to the top of the ear. |
| `ear_droop`, `earpiece_len` | 55°, 40 | Earpiece angle and length behind the ear. |
| `ipd` | 63 | Inter-Pupillary Distance (IPD). Moves the HUD tower and its brow inserts. |
| `lens_w`, `lens_h`, `dbl` | 52, 36, 20 | Lens opening and bridge width. Total frame width = `dbl + 2·lens_w + 2·rim + 2·endpiece_w`. |

## Tolerances (tune with `tolerance_coupon`)
| Parameter | Default | Coupon test |
|---|---|---|
| `tol` | 0.30 | General pocket clearance per side (0.25–0.50). |
| `insert_hole_d` | 3.1 | Use the hole where the M2 insert goes in straight and does not spin when you tighten a screw. |
| `tube_hole_glue` | 4.05 | Tube slides in with light friction, ready for CA. |
| `tube_hole_run` | 4.35 | Tube turns freely without wobble. |
| PCB slot | 1.6 + 0.2 | The ToF board slides in without force. |

## Modules: measure, then edit
`bme`, `batt`, `mic`, `spk_d`/`spk_t`, `bone`, `ptt`, `msw`/`msw_slot`, `disp_mod` are tagged `[MEASURE]`.

Outlines confirmed from vendor CAD: ToF (25.4 × 12.7), charger (29.21 × 19.05 + holes), IMU (25.4 × 17.78), amp (19.05 × 17.78).

## Common changes
- **Bigger battery (802060, 1100 mAh):** `batt=[62,20,8]`, `pod_len=104.2`, `rib_y=63.5`. Check the pod still ends before the ear: `pod_y0 + pod_len < ear_y`. If not, raise `ear_y`.
- **Second bone transducer:** `bone_left=true`. Wire it in parallel on the same amp (8 Ω ∥ 8 Ω = 4 Ω, which the MAX98357A supports).
- **HUD on the left eye:** `hud_side=+1`. The brow inserts move with it, and the BME pocket must then move: set `bme_x0=-37.5`.
- **Different micro-display:** set `disp_mod` (module outline) and `lens_bfl`. The slider covers ±6 mm.
- **Looser hinge:** raise `tube_hole_run`. **Stiffer open-stop:** the stop block lives in `temple_hinge_part()`.

## Rules the geometry depends on
- The temple inner face (`bar_in`) must equal `-knuckle_r` so the temple prints flat on its head side.
- `pod_endwall` must stay ≤ 1.6 mm so the USB-C plugs reach the receptacles.
- The ToF window is an open aperture. Don't put a printed or acrylic cover over it unless you also run ST's crosstalk calibration.
