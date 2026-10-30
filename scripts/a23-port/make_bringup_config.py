#!/usr/bin/env python3
"""Generate arch/arm64/configs/vendor/a23_bringup.config.

The m269/A05s base is GKI-style: most SoC drivers are modules that the vendor
ramdisk loads at boot. For A23 bring-up there is no 5.15 module set, so every
tristate that is =m and is defined under a boot-critical driver directory is
promoted to =y. Dependencies can clamp y back to m, so iterate to a fixpoint.

usage: make_bringup_config.py <srctree> <objdir> <out.config>
(objdir must already hold a merged .config, and `make olddefconfig` must work)
"""
import os, re, subprocess, sys

CRIT = (
    "drivers/clk/", "drivers/pinctrl/", "drivers/regulator/", "drivers/interconnect/",
    "drivers/iommu/", "drivers/soc/qcom/", "drivers/firmware/", "drivers/scsi/ufs/",
    "drivers/mmc/host/", "drivers/phy/", "drivers/spmi/", "drivers/mfd/",
    "drivers/tty/serial/", "drivers/i2c/busses/", "drivers/spi/", "drivers/gpio/",
    "drivers/irqchip/", "drivers/mailbox/", "drivers/hwspinlock/", "drivers/rpmsg/",
    "drivers/cpufreq/", "drivers/cpuidle/", "drivers/watchdog/", "drivers/power/reset/",
    "drivers/usb/dwc3/", "drivers/extcon/", "drivers/dma/", "drivers/bus/",
    "drivers/nvmem/", "drivers/reset/", "drivers/samsung/bsp/", "drivers/iio/adc/",
    "drivers/input/misc/", "drivers/rtc/", "drivers/hwmon/", "drivers/input/sec_input/",
    "drivers/char/hw_random/", "drivers/thermal/", "drivers/devfreq/", "drivers/usb/phy/",
)

# Samsung debug/RDX modules: not needed to boot, and several need Qualcomm symbols
# (e.g. qcom_lpm_set_sleep_disabled) that this tree does not export.
DISABLE = ("drivers/samsung/debug/",)

# Not under a critical directory, or not a tristate we can detect, but wanted at bring-up.
EXTRA = (
    "CONFIG_TOUCHSCREEN_FTS_FT8720=y",
    # Light build: Full LTO + CFI + DEBUG_INFO do not fit on a small builder and
    # only get in the way of a first boot. Re-enable once the port is stable.
    "CONFIG_LTO_NONE=y",
    "# CONFIG_LTO_CLANG_FULL is not set",
    "# CONFIG_LTO_CLANG_THIN is not set",
    "# CONFIG_CFI_CLANG is not set",
    "# CONFIG_DEBUG_INFO is not set",
    "# CONFIG_DEBUG_INFO_DWARF4 is not set",
    "# CONFIG_DEBUG_INFO_DWARF5 is not set",
    "# CONFIG_GDB_SCRIPTS is not set",
    # Built-in code (soc/qcom, cpufreq, ...) calls symbols that these export; a
    # module cannot satisfy a built-in reference, so build them in.
    "CONFIG_SCHED_WALT=y",
    "CONFIG_IPC_LOGGING=y",
    "CONFIG_REGMAP_QTI_DEBUGFS=y",
    "CONFIG_UCSI_QTI_GLINK=y",
    # memory_dump_v2/dcc_v2 call sec_debug_level() when this is =m, which a
    # built-in object cannot link against. Samsung QC debug is not needed to
    # boot; with it off those files use their stubs.
    "# CONFIG_SEC_QC_DEBUG is not set",
    # Same for sec_debug_is_enabled() called from the now built-in ipc_logging.
    # sec_debug.h provides inline stubs when SEC_DEBUG is off.
    "# CONFIG_SEC_DEBUG is not set",
    # Needs cpio on the build host; only exposes kernel headers via /proc.
    "# CONFIG_IKHEADERS is not set",
    # Sanitizers/debug options that can panic on first run of ported vendor code
    # (UBSAN_TRAP turns any array-bounds hit into a BRK panic) or need MTE/EL2.
    "# CONFIG_UBSAN is not set",
    "# CONFIG_UBSAN_TRAP is not set",
    "# CONFIG_UBSAN_BOUNDS is not set",
    "# CONFIG_KASAN is not set",
    "# CONFIG_KASAN_HW_TAGS is not set",
    "# CONFIG_KFENCE is not set",
    "# CONFIG_PAGE_OWNER is not set",
    "CONFIG_LOCALVERSION=\"-a23-bringup\"",
)


def index_kconfig(src):
    idx = {}
    pat = re.compile(r"^\s*(?:menu)?config\s+(\w+)\s*$")
    for root, dirs, files in os.walk(src):
        if "/.git" in root or root.startswith(os.path.join(src, "arch")) and "arm64" not in root:
            continue
        for f in files:
            if f.startswith("Kconfig"):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, src)
                try:
                    for line in open(p, errors="replace"):
                        m = pat.match(line)
                        if m:
                            idx.setdefault(m.group(1), rel)
                except OSError:
                    pass
    return idx


def main():
    src, obj, out = sys.argv[1:4]
    env = dict(os.environ, ARCH="arm64", LLVM="1", LLVM_IAS="1")
    idx = index_kconfig(src)
    chosen = set()
    disabled = set()
    for it in range(8):
        cfg = open(os.path.join(obj, ".config")).read()
        mods = re.findall(r"^CONFIG_(\w+)=m$", cfg, re.M)
        want = {s for s in mods if idx.get(s, "").startswith(CRIT)}
        on = re.findall(r"^CONFIG_(\w+)=[ym]$", cfg, re.M)
        off = {s for s in on if idx.get(s, "").startswith(DISABLE)}
        new = (want - chosen) | (off - disabled)
        print(f"iter {it}: {len(mods)} modules, {len(want)} critical still =m, {len(off)} debug on, {len(new)} new")
        if not new:
            break
        chosen |= want
        disabled |= off
        with open(out, "w") as fh:
            fh.write("# Generated by scripts/a23-port/make_bringup_config.py\n"
                     "# Boot-critical drivers built in for A23 bring-up (no 5.15 module set yet).\n")
            for s in sorted(chosen):
                fh.write(f"CONFIG_{s}=y\n")
            for s in sorted(disabled):
                fh.write(f"# CONFIG_{s} is not set\n")
            fh.write("\n".join(EXTRA) + "\n")
        subprocess.run([os.path.join(src, "scripts/kconfig/merge_config.sh"), "-m", "-O", obj,
                        os.path.join(obj, ".config"), out], env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=src)
        subprocess.run(["make", f"O={obj}", "olddefconfig"], env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=src)
    cfg = open(os.path.join(obj, ".config")).read()
    left = sorted(s for s in re.findall(r"^CONFIG_(\w+)=m$", cfg, re.M) if idx.get(s, "").startswith(CRIT))
    print("promoted:", len(chosen), " still-module critical:", left)


if __name__ == "__main__":
    main()
