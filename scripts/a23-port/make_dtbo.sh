#!/bin/bash
# Build dtbo.img from the A23 board overlays, the same way the 4.19 build.sh does
# (mkdtimg create --page_size=4096 <overlays>), using AOSP's mkdtboimg.py.
#
#   scripts/a23-port/make_dtbo.sh <objdir> <outdir>
#
# Writes <outdir>/dtbo.img      all four revisions (r00 r01 r08 r09)
#        <outdir>/dtbo_r09.img  only rev 9 (ro.boot.revision=9): use this first.
set -euo pipefail
OBJ=$(realpath "${1:?usage: make_dtbo.sh <objdir> <outdir>}")
OUT=$(realpath -m "${2:?usage: make_dtbo.sh <objdir> <outdir>}")
TOOLS=${LIBUFDT_DIR:-$HOME/.cache/a23-libufdt}
MK=$TOOLS/utils/src/mkdtboimg.py
if [ ! -f "$MK" ]; then
  mkdir -p "$(dirname "$TOOLS")"; rm -rf "$TOOLS"
  git clone --depth 1 https://github.com/LineageOS/android_system_libufdt "$TOOLS"
fi
DT=$OBJ/arch/arm64/boot/dts/samsung/a23/a23
for r in r00 r01 r08 r09; do
  [ -s "$DT/a23_eur_open_w00_$r.dtbo" ] || { echo "missing $DT/a23_eur_open_w00_$r.dtbo (run the build first)" >&2; exit 1; }
done
mkdir -p "$OUT"
python3 -I "$MK" create "$OUT/dtbo.img" --page_size=4096 \
  "$DT"/a23_eur_open_w00_r00.dtbo "$DT"/a23_eur_open_w00_r01.dtbo \
  "$DT"/a23_eur_open_w00_r08.dtbo "$DT"/a23_eur_open_w00_r09.dtbo
python3 -I "$MK" create "$OUT/dtbo_r09.img" --page_size=4096 "$DT"/a23_eur_open_w00_r09.dtbo
ls -la "$OUT/dtbo.img" "$OUT/dtbo_r09.img"
