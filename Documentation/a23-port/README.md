# Galaxy A23 4G (SM-A235F, khaje/SM6225) on the 5.15 A05s (m269) base

Status: **scaffolding only. This tree does not boot on A23 yet.**

## What is in this branch
- `build.config.msm.a23`, `build.config.msm.a23.sec`: build configs cloned from `m269`
  with `MSM_ARCH=a23`.
- `arch/arm64/configs/vendor/a23*`: defconfig/fragments cloned from `m269`
  (same SoC family, so the base GKI config is the starting point).
- `Documentation/a23-port/`: gap analysis against the 4.19 A23 tree
  (`blxyzY/android_kernel_samsung_sm6225`, branch `master`).
- `scripts/a23-port/analyze.py`: regenerates the analysis.

## Gap summary (from the analysis files)
- 388 CONFIG symbols enabled in `a23_eur_open_defconfig` do not exist in this tree.
- 44 of 75 compatibles used by the A23 DTS (`a23_eur_open_w00_r08`) have a driver only in 4.19.
- This tree has no board DTS at all (`arch/arm64/boot/dts/vendor` is empty); DTS/DLKM live outside.

## Port order (what blocks boot first)
1. Board DTS for A23 (from `samsung/a23/` in 4.19) in the external devicetree repo.
2. Display: panels `ft8720`, `ili7807s`, `nt36672c` + `ss_blic_s2dps01a01`.
3. Touch: `focaltech,fts`, `ilitek,ili9881x-spi`, `novatek,NVT-ts-spi`.
4. Power: `s2mu106` mfd/charger/fuelgauge/muic/pdic, `hl7132`, `sec-battery`, `sec-direct-charger`.
5. Audio: `tfa98xx`, `tas256x`, bolero/wcd937x/wsa881x (techpack/audio).
6. Camera, NFC (`sec-nfc`, `sn100u`), fingerprint (`et5xx`), sensors.
