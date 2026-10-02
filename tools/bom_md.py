#!/usr/bin/env python3
"""Regenerate docs/BOM.md from bom.csv (run after editing bom.csv)."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, "bom.csv"))))
tot = lambda rs: sum(float(r["qty"]) * float(r["approx_unit_usd"]) for r in rs)
T = {t: tot([r for r in rows if r["tier"] == t]) for t in ["CORE", "HUD", "MEDIA"]}
out = ["# Bill of Materials (BOM)", "",
       "Generated from [`../bom.csv`](../bom.csv) by `tools/bom_md.py`. Prices are approximate USD, so verify before ordering.",
       "Status labels: **FINISHED / PROTOTYPE-READY / EXPERIMENTAL**.", ""]
for tier in ["CORE", "HUD", "MEDIA", "OPTION"]:
    rs = [r for r in rows if r["tier"] == tier]
    out += [f"## {tier}" + (f" ≈ ${tot(rs):,.2f}" if tot(rs) else ""), "",
            "| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |", "|---|---|---:|---:|---|---|---|"]
    for r in rs:
        item = f"[{r['item']}]({r['source_url']})" if r["source_url"] else r["item"]
        out.append(f"| {item} | {r['part_or_example']} | {r['qty']} | {float(r['approx_unit_usd']):.2f} | "
                   f"{r['status']} | {r['engineering_notes']} | {r['change_vs_brief']} |")
    out.append("")
out += [f"Totals: CORE ≈ ${T['CORE']:.0f} · CORE + HUD ≈ ${T['CORE']+T['HUD']:.0f} · + MEDIA ≈ ${T['CORE']+T['HUD']+T['MEDIA']:.0f}.",
        "The HUD is priced from real optical parts. A budget 30/70 glass combiner instead of the Edmund plate saves about $130.", ""]
open(os.path.join(ROOT, "docs", "BOM.md"), "w").write("\n".join(out))
print("wrote docs/BOM.md")
