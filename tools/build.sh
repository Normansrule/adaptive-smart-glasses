#!/usr/bin/env bash
# Rebuild every printable part (STL + 3MF), the Bambu plates, and the web-viewer
# assembly meshes from cad/adaptive_smart_glasses.scad + cad/config.scad.
#   usage:  ./tools/build.sh            (all parts)
#           ./tools/build.sh frame lid_left   (only those parts)
set -euo pipefail
cd "$(dirname "$0")/.."
SCAD=cad/adaptive_smart_glasses.scad
PARTS=(frame temple_left temple_right ear_grip_left ear_grip_right visor_shell visor_back tolerance_coupon)
[ $# -gt 0 ] && PARTS=("$@")
JOBS=${JOBS:-$(nproc 2>/dev/null || echo 2)}
command -v openscad >/dev/null || { echo "openscad not found: sudo apt install -y openscad"; exit 1; }
mkdir -p cad/stl cad/3mf cad/plates models build_tmp

export SCAD
one() {   # $1 = part
  local p=$1
  openscad -q -D "part=\"$p\"" -D '$fn=64' -o "build_tmp/$p.stl" "$SCAD"
  if [ "$p" != "tolerance_coupon" ]; then
    openscad -q -D 'part="asm"' -D "which=\"$p\"" -o "build_tmp/asm_$p.stl" "$SCAD"
  fi
  echo "  built $p"
}
export -f one
echo "Building ${#PARTS[@]} parts with $JOBS jobs (OpenSCAD can take a few minutes)..."
printf '%s\n' "${PARTS[@]}" | xargs -P "$JOBS" -I{} bash -c 'one {}'
python3 tools/postprocess.py build_tmp
python3 tools/bom_md.py
python3 tools/netlist.py
rm -rf build_tmp
echo "Done. Print files: cad/stl, cad/3mf, cad/plates   Viewer meshes: models/"
