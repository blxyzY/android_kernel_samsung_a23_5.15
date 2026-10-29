# SPDX-License-Identifier: GPL-2.0
# Galaxy A23 4G (SM-A235F, khaje/SM6225) board overlays.
#
# Each board *.dts here is an overlay (dtbo). It is also combined with the
# khaje base DTB from vendor/qcom into a full <base>-<board>.dtb.

dtstree		:= $(srctree)/$(src)
a23_boards	:= $(filter-out khaje-base.dtbo,$(patsubst $(dtstree)/%.dts,%.dtbo, $(wildcard $(dtstree)/*.dts)))

# khaje-<board>-dtbs = khaje-base.dtb board.dtbo
add-overlays	= $(foreach o,$1,$(eval khaje-$(basename $o)-dtbs = $2 $o) khaje-$(basename $o).dtb)

# khaje-base.dts includes the vendor/qcom khaje base; see the comment there.
sec_khaje_base_dtb	:= khaje-base.dtb

a23-dtb-$(CONFIG_ARCH_KHAJE)	+= $(call add-overlays, $(a23_boards), $(sec_khaje_base_dtb))
a23-overlays-dtb-$(CONFIG_ARCH_KHAJE) += $(a23_boards) $(sec_khaje_base_dtb)

dtb-$(CONFIG_ARCH_KHAJE)	+= $(a23-dtb-y)

always-y	:= $(dtb-y)

clean-files	:= *.dtb *.reverse.dts *.dtbo
