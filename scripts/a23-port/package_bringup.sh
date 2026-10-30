#!/bin/bash
# Collect everything needed for a first-boot attempt into one tarball.
#
#   scripts/a23-port/package_bringup.sh <objdir> <outdir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$(cd "$HERE/../.." && pwd)
OBJ=$(realpath "${1:?usage: package_bringup.sh <objdir> <outdir>}")
OUT=$(realpath -m "${2:?usage: package_bringup.sh <objdir> <outdir>}")
DT=$OBJ/arch/arm64/boot/dts/samsung/a23/a23
PKG=$OUT/a23-bringup-r09
rm -rf "$PKG"; mkdir -p "$PKG"
for f in "$OBJ/arch/arm64/boot/Image" "$DT/khaje-base.dtb" "$DT/khaje-a23_eur_open_w00_r09.dtb"; do
  [ -s "$f" ] || { echo "missing $f" >&2; exit 1; }
  cp "$f" "$PKG/"
done
"$HERE/make_dtbo.sh" "$OBJ" "$PKG" >/dev/null
cp "$OBJ/System.map" "$PKG/System.map"
cp "$OBJ/.config" "$PKG/kernel.config"
cp "$HERE/repack_boot.py" "$SRC/Documentation/a23-port/BRINGUP.md" "$PKG/"
( cd "$PKG" && sha256sum * > SHA256SUMS )
tar -C "$OUT" -czf "$OUT/a23-bringup-r09.tar.gz" a23-bringup-r09
ls -la "$PKG" "$OUT/a23-bringup-r09.tar.gz"
