#!/bin/bash
# Build an A23 bring-up kernel: Image + DTBs (+ modules for the few that stay =m).
#
#   scripts/a23-port/build_bringup.sh <objdir> [extra make args]
#
# Optional: LOCAL_FRAGMENT=/path/to.config is merged last (e.g. to turn off
# DEBUG_INFO_BTF on a host without libelf/pahole).
set -euo pipefail
SRC=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$(realpath -m "${1:?usage: build_bringup.sh <objdir> [make args]}"); shift || true
export ARCH=arm64 LLVM=1 LLVM_IAS=1
CFG=$SRC/arch/arm64/configs/vendor
mkdir -p "$OUT"
make -C "$SRC" O="$OUT" vendor/a23-gki_defconfig
# a23_sec_defconfig = Samsung additions; a23_bringup.config is generated below.
"$SRC/scripts/kconfig/merge_config.sh" -m -O "$OUT" "$OUT/.config" "$CFG/a23_sec_defconfig" ${LOCAL_FRAGMENT:+"$LOCAL_FRAGMENT"} >/dev/null
make -C "$SRC" O="$OUT" olddefconfig
python3 -I "$SRC/scripts/a23-port/make_bringup_config.py" "$SRC" "$OUT" "$CFG/a23_bringup.config"
[ -n "${LOCAL_FRAGMENT:-}" ] && { "$SRC/scripts/kconfig/merge_config.sh" -m -O "$OUT" "$OUT/.config" "$LOCAL_FRAGMENT" >/dev/null; make -C "$SRC" O="$OUT" olddefconfig; }
make -C "$SRC" O="$OUT" -j"$(nproc)" "$@" Image modules
# The A05s devicetree checkout has an unrelated overlay that fails to resolve an
# #include (khaje-sec.a05s.overlay.00); -k keeps going so the A23 DTBs still build.
make -C "$SRC" O="$OUT" -k -j"$(nproc)" "$@" dtbs || true
DTB=$OUT/arch/arm64/boot/dts/samsung/a23/a23/khaje-a23_eur_open_w00_r09.dtb
[ -f "$DTB" ] || { echo "ERROR: A23 r09 DTB was not produced" >&2; exit 1; }
ls -la "$OUT/arch/arm64/boot/Image" "$OUT"/arch/arm64/boot/dts/samsung/a23/a23/*.dtb*
