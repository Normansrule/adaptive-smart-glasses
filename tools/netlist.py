#!/usr/bin/env python3
"""Single source of truth for the electrical build.

Writes:
  hardware/netlist.csv          one row per pin connection (machine-readable)
  hardware/wire_cut_list.csv    harness wires with gauge, colour, length, route
  docs/img/wiring_power.svg     power + microphone-privacy diagram
  docs/img/wiring_signals.svg   I2C / I2S / audio diagram
  docs/pinout.md                pin-by-pin tables for every module
Edit the tables below, then run:  python3 tools/netlist.py
"""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ref: (name, part, location)
PARTS = {
 "J1":  ("Brick cable",     "micro-HDMI->HDMI + USB 4-core, braided",       "Enters visor crest, left side"),
 "BT1": ("Cell LEFT",       "Protected 1S LiPo 501040 200 mAh",             "Left earpiece"),
 "BT2": ("Cell RIGHT",      "Protected 1S LiPo 501040 200 mAh",             "Right earpiece"),
 "SW1": ("Main power",      "Wurth 452403012014 DPDT slide",                "Visor crest top"),
 "SW2": ("Camera kill",     "Wurth 452403012014 DPDT slide",                "Visor crest top"),
 "D1":  ("CAMERA LIVE LED", "3 mm red LED",                                 "Visor front, beside camera"),
 "R1":  ("1k",              "1k 1/8 W",                                     "Visor crest"),
 "D2":  ("1N5817",          "1N5817 Schottky",                              "Visor crest"),
 "U1":  ("XIAO ESP32-S3",   "Seeed XIAO ESP32-S3 (non-Sense)",              "Visor bridge, behind camera"),
 "R2":  ("100k top",        "100k 1/8 W",                                   "Visor bridge"),
 "R3":  ("100k bottom",     "100k 1/8 W",                                   "Visor bridge"),
 "U2":  ("Camera",          "Arducam IMX708 UVC 102 deg",                   "Visor centre bridge, front"),
 "U3":  ("IMU",             "Adafruit 4438 LSM6DSOX",                       "Visor bridge"),
 "U4":  ("Hall switch",     "TI DRV5032FA on SOT-23 adapter",               "Back of visor bridge, faces brow magnet"),
 "U5":  ("LCD LEFT",        "Waveshare 1.69in 240x280 ST7789V2",            "Left pod, front"),
 "U6":  ("LCD RIGHT",       "Waveshare 1.69in 240x280 ST7789V2",            "Right pod, front"),
 "U7":  ("Micro-OLED board","Dual 0.71in micro-OLED HDMI driver",           "Visor crest bay"),
 "SW3": ("Action button",   "Omron B3F-1000 6x6 tact",                      "Visor crest top flexure"),
}
NETS = [
 ("BAT+",     "#c0392b", "28 AWG red",  "Both cells in parallel",        [("BT1","+"),("BT2","+"),("SW1","COM")]),
 ("BAT_SW",   "#e74c3c", "local",       "Switched battery",              [("SW1","throw A"),("U1","BAT+ pad"),("R2","1")]),
 ("VBAT_DIV", "#2ecc71", "local",       "Half battery voltage to ADC",   [("R2","2"),("R3","1"),("U1","D3 (A2)")]),
 ("VBUS_5V",  "#ff7f50", "USB red",     "5 V from the brick / power bank", [("J1","USB VBUS"),("D2","anode"),("SW2","COM"),("U7","5V in")]),
 ("XIAO_5V",  "#ff9f80", "local",       "XIAO 5V pin, also charges the cells", [("D2","cathode (band)"),("U1","5V")]),
 ("CAM_5V",   "#e84393", "local",       "Camera power, ONLY with SW2 on", [("SW2","throw A"),("U2","5V (USB VBUS)"),("R1","1")]),
 ("LED_A",    "#fd79a8", "local",       "LED current limit",             [("R1","2"),("D1","anode (long leg)")]),
 ("GND",      "#2c3e50", "28 AWG black","Common ground",                 [("BT1","-"),("BT2","-"),("J1","USB GND / HDMI shell"),("U1","GND + BAT- pad"),("R3","2"),
                                                                            ("D1","cathode"),("U2","GND"),("U3","GND"),("U4","GND"),("U5","GND"),("U6","GND"),("U7","GND"),("SW3","pin 2")]),
 ("3V3",      "#f39c12", "local",       "Logic supply from the XIAO",    [("U1","3V3"),("U3","VIN (Qwiic)"),("U4","VCC"),("U5","VCC + RST"),("U6","VCC + RST")]),
 ("USB_D+",   "#0984e3", "USB green",   "Camera USB data to the brick",  [("J1","USB D+"),("U2","D+")]),
 ("USB_D-",   "#74b9ff", "USB white",   "",                              [("J1","USB D-"),("U2","D-")]),
 ("HDMI",     "#6c5ce7", "HDMI cable",  "Side-by-side 3840x1080 video",  [("J1","HDMI"),("U7","HDMI in")]),
 ("SPI_SCK",  "#00b894", "local",       "LCD clock (shared)",            [("U1","D8"),("U5","CLK"),("U6","CLK")]),
 ("SPI_MOSI", "#00cec9", "local",       "LCD data (shared)",             [("U1","D10"),("U5","DIN"),("U6","DIN")]),
 ("LCD_DC",   "#55efc4", "local",       "Data / command (shared)",       [("U1","D2"),("U5","DC"),("U6","DC")]),
 ("CS_L",     "#a29bfe", "local",       "Select left LCD",               [("U1","D0"),("U5","CS")]),
 ("CS_R",     "#b388ff", "local",       "Select right LCD",              [("U1","D1"),("U6","CS")]),
 ("LCD_BL",   "#fdcb6e", "local",       "Backlight PWM (shared)",        [("U1","D6"),("U5","BL"),("U6","BL")]),
 ("SDA",      "#2980b9", "Qwiic blue",  "I2C data",                      [("U1","D4"),("U3","SDA (Qwiic)")]),
 ("SCL",      "#f1c40f", "Qwiic yellow","I2C clock",                     [("U1","D5"),("U3","SCL (Qwiic)")]),
 ("HALL",     "#e17055", "local",       "Visor down = LOW",              [("U4","OUT"),("U1","D7")]),
 ("BUTTON",   "#d35400", "local",       "Action button (pull-up)",       [("SW3","pin 1"),("U1","D9")]),
 ("OLED_FPC", "#636e72", "panel flex", "Panel flex cables",              [("U7","FPC L / FPC R")]),
]
NC = [("U5","RST","tie to 3V3 (the firmware sends a software reset)"),("U6","RST","tie to 3V3"),
      ("U1","D3","ADC: VBAT/2"),("U7","5V in","power the HDMI board from VBUS, never from the XIAO 3V3"),
      ("BT1","before joining","charge both cells to 4.2 V separately, then wire them in parallel")]

# harness wires that cross hinges (cut length includes ~20% slack)
CUT = [
 ("BAT+ / GND (left cell)",  "30 AWG red/black", 230, "BT1 -> earpiece groove -> L temple tube -> frame -> L visor tube -> SW1"),
 ("BAT+ / GND (right cell)", "30 AWG red/black", 330, "BT2 -> R temple tube -> brow groove -> L visor tube -> SW1"),
 ("Brick cable",            "HDMI + USB 4-core", 1500, "Pocket brick -> clip along left temple -> visor crest (left side)"),
 ("LCD harness",            "8 x 30 AWG",        120, "U1 (bridge) -> U5 and U6 (shared SCK/MOSI/DC/BL/VCC/GND, own CS)"),
]

DIAGRAMS = {
 "wiring_power.svg":   ("Power + camera privacy",
                        ["BAT+","BAT_SW","VBAT_DIV","VBUS_5V","XIAO_5V","CAM_5V","LED_A","GND"],
                        ["BT1","BT2","|V","J1","|C","SW1","R2","R3","U1","D2","SW2","R1","D1","U2","U7"]),
 "wiring_signals.svg": ("Signals: displays, camera, sensors",
                        ["3V3","GND","SPI_SCK","SPI_MOSI","LCD_DC","CS_L","CS_R","LCD_BL","SDA","SCL","HALL","BUTTON","USB_D+","USB_D-","HDMI"],
                        ["J1","|C","U1","U5","U6","U3","U4","SW3","U2","U7"]),
}

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def svg(fname, title, nets, order):
    """Vertical harness diagram: modules stacked top-to-bottom in physical order (left pod -> right grip),
    pins on the box edge, each net is a coloured vertical rail. Readable at README width."""
    netmap = {n[0]: n for n in NETS}
    pins = {}
    for n in nets:
        for ref, pin in netmap[n][4]:
            pins.setdefault(ref, []).append((pin, n))
    refs = [r for r in order if r.startswith("|") or r in pins]
    BX, BW, PH, RX0, RDX, TOP = 20, 330, 22, 400, 34, 190
    W = RX0 + RDX * (len(nets) - 1) + 60
    o, y, ys = [], TOP, {}
    railx = {n: RX0 + i * RDX for i, n in enumerate(nets)}
    for r in refs:
        if r.startswith("|"):
            lab = {"L": "LEFT HINGE", "R": "RIGHT HINGE", "G": "EAR GRIP", "V": "TEMPLE + VISOR HINGES  (wires run through the brass tubes)", "C": "INSIDE THE VISOR"}[r[1]]
            o.append(f'<line x1="10" y1="{y+8}" x2="{W-10}" y2="{y+8}" stroke="#9aa3ad" stroke-width="2" stroke-dasharray="8 6"/>')
            o.append(f'<text x="{BX}" y="{y+2}" font-size="12" font-weight="700" fill="#5d6773">{lab}</text>'); y += 30; continue
        name, part, loc = PARTS[r]; ps = sorted(pins[r], key=lambda p: nets.index(p[1]))
        h = 40 + PH * len(ps)
        o.append(f'<rect x="{BX}" y="{y}" width="{BW}" height="{h}" rx="9" fill="#f4f6f8" stroke="#2c3e50" stroke-width="1.6"/>')
        o.append(f'<text x="{BX+12}" y="{y+20}" font-size="15" font-weight="700" fill="#14181d">{r} · {esc(name)}</text>')
        o.append(f'<text x="{BX+12}" y="{y+34}" font-size="11" fill="#5d6773">{esc(loc)}</text>')
        for i, (pin, n) in enumerate(ps):
            py = y + 50 + i * PH; c = netmap[n][1]
            o.append(f'<text x="{BX+BW-10}" y="{py+4}" font-size="12.5" text-anchor="end" fill="#14181d">{esc(pin)}</text>')
            o.append(f'<line x1="{BX+BW}" y1="{py}" x2="{railx[n]}" y2="{py}" stroke="{c}" stroke-width="2.4"/>')
            o.append(f'<circle cx="{BX+BW}" cy="{py}" r="3.5" fill="#2c3e50"/><circle cx="{railx[n]}" cy="{py}" r="5" fill="{c}"/>')
            ys.setdefault(n, []).append(py)
        y += h + 14
    H = y + 20
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            f'<text x="{BX}" y="34" font-size="24" font-weight="700" fill="#14181d">{esc(title)}</text>',
            f'<text x="{BX}" y="56" font-size="13" fill="#5d6773">Modules in physical order: earpieces → brick cable → visor. Each coloured rail is one net.</text>',
            f'<text x="{BX}" y="74" font-size="13" fill="#5d6773">A dot is a connection. A line that crosses a rail without a dot is not connected.</text>']
    rails = []
    for n in nets:
        if n not in ys: continue
        c = netmap[n][1]; x = railx[n]
        rails.append(f'<line x1="{x}" y1="{min(ys[n])}" x2="{x}" y2="{max(ys[n])}" stroke="{c}" stroke-width="4"/>')
        rails.append(f'<text transform="translate({x+4},{TOP-12}) rotate(-60)" font-size="13" font-weight="700" fill="{c}">{esc(n)}</text>')
    open(os.path.join(ROOT, "docs", "img", fname), "w").write("\n".join(head + rails + o + ["</svg>"]))

def main():
    os.makedirs(os.path.join(ROOT, "hardware"), exist_ok=True); os.makedirs(os.path.join(ROOT, "docs", "img"), exist_ok=True)
    with open(os.path.join(ROOT, "hardware", "netlist.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["net", "ref", "module", "pin", "part", "location", "wire", "net_description"])
        for net, col, wire, desc, ends in NETS:
            for ref, pin in ends:
                name, part, loc = PARTS[ref]; w.writerow([net, ref, name, pin, part, loc, wire, desc])
        for ref, pin, note in NC:
            name, part, loc = PARTS[ref]; w.writerow(["NC / prep", ref, name, pin, part, loc, "", note])
    with open(os.path.join(ROOT, "hardware", "wire_cut_list.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["signal", "wire", "cut_length_mm", "route"]); w.writerows(CUT)
    for fn, (title, nets, order) in DIAGRAMS.items(): svg(fn, title, nets, order)
    # pin-by-pin markdown
    by = {}
    for net, col, wire, desc, ends in NETS:
        for ref, pin in ends:
            others = [f"{r}.{p}" for r, p in ends if (r, p) != (ref, pin)]
            by.setdefault(ref, []).append((pin, net, ", ".join(others) or "test pad / no connection", wire))
    md = ["# Pin-by-pin connections", "",
          "Generated by `tools/netlist.py` from the same table as `hardware/netlist.csv` and the diagrams. Edit the script, not this file.", "",
          "![Power and privacy wiring](img/wiring_power.svg)", "", "![Signal wiring](img/wiring_signals.svg)", "",
          "## Board prep (do this before wiring)", "", "| Ref | Pin / item | Action |", "|---|---|---|"]
    md += [f"| {r} | {p} | {n} |" for r, p, n in NC]
    md += ["", "## Every module, every pin", ""]
    for ref in PARTS:
        name, part, loc = PARTS[ref]
        md += [f"### {ref} · {name}", f"*{part}* · {loc}", "", "| Pin | Net | Connects to | Wire |", "|---|---|---|---|"]
        md += [f"| {p} | `{n}` | {o} | {w} |" for p, n, o, w in by.get(ref, [])] + [""]
    md += ["## Harness cut list (wires that cross a hinge)", "", "| Signal | Wire | Cut (mm) | Route |", "|---|---|---:|---|"]
    md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in CUT]
    md += ["", "Only battery wires cross hinges: each temple tube carries its cell's BAT+ and GND (2 wires), and the left visor tube carries both pairs (4 wires). Everything else lives inside the visor.", ""]
    open(os.path.join(ROOT, "docs", "pinout.md"), "w").write("\n".join(md))
    print("wrote hardware/netlist.csv, hardware/wire_cut_list.csv, docs/pinout.md, docs/img/wiring_*.svg")

if __name__ == "__main__":
    main()
