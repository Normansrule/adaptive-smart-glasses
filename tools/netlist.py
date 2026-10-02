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
 "BT1": ("Battery",        "Protected 1S LiPo 8x20x46, JST-PH",           "Left pod, front bay"),
 "TH1": ("NTC 10k",        "10k NTC B3435 (103AT)",                        "Taped to BT1"),
 "U8":  ("Charger + 5V",   "Adafruit 6106 bq25185 + TPS61023",              "Left pod, rear bay"),
 "SW1": ("Main switch",    "E-Switch 500SSP1S1M6QEA (SPDT used as SPST)",  "Left frame endpiece"),
 "U4":  ("BME280",         "GY-BME280 3.3 V, 4-pin",                       "Left brow pocket"),
 "U2":  ("ToF 8x8",        "SparkFun SEN-19013 VL53L5CX Mini",             "Bridge pocket"),
 "SW2": ("PTT button",     "6x6 tact switch, Omron B3F-1000",              "Right frame endpiece (top)"),
 "R1":  ("1k",             "1k 1/8 W",                                     "Right frame endpiece"),
 "D1":  ("Privacy LED",    "3 mm red LED",                                 "Right frame endpiece (front)"),
 "U3":  ("IMU",            "Adafruit 4438 LSM6DSOX",                       "Right pod, outer layer"),
 "U1":  ("XIAO ESP32-S3",  "Seeed XIAO ESP32-S3 (non-Sense)",              "Right pod, outer layer, rear"),
 "D2":  ("1N5817",         "1N5817 Schottky",                              "Right pod"),
 "D3":  ("1N4148",         "1N4148",                                       "Right pod"),
 "R2":  ("100k top",       "100k 1/8 W",                                   "Right pod"),
 "R3":  ("100k bottom",    "100k 1/8 W",                                   "Right pod"),
 "R4":  ("100k pulldown",  "100k 1/8 W",                                   "Right pod"),
 "U5":  ("Mic",            "Adafruit 3421 SPH0645LM4H",                    "Right pod, outer layer, front"),
 "U6":  ("Amp BONE",       "Adafruit 3006 MAX98357A",                      "Right pod, inner layer"),
 "U7":  ("Amp OUTWARD",    "Adafruit 3006 MAX98357A",                      "Right pod, inner layer"),
 "LS1": ("Speaker",        "15 mm 8 ohm micro speaker",                    "Right pod, inner wall grille"),
 "LS2": ("Bone transducer","Adafruit 1674 8 ohm 1 W",                      "Right ear grip cradle"),
}
# net: (colour, wire, description, [(ref, pin label), ...])
NETS = [
 ("BATT",      "#c0392b", "JST-PH plug", "Battery into charger",            [("BT1","JST-PH"),("U8","BATT JST-PH")]),
 ("THERM",     "#8e44ad", "NTC leads",   "Charger stops when the cell is too hot or cold", [("TH1","lead A"),("U8","R16 pad (THERM side)")]),
 ("5V_RAW",    "#e74c3c", "28 AWG red",  "Boost output to main switch",    [("U8","5V +"),("SW1","COM")]),
 ("5V_SW",     "#ff7f50", "28 AWG red",  "Switched system 5 V",            [("SW1","throw A"),("D2","anode"),("U6","Vin"),("U7","Vin")]),
 ("5V_XIAO",   "#ff9f80", "local",       "XIAO supply after diode",        [("D2","cathode (band)"),("U1","5V")]),
 ("GND",       "#2c3e50", "28 AWG black","Common ground",                  [("U8","5V -"),("TH1","lead B -> R16 GND pad"),("U4","GND"),("U2","GND"),
                                                                              ("D1","cathode (short leg)"),("U3","GND"),("U1","GND"),("R3","2"),("R4","2"),
                                                                              ("U5","GND"),("U5","SEL"),("U6","GND"),("U7","GND")]),
 ("VBAT_SENSE","#27ae60", "30 AWG green","Battery voltage to divider",     [("U8","VBAT (header pin 6)"),("R2","1")]),
 ("VBAT_DIV",  "#2ecc71", "local",       "Half battery voltage to ADC",    [("R2","2"),("R3","1"),("U1","D0 / A0")]),
 ("3V3",       "#f39c12", "30 AWG (Qwiic red)", "Sensors and PTT feed",    [("U1","3V3"),("U3","3V3 (Qwiic)"),("U2","3V3 (Qwiic)"),("U4","VIN"),("SW2","pin 1")]),
 ("MIC_3V3",   "#e84393", "30 AWG white","Mic power, ONLY while PTT held", [("SW2","pin 3"),("R1","1"),("U5","3V"),("D3","anode")]),
 ("LED_A",     "#fd79a8", "local",       "LED current limit",              [("R1","2"),("D1","anode (long leg)")]),
 ("PTT_SENSE", "#a29bfe", "local",       "PTT state to MCU, one-way",      [("D3","cathode (band)"),("R4","1"),("U1","D1")]),
 ("SDA",       "#2980b9", "30 AWG (Qwiic blue)",   "I2C data",            [("U1","D4"),("U3","SDA (Qwiic)"),("U2","SDA (Qwiic)"),("U4","SDA")]),
 ("SCL",       "#f1c40f", "30 AWG (Qwiic yellow)", "I2C clock",           [("U1","D5"),("U3","SCL (Qwiic)"),("U2","SCL (Qwiic)"),("U4","SCL")]),
 ("I2S_BCLK",  "#6c5ce7", "local",       "I2S bit clock",                  [("U1","D8"),("U5","BCLK"),("U6","BCLK"),("U7","BCLK")]),
 ("I2S_WS",    "#00b894", "local",       "I2S word select",                [("U1","D9"),("U5","LRCL"),("U6","LRC"),("U7","LRC")]),
 ("I2S_TX",    "#0984e3", "local",       "Audio to amps",                  [("U1","D10"),("U6","DIN"),("U7","DIN")]),
 ("I2S_RX",    "#00cec9", "local",       "Audio from mic",                 [("U5","DOUT"),("U1","D7")]),
 ("SD_BONE",   "#d35400", "local",       "Bone amp on/off",                [("U1","D2"),("U6","SD")]),
 ("SD_OUT",    "#e17055", "local",       "Outward amp on/off",             [("U1","D3"),("U7","SD")]),
 ("BONE+",     "#636e72", "30 AWG pair", "To ear-grip transducer",         [("U6","OUT +"),("LS2","+")]),
 ("BONE-",     "#2d3436", "30 AWG pair", "",                               [("U6","OUT -"),("LS2","-")]),
 ("SPK+",      "#b2bec3", "30 AWG pair", "To pod speaker",                 [("U7","OUT +"),("LS1","+")]),
 ("SPK-",      "#7f8c8d", "30 AWG pair", "",                               [("U7","OUT -"),("LS1","-")]),
 ("MEDIA_EN",  "#e67e22", "test pad",    "Future media gate, LOW by default", [("U1","D6")]),
]
NC = [("U6","GAIN","leave open (9 dB)"),("U7","GAIN","leave open (9 dB)"),("U8","EN","leave open (boost on)"),
      ("U8","ISET jumper","CUT -> 500 mA charge"),("U8","R16","REMOVE, NTC goes on its pads"),("U2","LPn/INT","not used")]

# harness wires that cross hinges (cut length includes ~20% slack)
CUT = [
 ("5V_RAW",    "28 AWG red",    170, "U8 5V+ -> L pod front wall -> L hinge tube -> L endpiece groove -> SW1 COM"),
 ("5V_SW",     "28 AWG red",    260, "SW1 -> brow groove -> R hinge tube -> R pod (D2, U6, U7)"),
 ("GND",       "28 AWG black",  360, "U8 5V- -> L hinge -> brow (taps: U4, U2 via Qwiic, D1) -> R hinge -> R pod"),
 ("VBAT_SENSE","30 AWG green",  360, "U8 VBAT -> L hinge -> brow -> R hinge -> R2"),
 ("3V3/SDA/SCL","Qwiic 100 mm cable, cut", 200, "U3 Qwiic -> R pod front -> R hinge tube -> brow -> U2 Qwiic A (splice; tap 3V3 to SW2 at R endpiece)"),
 ("3V3/SDA/SCL","Qwiic 50 mm pigtail",      70, "U2 Qwiic B -> brow -> U4 (solder 4 wires)"),
 ("MIC_3V3",   "30 AWG white",  130, "SW2 pin 3 (R endpiece) -> R hinge -> R pod (U5 3V, D3)"),
 ("BONE+/-",   "30 AWG twisted pair", 90, "U6 OUT -> R pod rear wall hole -> earpiece groove -> LS2 in grip"),
 ("SPK+/-",    "30 AWG twisted pair", 50, "U7 OUT -> LS1 (inside pod)"),
]

DIAGRAMS = {
 "wiring_power.svg":   ("Power + microphone privacy",
                        ["BATT","THERM","5V_RAW","5V_SW","5V_XIAO","GND","VBAT_SENSE","VBAT_DIV","3V3","MIC_3V3","LED_A","PTT_SENSE"],
                        ["BT1","TH1","U8","|L","SW1","SW2","R1","D1","|R","U1","D2","R2","R3","D3","R4","U5","U6","U7"]),
 "wiring_signals.svg": ("Signals: I2C sensors, I2S audio",
                        ["3V3","GND","SDA","SCL","I2S_BCLK","I2S_WS","I2S_TX","I2S_RX","SD_BONE","SD_OUT","BONE+","BONE-","SPK+","SPK-","MEDIA_EN"],
                        ["U4","U2","|R","U3","U1","U5","U6","U7","LS1","|G","LS2"]),
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
            lab = {"L": "LEFT HINGE  (wires pass through the brass tube)", "R": "RIGHT HINGE  (wires pass through the brass tube)", "G": "EAR GRIP"}[r[1]]
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
            f'<text x="{BX}" y="56" font-size="13" fill="#5d6773">Modules in physical order: left temple → frame → right temple. Each coloured rail is one net.</text>',
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
    md += ["", "Right hinge carries 7 conductors (5V_SW, GND, VBAT_SENSE, 3V3, SDA, SCL, MIC_3V3). Left hinge carries 3 (5V_RAW, GND, VBAT_SENSE).", ""]
    open(os.path.join(ROOT, "docs", "pinout.md"), "w").write("\n".join(md))
    print("wrote hardware/netlist.csv, hardware/wire_cut_list.csv, docs/pinout.md, docs/img/wiring_*.svg")

if __name__ == "__main__":
    main()
