#!/usr/bin/env python3
"""Regenerate docs/BOM.md from bom.csv (run after editing bom.csv)."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, "bom.csv"))))
tot = lambda rs: sum(float(r["qty"]) * float(r["approx_unit_usd"]) for r in rs)
T = {t: tot([r for r in rows if r["tier"] == t]) for t in ["GLASSES", "BRICK"]}
out = ["# Bill of Materials (BOM)", "",
       "Generated from [`../bom.csv`](../bom.csv) by `tools/bom_md.py`. Prices are approximate USD, so verify before ordering.",
       "Status labels: **FINISHED / PROTOTYPE-READY / EXPERIMENTAL**.", ""]
for tier in ["GLASSES", "BRICK", "PHONE", "OPTION"]:
    rs = [r for r in rows if r["tier"] == tier]
    out += [f"## {tier}" + (f" ≈ ${tot(rs):,.2f}" if tot(rs) else ""), "",
            "| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |", "|---|---|---:|---:|---|---|---|"]
    for r in rs:
        item = f"[{r['item']}]({r['source_url']})" if r["source_url"] else r["item"]
        out.append(f"| {item} | {r['part_or_example']} | {r['qty']} | {float(r['approx_unit_usd']):.2f} | "
                   f"{r['status']} | {r['engineering_notes']} | {r['change_vs_brief']} |")
    out.append("")
out += [f"Totals: glasses ≈ ${T['GLASSES']:.0f} · pocket brick ≈ ${T['BRICK']:.0f} · together ≈ ${T['GLASSES']+T['BRICK']:.0f}.",
        "Most of the glasses cost is the micro-OLED dual kit ($660). The budget 0.49-inch option is listed under OPTION.", ""]
open(os.path.join(ROOT, "docs", "BOM.md"), "w").write("\n".join(out))
print("wrote docs/BOM.md")
