# Customization (`cad/config.scad`)

| Parameter | Default | What it does |
|---|---|---|
| `ipd` | 63 | Pupil distance: centers both eyepiece sleeves. **Set this to your own.** |
| `eye_relief` | 17 | Eye-to-eyepiece distance. The visor position follows it. |
| `head_width`, `ear_y`, `ear_droop` | 148, 98, 55° | Temple splay, ear bend, earpiece angle |
| `cell` | [40, 10, 5] | Earpiece battery bay (L × W × T). For an LP401235, use [36, 12, 4]. |
| `eyepiece_d`, `eyepiece_len` | 26, 22 | **[MEASURE]** your eyepieces |
| `hdmi_board` | [45, 28, 7] | **[MEASURE]** the dual micro-OLED driver board |
| `lcd`, `lcd_active` | 39 × 31.5, 32.6 × 28 | Waveshare 1.69″ screen (outline confirmed, thickness [MEASURE]) |
| `cam_board`, `cam_lens_d`, `cam_z` | 24 × 25, 12, 16.4 | Arducam IMX708 UVC board and lens hole |
| `visor_tube_run` | 4.2 | Frame-side visor bore. Smaller means stiffer (holds the visor up). Tune it on the coupon. |
| `visor_up_deg` | 100 | Flip angle checked by `tools/check_fit.py` |
| `tol`, `insert_hole_d`, `tube_hole_glue`, `tube_hole_run` | 0.3, 3.1, 4.05, 4.35 | Print fits. Tune on the coupon. |

After any change, run `./tools/build.sh && python3 tools/check_fit.py`.
