#!/usr/bin/env python3
"""Post-process OpenSCAD exports (no third-party packages needed).

- print parts  -> cad/stl/<part>.stl (binary, on the bed: min z = 0, centred XY)
                  cad/3mf/<part>.3mf
- assembly     -> models/<part>.stl (binary, assembly coordinates, for the web viewer)
- plates       -> cad/plates/*.3mf  (multi-object, laid out on a 256 x 256 P1S plate)
- stats        -> cad/part_stats.json (bbox, triangles, volume, watertight check, fits A1 mini)
"""
import json, math, os, struct, sys, zipfile
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATERIAL = {"ear_grip_left": "TPU 95A", "ear_grip_right": "TPU 95A"}
DENSITY = {"PETG": 1.27, "TPU 95A": 1.21}
PLATES = {
    "plate_1_core_petg": ["frame", "temple_left", "temple_right", "lid_left", "lid_right"],
    "plate_2_tpu_grips": ["ear_grip_left", "ear_grip_right"],
    "plate_3_hud_petg_EXPERIMENTAL": ["optics_tower", "display_slider", "combiner_arm"],
    "plate_0_tolerance_coupon": ["tolerance_coupon"],
}
BED = 256.0

def read_stl(path):
    data = open(path, "rb").read()
    tris = []
    if data[:5] == b"solid" and b"facet" in data[:400]:
        v = []
        for line in data.decode("ascii", "ignore").splitlines():
            t = line.split()
            if t and t[0] == "vertex":
                v.append((float(t[1]), float(t[2]), float(t[3])))
                if len(v) == 3:
                    tris.append(tuple(v)); v = []
    else:
        n = struct.unpack("<I", data[80:84])[0]
        for i in range(n):
            f = struct.unpack("<12f", data[84 + 50*i: 84 + 50*i + 48])
            tris.append(((f[3], f[4], f[5]), (f[6], f[7], f[8]), (f[9], f[10], f[11])))
    return tris

def bbox(tris):
    xs = [p[0] for t in tris for p in t]; ys = [p[1] for t in tris for p in t]; zs = [p[2] for t in tris for p in t]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

def translate(tris, d):
    return [tuple((p[0]+d[0], p[1]+d[1], p[2]+d[2]) for p in t) for t in tris]

def normal(t):
    a, b, c = t
    u = (b[0]-a[0], b[1]-a[1], b[2]-a[2]); v = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    l = math.sqrt(n[0]**2+n[1]**2+n[2]**2) or 1.0
    return (n[0]/l, n[1]/l, n[2]/l)

def write_stl(path, tris, name):
    with open(path, "wb") as f:
        f.write(name.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            f.write(struct.pack("<3f", *normal(t)))
            for p in t: f.write(struct.pack("<3f", *p))
            f.write(b"\0\0")

def volume(tris):
    s = 0.0
    for a, b, c in tris:
        s += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
    return s/6.0

def watertight(tris):
    key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4))
    e = Counter()
    for t in tris:
        k = [key(p) for p in t]
        for i in range(3):
            e[(k[i], k[(i+1) % 3])] += 1
    bad = sum(1 for (a, b), n in e.items() if n != 1 or e.get((b, a), 0) != 1)
    return bad == 0, bad

def mesh_xml(tris, oid, name):
    idx, verts, faces = {}, [], []
    for t in tris:
        f = []
        for p in t:
            k = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
            if k not in idx:
                idx[k] = len(verts); verts.append(k)
            f.append(idx[k])
        if len(set(f)) == 3: faces.append(f)
    out = [f'  <object id="{oid}" name="{name}" type="model"><mesh><vertices>']
    out += [f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in verts]
    out.append('</vertices><triangles>')
    out += [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces]
    out.append('</triangles></mesh></object>')
    return "\n".join(out)

def write_3mf(path, objects):   # objects: [(name, tris, (tx,ty,tz))]
    model = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
             ' <metadata name="Application">adaptive-smart-glasses tools/postprocess.py</metadata>', ' <resources>']
    for i, (name, tris, _) in enumerate(objects, 1):
        model.append(mesh_xml(tris, i, name))
    model.append(' </resources>\n <build>')
    for i, (_, _, t) in enumerate(objects, 1):
        model.append(f'  <item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {t[0]:.3f} {t[1]:.3f} {t[2]:.3f}"/>')
    model.append(' </build>\n</model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", "\n".join(model))

def pack(sizes, gap=6.0):
    """simple shelf packing on a BED x BED plate; returns {name: (x0,y0)} lower-left corners"""
    order = sorted(sizes, key=lambda n: -sizes[n][1])
    pos, x, y, row_h = {}, gap, gap, 0.0
    for n in order:
        w, h = sizes[n]
        if x + w + gap > BED:
            x, y, row_h = gap, y + row_h + gap, 0.0
        pos[n] = (x, y); x += w + gap; row_h = max(row_h, h)
    used_h = y + row_h + gap
    if used_h > BED: raise SystemExit(f"plate overflow ({used_h:.0f} mm) — split the plate")
    dy = (BED - used_h) / 2
    return {n: (p[0], p[1] + dy) for n, p in pos.items()}

def main(tmp):
    stats_path = os.path.join(ROOT, "cad", "part_stats.json")
    stats = json.load(open(stats_path)) if os.path.exists(stats_path) else {}
    printed = {}
    for fn in sorted(os.listdir(tmp)):
        if not fn.endswith(".stl"): continue
        name = fn[:-4]; tris = read_stl(os.path.join(tmp, fn))
        if name.startswith("asm_"):
            write_stl(os.path.join(ROOT, "models", name[4:] + ".stl"), tris, name)
            continue
        (x0, y0, z0), (x1, y1, z1) = bbox(tris)
        tris = translate(tris, (-(x0+x1)/2, -(y0+y1)/2, -z0))
        printed[name] = tris
        write_stl(os.path.join(ROOT, "cad", "stl", name + ".stl"), tris, name)
        write_3mf(os.path.join(ROOT, "cad", "3mf", name + ".3mf"), [(name, tris, (BED/2, BED/2, 0))])
        mat = MATERIAL.get(name, "PETG")
        vol = abs(volume(tris)) / 1000.0
        ok, bad = watertight(tris)
        dims = [round(x1-x0, 1), round(y1-y0, 1), round(z1-z0, 1)]
        stats[name] = {"bbox_mm": dims, "triangles": len(tris), "solid_volume_cm3": round(vol, 2),
                       "material": mat, "solid_mass_g": round(vol*DENSITY[mat], 1),
                       "watertight": ok, "open_edges": bad,
                       "fits_P1S": max(dims[:2]) <= BED and dims[2] <= 256,
                       "fits_A1_mini": max(dims[:2]) <= 180 and dims[2] <= 180}
        print(f"  {name:18s} {dims} mm  {vol:6.2f} cm3  watertight={ok}")
    json.dump(stats, open(stats_path, "w"), indent=1)
    # plates (only when all their parts were rebuilt in this run)
    for plate, names in PLATES.items():
        if not all(n in printed for n in names): continue
        sizes = {}
        for n in names:
            (a0, b0, _), (a1, b1, _) = bbox(printed[n]); sizes[n] = (a1-a0, b1-b0)
        pos = pack(sizes)
        objs = [(n, printed[n], (pos[n][0] + sizes[n][0]/2, pos[n][1] + sizes[n][1]/2, 0)) for n in names]
        write_3mf(os.path.join(ROOT, "cad", "plates", plate + ".3mf"), objs)
        print(f"  plate {plate}: {', '.join(names)}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build_tmp")
