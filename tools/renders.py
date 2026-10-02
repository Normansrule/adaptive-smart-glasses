#!/usr/bin/env python3
"""Regenerate the README images in renders/ (needs: pip install playwright pillow; playwright install chromium; openscad).
   python3 tools/renders.py
"""
import asyncio, math, os, subprocess, threading, http.server, functools, tempfile
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "renders")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(sz, bold=False):
    try: return ImageFont.truetype(FONTB if bold else FONT, sz)
    except OSError: return ImageFont.load_default()

SPLAY, AX, AY, TZ = 6.05, 67.7, 11.55, 15.0
def pod(side, y, z=0.0, x=3.0):
    t = math.radians(-SPLAY); xr = x*math.cos(t) - y*math.sin(t); yr = x*math.sin(t) + y*math.cos(t)
    return [side*(AX + xr), AY + yr, TZ + z]
ELECTRONICS = [   # (label, xyz, colour)
    ("ToF depth sensor", [0, 0, 25.5], "#4fc3f7"), ("BME280 (vented)", [30, 1, 24], "#81c784"),
    ("PTT button", [-66.8, 3, 30.5], "#ff8a80"), ("Privacy LED", [-66.8, 0, 23.4], "#ff5252"),
    ("Main power switch", [71, 4, -4], "#ffd54f"), ("Hinge tube (wires inside)", [AX, AY, TZ+3], "#bdbdbd"),
    ("Battery 800 mAh", pod(1, 31), "#ffb74d"), ("Charger + 5V boost / USB-C", pod(1, 77, 0, 1), "#ffb74d"),
    ("Mic (lid port)", pod(-1, 17, 0, 6), "#ce93d8"), ("IMU", pod(-1, 41, 0, 6), "#ce93d8"),
    ("XIAO ESP32-S3 / USB-C", pod(-1, 81, 0, 6), "#e57373"), ("2x I2S amps", pod(-1, 28, 0, 0), "#90a4ae"),
    ("Speaker grille", pod(-1, 74, -2, -3), "#90a4ae"),
    ("Bone transducer", [-(AX + (-7)*math.cos(math.radians(-SPLAY)) - 111.5*math.sin(math.radians(-SPLAY))),
                         AY + (-7)*math.sin(math.radians(-SPLAY)) + 111.5*math.cos(math.radians(-SPLAY)), TZ - 16.4], "#a1887f"),
    ("Micro-OLED (slider)", [-31.5, -14.8, 48], "#fff176"), ("Combiner 30R/70T", [-31.5, -14.8, 6], "#80deea"),
]
PART_NAMES = {"frame": "Front frame", "temple_left": "Temple L · power", "temple_right": "Temple R · compute",
              "lid_left": "Lid L", "lid_right": "Lid R", "ear_grip_left": "Ear grip L (TPU)", "ear_grip_right": "Ear grip R (TPU)",
              "optics_tower": "HUD tower", "display_slider": "Display slider", "combiner_arm": "Combiner arm"}

def callouts(img, pts, labels, colors=None, ring=False):
    d = ImageDraw.Draw(img); W, H = img.size; cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
    f = font(19, True); placed = []
    for i, ((x, y), lab) in enumerate(zip(pts, labels)):
        c = (colors or ["#ff4d3d"]*len(pts))[i]
        ang = math.atan2(y - cy, x - cx); r = 95
        lx, ly = x + r*math.cos(ang), y + r*math.sin(ang)
        for _ in range(30):                                 # nudge to avoid overlaps
            if all(abs(ly - py) > 28 or abs(lx - px) > 260 for px, py in placed): break
            ly += 26 if ly > cy else -26
        lx = min(max(lx, 10), W - 10); ly = min(max(ly, 16), H - 16); placed.append((lx, ly))
        tw = d.textlength(lab, font=f); left = lx < x
        tx = lx - tw - 8 if left else lx + 8
        tx = min(max(tx, 6), W - tw - 6)
        d.line([(x, y), (lx, ly)], fill=c, width=3)
        d.ellipse([x-6, y-6, x+6, y+6], fill=c, outline="#0f1216", width=2)
        d.rounded_rectangle([tx-6, ly-15, tx+tw+6, ly+15], radius=7, fill=(15, 18, 22, 235), outline=c, width=2)
        d.text((tx, ly-11), lab, fill="#ffffff", font=f)
    return img

def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    h.log_message = lambda *a, **k: None
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 8799), h); threading.Thread(target=s.serve_forever, daemon=True).start(); return s

async def viewer_shots():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1700, "height": 1000}, color_scheme="dark")
        await pg.goto("http://127.0.0.1:8799/index.html"); await pg.wait_for_function("window.__ready && window.__ready()", timeout=90000)
        view = pg.locator("#view")
        async def shot(name, v, k, hud, ghost=False, pts=None, pos=None):
            await pg.evaluate(f"window.__setView('{v}', {k}, {str(hud).lower()}, {pos or 'null'})"); await pg.evaluate(f"window.__ghost({str(ghost).lower()})")
            await pg.wait_for_timeout(1500); path = os.path.join(OUT, name); await view.screenshot(path=path)
            return path, (await pg.evaluate("p => window.__project(p)", pts) if pts else None)
        await shot("hero.png", "iso", 0, True)
        await shot("front.png", "front", 0, True)
        EXP = [-250, -300, 360]
        centers = await pg.evaluate(f"(window.__setView('iso', 1, true, {EXP}), window.__partCenters())")
        ids = list(centers); path, pts = await shot("exploded.png", "iso", 1, True, pts=[centers[i] for i in ids], pos=EXP)
        callouts(Image.open(path).convert("RGB"), pts, [PART_NAMES[i] for i in ids]).save(path)
        EL = [e for e in ELECTRONICS if "OLED" not in e[0] and "Combiner" not in e[0]]
        path, pts = await shot("electronics.png", "iso", 0, False, ghost=True, pts=[e[1] for e in EL], pos=[240, 360, 260])
        callouts(Image.open(path).convert("RGB"), pts, [e[0] for e in EL], [e[2] for e in EL]).save(path)
        await b.close()

def gallery():
    parts = ["frame", "temple_left", "temple_right", "lid_left", "ear_grip_right", "optics_tower", "display_slider", "combiner_arm", "tolerance_coupon"]
    tiles = []
    with tempfile.TemporaryDirectory() as td:
        for p in parts:
            scad = os.path.join(td, "v.scad"); png = os.path.join(td, p + ".png")
            open(scad, "w").write(f'color("#4a5466") import("{ROOT}/cad/stl/{p}.stl");')
            subprocess.run(["xvfb-run", "-a", "openscad", scad, "--autocenter", "--viewall", "--camera=0,0,0,55,0,25,0",
                            "--imgsize=600,440", "--colorscheme=Tomorrow", "-o", png], capture_output=True)
            tiles.append((p, Image.open(png).convert("RGB")))
    cols, tw, th = 3, 600, 480
    G = Image.new("RGB", (cols*tw, math.ceil(len(tiles)/cols)*th), "#f7f8fa"); d = ImageDraw.Draw(G)
    for i, (p, im) in enumerate(tiles):
        x, y = (i % cols)*tw, (i // cols)*th; G.paste(im, (x, y+40))
        d.text((x+18, y+12), p, fill="#14181d", font=font(24, True))
        d.text((x+18, y+446), "TPU 95A" if "grip" in p else ("calibration" if "coupon" in p else "PETG"), fill="#5d6773", font=font(18))
    G.save(os.path.join(OUT, "parts_gallery.png"))

def hinge_section():
    scad = os.path.join(ROOT, "cad", "_section.scad")
    open(scad, "w").write('''use <adaptive_smart_glasses.scad>
include <config.scad>
ax = dbl/2 + lens_w + rim + endpiece_w - knuckle_r; ay = brow_depth + knuckle_r + hinge_gap;
intersection() {
  union() { color("#59616e") asm("frame"); color("#8a93a3") asm("temple_left");
            color("#d4a640") translate([ax, ay, tz-6.5]) difference() { cylinder(d=4, h=13.5, $fn=48); translate([0,0,-1]) cylinder(d=3.1, h=16, $fn=48); }
            color("#e74c3c") for (dx=[-0.6,0.6]) translate([ax+dx, ay, tz-8]) cylinder(d=0.9, h=17, $fn=12); }
  translate([ax-14, ay, tz-13]) cube([28, 30, 26]);
}
''')
    subprocess.run(["xvfb-run", "-a", "openscad", scad, "--camera=67.7,-25,15,67.7,11.55,15", "--projection=p", "--imgsize=900,700",
                    "--colorscheme=Tomorrow", "-o", os.path.join(OUT, "hinge_section.png")], capture_output=True)
    os.remove(scad)
    im = Image.open(os.path.join(OUT, "hinge_section.png")).convert("RGB"); d = ImageDraw.Draw(im)
    d.text((24, 20), "Hollow-pin hinge (section): wires run up the brass tube and twist instead of bending", fill="#14181d", font=font(20, True))
    im.save(os.path.join(OUT, "hinge_section.png"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); s = serve()
    asyncio.run(viewer_shots()); s.shutdown()
    gallery(); print("renders/ updated")
