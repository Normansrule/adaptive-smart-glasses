#!/usr/bin/env python3
"""Collision checks with OpenSCAD intersections (no extra packages).
   python3 tools/check_fit.py      -> prints overlap volume (mm^3) for every pair that must not touch"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__)); import postprocess as pp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "cad", "adaptive_smart_glasses.scad")
TEMPLATE = '''use <{scad}>
include <{cfg}>
lens_cx = dbl/2 + lens_w/2; half_w = dbl/2 + lens_w + rim + endpiece_w;
ax = half_w - knuckle_r; ay = brow_depth + knuckle_r + hinge_gap;
module place(p, up, fold) {{
  if (fold != 0 && p == "temple_left") translate([ax, ay, 0]) rotate([0,0,fold]) translate([-ax, -ay, 0]) asm(p, up);
  else asm(p, up);
}}
intersection() {{ place("{a}", {up}, {fold}); place("{b}", {up}, {fold}); }}
'''
CHECKS = [  # (a, b, visor angle, temple fold, label)
    ("frame", "temple_left", 0, 0, "temple at rest"), ("frame", "temple_right", 0, 0, "temple at rest"),
    ("frame", "temple_left", 0, 80, "temple folded 80 deg"),
    ("frame", "visor_shell", 0, 0, "visor down"), ("frame", "visor_back", 0, 0, "visor down"),
    ("frame", "visor_shell", 35, 0, "visor 35 deg"), ("frame", "visor_shell", 70, 0, "visor 70 deg"),
    ("frame", "visor_shell", 100, 0, "visor up 100 deg"), ("frame", "visor_back", 100, 0, "visor up 100 deg"),
    ("temple_left", "visor_shell", 0, 0, "visor down vs temple"), ("temple_left", "visor_shell", 100, 0, "visor up vs temple"),
    ("visor_shell", "visor_back", 0, 0, "shell vs back plate (touching only)"),
]
def run():
    worst = 0.0
    with tempfile.TemporaryDirectory() as td:
        for a, b, up, fold, label in CHECKS:
            f = os.path.join(td, "x.scad"); o = os.path.join(td, "x.stl")
            open(f, "w").write(TEMPLATE.format(scad=SCAD, cfg=os.path.join(ROOT, "cad", "config.scad"), a=a, b=b, up=up, fold=fold))
            r = subprocess.run(["openscad", "-o", o, f], capture_output=True, text=True)
            v = 0.0
            if "empty" not in r.stderr and os.path.exists(o):
                t = pp.read_stl(o); v = abs(pp.volume(t)) if t else 0.0
            worst = max(worst, v)
            print(f"  {'OK ' if v < 0.5 else 'HIT'}  {a:12s} x {b:12s} {label:34s} overlap {v:8.2f} mm3")
    return worst
if __name__ == "__main__":
    sys.exit(0 if run() < 0.5 else 1)
