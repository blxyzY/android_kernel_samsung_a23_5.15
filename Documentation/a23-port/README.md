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
- The base DTS lives outside this tree (`arch/arm64/boot/dts/vendor` is a symlink to a sibling
  devicetree checkout); the A23 board DTS now lives in `arch/arm64/boot/dts/samsung/a23/`.

## Ported so far (compile-tested only, not run on hardware)
| compatible | driver | config |
|---|---|---|
| `samsung,s2mpb03pmic` | `drivers/regulator/s2mpb03.c` | `CONFIG_REGULATOR_S2MPB03=m` |
| `samsung,sec-thermistor` | `drivers/hwmon/sec_thermistor.c` | `CONFIG_SENSORS_SEC_THERMISTOR=m` (needs `HWMON`, now `=y` in `a23_sec_defconfig`) |

| `focaltech,fts` | `drivers/input/touchscreen/focaltech/ft8720/` | `CONFIG_TOUCHSCREEN_FTS_FT8720=m` (SPI; needs `INPUT_SEC_INPUT`) |
| (framework) | `drivers/input/sec_input/` (sec_cmd, tsp_log, secure_touch, dumpkey) | `CONFIG_INPUT_SEC_INPUT=m` and friends |

Optional hooks (`VBUS_NOTIFIER`, `SEC_ABC`, hall/fold, KUnit) are guarded in the sources and
left disabled until their providers are ported. A23 also ships `ilitek,ili9881x-spi` and
`novatek,NVT-ts-spi` panels; those drivers are still to be ported.

All of these build clean with clang 18 on `vendor/a23-gki_defconfig` + `a23_sec_defconfig`
(`ARCH=arm64 LLVM=1`). `m269` disables `HWMON`; A23 needs it for the thermistors.

## Devicetree (`arch/arm64/boot/dts/samsung/a23/`)
Board overlays ported from 4.19 `samsung/a23/` for the four hardware revisions, each built as an
overlay (`a23_eur_open_w00_rXX.dtbo`) and merged with the khaje base into
`khaje-a23_eur_open_w00_rXX.dtb`:

| board | `dtbo-hw_rev` range |
|---|---|
| r00 | 0 |
| r01 | 1 - 32 |
| r08 | 8 - 32 |
| r09 | 9 - 32 |

`msm-id`/`board-id`/`hw_rev` match the 4.19 sources. The only source change vs 4.19 is the ADC
macro `ADC_AMUX_THM2_PU2` -> `ADC5_AMUX_THM2_100K_PU` (same value, 0x4e); include paths in the
`khaje-sec.a23.XX.dtsi` files point at the external `vendor/samsung` tree.

**Not built yet:** `a23/a23/khaje-sec-a23-mm-{display,audio,camera}.dtsi`. They hold the panel,
audio and camera nodes from 4.19, which reference labels the khaje base DTB does not define
(`mdss_mdp`, `sde_dsi`, `bolero`, `wcd937x_codec`, `cam_cci0`, ...). Those come from the Qualcomm
display/audio/camera devicetree repos, which are not part of the A05s devicetree checkout. Until
they are added the phone has no display/audio/camera description. `split_dts` logic is in
`scripts/a23-port/`-style tooling kept outside the tree.

Build (needs the A05s devicetree repo as a sibling checkout named `a05s-devicetrees`):

    git clone https://github.com/samsung-sm6225-dev/android_kernel_samsung_a05s-devicetrees a05s-devicetrees
    make ARCH=arm64 LLVM=1 O=out vendor/a23-gki_defconfig
    make ARCH=arm64 LLVM=1 O=out -k -j$(nproc) dtbs

`khaje-base.dts` is a private copy of the base DTB so the A23 directory never builds the same
output file as `vendor/` (that raced under `-j`). `make dtbs` currently reports an unrelated
error for the A05s overlay `khaje-sec.a05s.overlay.00.dts` (an `#include` of
`m269-sm6225-overlay.dts` does not resolve in this layout); use `-k`.

Compile-tested only. Nothing here has been flashed or booted.

## Port order (what blocks boot first)
1. ~~Board DTS for A23~~ (core overlays done, see above); display/audio/camera DT still missing.
2. Display: panels `ft8720`, `ili7807s`, `nt36672c` + `ss_blic_s2dps01a01`.
3. Touch: `focaltech,fts`, `ilitek,ili9881x-spi`, `novatek,NVT-ts-spi`.
4. Power: `s2mu106` mfd/charger/fuelgauge/muic/pdic, `hl7132`, `sec-battery`, `sec-direct-charger`.
5. Audio: `tfa98xx`, `tas256x`, bolero/wcd937x/wsa881x (techpack/audio).
6. Camera, NFC (`sec-nfc`, `sn100u`), fingerprint (`et5xx`), sensors.
