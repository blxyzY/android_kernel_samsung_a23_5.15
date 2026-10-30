core-y		+= drivers/samsung/debug/boot_stat/
core-y		+= drivers/samsung/debug/log_buf/
core-y		+= drivers/samsung/debug/arm64/ap_context/
#core-y		+= drivers/base/regmap/
#core-y		+= drivers/spmi/
# A23 bring-up: drivers/interconnect/qcom is already built in through drivers/ (see
# arch/arm64/configs/vendor/a23_bringup.config); listing it here too links every
# object twice ("duplicate symbol: qcom_icc_rpm_set").
#core-y		+= drivers/interconnect/qcom/
