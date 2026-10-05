#!/usr/bin/env bash
# Bundle everything a maker needs into dist/<name>-fab-<version>.zip (attach to a GitHub release).
#   ./tools/package_release.sh v0.1.0
set -euo pipefail
cd "$(dirname "$0")/.."
VER=${1:-v0.1.0}; NAME=adaptive-smart-glasses-fab-$VER; OUT=dist/$NAME
rm -rf "$OUT" && mkdir -p "$OUT"
cp -r cad/stl cad/3mf cad/plates "$OUT/"
cp cad/print_manifest.csv cad/part_stats.json cad/config.scad cad/adaptive_smart_glasses.scad "$OUT/"
cp bom.csv hardware/netlist.csv hardware/wire_cut_list.csv "$OUT/"
mkdir -p "$OUT/docs" && cp docs/*.md "$OUT/docs/" && cp -r docs/img "$OUT/docs/"
mkdir -p "$OUT/firmware" && cp firmware/glasses_mcu/prebuilt/* "$OUT/firmware/" && cp -r brick "$OUT/"
cp -r LICENSES "$OUT/" && cp README.md "$OUT/"
(cd dist && rm -f "$NAME.zip" && zip -qr "$NAME.zip" "$NAME")
rm -rf "$OUT"; echo "dist/$NAME.zip"
