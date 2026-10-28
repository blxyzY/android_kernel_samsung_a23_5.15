# A23 DTS compatible -> driver map

Source DTS: `samsung/a23/a23/a23_eur_open_w00_r08.dts` (4.19) with all includes resolved (29 dts/dtsi files).

- 75 compatible strings total
- 8 already have a matching driver in the 5.15 tree
- 44 have a driver only in 4.19 (must be ported)
- 23 not found as a literal in any .c file of either tree (generic/binding-only or matched another way)

## Driver exists only in 4.19 (port needed)

| compatible | 4.19 driver | first used in |
|---|---|---|
| `etspi,et5xx` | `drivers/fingerprint/et5xx-spi.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `focaltech,fts` | `drivers/input/touchscreen/focaltech/ft8720/focaltech_core.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `halo,hl7132` | `drivers/battery/charger/hl7132_charger/hl7132_charger.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `ilitek,ili9881x-spi` | `drivers/input/touchscreen/ilitek/ili9881x/ili9881x_init.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `novatek,NVT-ts-spi` | `drivers/input/touchscreen/novatek/nt36523_spi/nt36xxx.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `nxp,pca953x` | `drivers/gpio/gpio-pca953x.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `qcom,actuator` | `drivers/media/platform/msm/camera_v2/sensor/actuator/msm_actuator.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,audio-ref-clk` | `techpack/audio/asoc/codecs/audio-ext-clk-up.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,bolero-clk-rsc-mngr` | `techpack/audio/asoc/codecs/bolero/bolero-clk-rsc.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,cam-res-mgr` | `techpack/camera/drivers/cam_sensor_module/cam_res_mgr/cam_res_mgr.c` | `vendor/qcom/camera/khaje-camera-sensor-idp.dtsi` |
| `qcom,cam-sensor` | `techpack/camera/drivers/cam_sensor_module/cam_sensor/cam_sensor_dev.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,camera-flash` | `drivers/media/platform/msm/camera_v2/sensor/flash/msm_flash.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,dsi-display` | `techpack/display/msm/dsi/dsi_display.c` | `vendor/qcom/khaje-sde-display.dtsi` |
| `qcom,eeprom` | `drivers/media/platform/msm/camera_v2/sensor/eeprom/msm_eeprom.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,msm-cdc-pinctrl` | `techpack/audio/asoc/codecs/msm-cdc-pinctrl.c` | `samsung/a23/khaje-sec-a23-audio-common.dtsi` |
| `qcom,msm-notifier` | `techpack/display/msm/msm_notifier.c` | `vendor/qcom/khaje-sde-display.dtsi` |
| `qcom,nq-nci` | `drivers/nfc/nq-nci.c` | `vendor/qcom/khaje-idp.dtsi` |
| `qcom,ois` | `drivers/media/platform/msm/camera_v2/sensor/ois/msm_ois.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,rx-macro` | `techpack/audio/asoc/codecs/bolero/rx-macro.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,s2mu106-fled` | `drivers/leds/leds-s2mu106.c` | `samsung/a23/a23/khaje-sec-a23-camera-sensor-common.dtsi` |
| `qcom,swr-mstr` | `techpack/audio/soc/swr-mstr-ctrl.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,tx-macro` | `techpack/audio/asoc/codecs/bolero/tx-macro.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,va-macro` | `techpack/audio/asoc/codecs/bolero/va-macro.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,wb-display` | `techpack/display/msm/sde/sde_wb.c` | `vendor/qcom/khaje-sde-display.dtsi` |
| `qcom,wcd937x-codec` | `techpack/audio/asoc/codecs/wcd937x/wcd937x.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,wcd937x-slave` | `techpack/audio/asoc/codecs/wcd937x/wcd937x_slave.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `qcom,wsa881x-i2c-codec` | `techpack/audio/asoc/codecs/wsa881x-analog.c` | `vendor/qcom/bengal-audio-overlay.dtsi` |
| `s2dps01a01,display_backlight` | `techpack/display/msm/samsung/BLIC/ss_blic_s2dps01a01_i2c.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,abc_hub` | `drivers/sti/abc/abc_hub_core.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,audio-sysfs` | `sound/soc/samsung/sec_audio_sysfs.c` | `samsung/a23/khaje-sec-a23-audio-common.dtsi` |
| `samsung,q6audio-adaptation` | `techpack/audio/asoc/sec_audio_adaptation.c` | `samsung/a23/khaje-sec-a23-audio-common.dtsi` |
| `samsung,s2mpb03pmic` | `drivers/regulator/s2mpb03/s2mpb03.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,s2mu106-charger` | `drivers/battery/charger/s2mu106_charger/s2mu106_charger.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,s2mu106-fuelgauge` | `drivers/battery/fuelgauge/s2mu106_fuelgauge/s2mu106_fuelgauge.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,s2mu106mfd` | `drivers/mfd/slsi/s2mu106/s2mu106_core.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,sec-battery` | `drivers/battery/common/sec_battery.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,sec-direct-charger` | `drivers/battery/common/sec_direct_charger.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,sec-smem` | `drivers/samsung/misc/sec_smem.c` | `samsung/khaje-sec-common.dtsi` |
| `samsung,sec-thermistor` | `drivers/hwmon/sec_thermistor/sec_thermistor.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,sec_abc` | `drivers/sti/abc/abc_common.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,ss_touch` | `drivers/input/sec_input/sec_secure_touch.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `sec,s2mu106-haptic` | `drivers/mfd/slsi/s2mu106/s2mu106_core.c` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `synaptics,tcm-i2c` | `drivers/input/touchscreen/synaptics_tcm/synaptics_tcm_i2c.c` | `vendor/qcom/khaje-idp.dtsi` |
| `tfa,tfa98xx` | `techpack/audio/asoc/codecs/tfa9878/tfa98xx.c` | `samsung/a23/a23/khaje-sec.a23.08.dtsi` |

## Not found in any driver source

| compatible | first used in |
|---|---|
| `android,vbmeta` | `samsung/khaje-sec-common.dtsi` |
| `ese_p3` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `gpio-keys` | `vendor/qcom/khaje-idp.dtsi` |
| `i2c-gpio` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `input_booster` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `isg6320` | `samsung/a23/khaje-sec-a23-grip-common.dtsi` |
| `modem-removed-dma-pool` | `samsung/khaje-sec-common.dtsi` |
| `novatek,NVT-ts` | `vendor/qcom/khaje-idp.dtsi` |
| `novatek-mp-criteria-7235` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `qcom,idp` | `samsung/a23/a23/khaje-sec.a23.08.dtsi` |
| `qcom,khaje` | `samsung/a23/a23/khaje-sec.a23.08.dtsi` |
| `qcom,khaje-idp` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `qcom,khaje:qcom,idp` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `ramoops` | `samsung/khaje-sec-common.dtsi` |
| `regulator-fixed` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `removed-dma-pool` | `samsung/khaje-sec-common.dtsi` |
| `resource` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `s2mu106-usbpd` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `samsung,sec-ap-pmic` | `samsung/a23/khaje-sec-a23-pm-common.dtsi` |
| `sec-nfc` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `simple-bus` | `samsung/a23/a23/a23_eur_open_w00_r08.dts` |
| `ss_plog` | `samsung/khaje-sec-common.dtsi` |
| `ti, tas256x` | `samsung/a23/khaje-sec-a23-audio-common.dtsi` |

## Already present in 5.15

| compatible | 5.15 driver |
|---|---|
| `awinic,aw2016_led` | `drivers/leds/leds-aw2016.c` |
| `qcom,memshare` | `drivers/soc/qcom/memshare/msm_memshare.c` |
| `qcom,memshare-peripheral` | `drivers/soc/qcom/memshare/msm_memshare.c` |
| `qcom,msm-geni-serial-hs` | `drivers/tty/serial/msm_geni_serial.c` |
| `qcom,msm-imem-upload_cause` | `drivers/samsung/debug/qcom/upload_cause/sec_qc_upload_cause.c` |
| `qcom,ufs-phy-qmp-v4` | `drivers/phy/qualcomm/phy-qcom-ufs-qmp-v4.c` |
| `samsung,argos` | `drivers/samsung/bsp/argos/sec_argos.c` |
| `samsung,usb-notifier` | `drivers/usb/notify/usb_notifier.c` |
