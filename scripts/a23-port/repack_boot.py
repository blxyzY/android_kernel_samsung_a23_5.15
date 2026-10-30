#!/usr/bin/env python3
"""Repack your *stock* A23 boot.img with the 5.15 bring-up kernel and DTB.

Nothing here is written back to the phone: it only produces new image files next
to <outdir>. Your stock images are never modified.

    repack_boot.py --boot stock_boot.img --kernel Image --dtb khaje-a23_r09.dtb \
                   [--vendor-boot stock_vendor_boot.img] [--outdir out]

How the pieces are replaced depends on the boot image header version:

  v0/v1  the DTB is appended to the kernel image            -> kernel+dtb concatenated
  v2     boot.img carries kernel, ramdisk and a DTB section -> kernel and dtb replaced
  v3/v4  boot.img carries kernel + generic ramdisk; the DTB
         lives in vendor_boot.img                           -> --vendor-boot is required,
                                                              kernel replaced in boot.img,
                                                              dtb replaced in vendor_boot.img

The stock ramdisk, cmdline, offsets, os_version and patch level are kept as they are.
The kernel is compressed the same way as the stock one (gzip or raw); lz4 is refused
rather than guessed.

mkbootimg/unpack_bootimg are the AOSP scripts. If --mkbootimg-dir is not given they
are cloned (once) from a GitHub mirror into ~/.cache/a23-mkbootimg.
"""
import argparse
import gzip
import os
import shutil
import subprocess
import sys
import tempfile

MIRROR = "https://github.com/LineageOS/android_system_tools_mkbootimg"


def die(msg):
    sys.exit("error: " + msg)


def ensure_tools(given):
    d = given or os.path.join(os.path.expanduser("~"), ".cache", "a23-mkbootimg")
    need = ("mkbootimg.py", "unpack_bootimg.py")
    if not all(os.path.exists(os.path.join(d, n)) for n in need):
        if given:
            die("%s does not contain mkbootimg.py and unpack_bootimg.py" % given)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.rmtree(d, ignore_errors=True)
        print("cloning mkbootimg tools from", MIRROR)
        subprocess.run(["git", "clone", "--depth", "1", MIRROR, d], check=True)
    return d


def unpack(tools, img, outdir):
    """Return (args, header_version) where args is the mkbootimg argument list."""
    os.makedirs(outdir, exist_ok=True)
    p = subprocess.run(
        [sys.executable, os.path.join(tools, "unpack_bootimg.py"), "--boot_img", img,
         "--out", outdir, "--format", "mkbootimg", "-0"],
        check=True, capture_output=True)
    # Every argument is NUL-terminated, so the last split element is the empty tail.
    # Empty arguments in the middle are real (e.g. `--board ""`) and must be kept.
    parts = p.stdout.split(b"\0")
    if parts and parts[-1] == b"":
        parts.pop()
    return [a.decode() for a in parts]


def get(args, name):
    return args[args.index(name) + 1] if name in args else None


def put(args, name, value):
    if name in args:
        args[args.index(name) + 1] = value
    else:
        args += [name, value]


def stock_kernel_kind(path):
    with open(path, "rb") as f:
        head = f.read(4)
    if head[:2] == b"\x1f\x8b":
        return "gzip"
    if head == b"\x02\x21\x4c\x18":
        return "lz4"
    return "raw"


def build_kernel(image, kind, workdir):
    out = os.path.join(workdir, "kernel.new")
    if kind == "gzip":
        with open(image, "rb") as src, open(out, "wb") as raw:
            # mtime=0 and no name: reproducible output
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as gz:
                shutil.copyfileobj(src, gz)
    elif kind == "lz4":
        die("stock kernel is lz4-compressed; recompress Image with `lz4 -l -9` and pass that "
            "file as --kernel together with --kernel-format raw")
    else:
        shutil.copyfile(image, out)
    return out


def run_mkbootimg(tools, args, out):
    cmd = [sys.executable, os.path.join(tools, "mkbootimg.py")] + args + ["-o", out]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boot", required=True, help="stock boot.img")
    ap.add_argument("--vendor-boot", help="stock vendor_boot.img (needed for header v3/v4)")
    ap.add_argument("--kernel", required=True, help="arch/arm64/boot/Image from the bring-up build")
    ap.add_argument("--dtb", required=True, help="khaje-a23_eur_open_w00_r09.dtb")
    ap.add_argument("--kernel-format", choices=["auto", "raw", "gzip"], default="auto",
                    help="auto = same as the stock kernel (default)")
    ap.add_argument("--outdir", default="a23_out")
    ap.add_argument("--mkbootimg-dir")
    a = ap.parse_args()

    tools = ensure_tools(a.mkbootimg_dir)
    work = tempfile.mkdtemp(prefix="a23repack-")
    os.makedirs(a.outdir, exist_ok=True)

    args = unpack(tools, a.boot, os.path.join(work, "boot"))
    hv = int(get(args, "--header_version") or 0)
    kern_stock = get(args, "--kernel")
    if not kern_stock or not os.path.exists(kern_stock):
        die("could not extract the stock kernel from %s" % a.boot)
    kind = stock_kernel_kind(kern_stock) if a.kernel_format == "auto" else a.kernel_format
    print("stock boot.img: header v%d, kernel is %s" % (hv, kind))
    new_kernel = build_kernel(a.kernel, kind, work)

    results = []
    if hv <= 1:
        # DTB is appended to the kernel image.
        appended = os.path.join(work, "kernel.dtb")
        with open(appended, "wb") as o:
            for p in (new_kernel, a.dtb):
                with open(p, "rb") as f:
                    shutil.copyfileobj(f, o)
        put(args, "--kernel", appended)
    elif hv == 2:
        put(args, "--kernel", new_kernel)
        put(args, "--dtb", a.dtb)
    else:
        put(args, "--kernel", new_kernel)
        if not a.vendor_boot:
            die("header v%d keeps the DTB in vendor_boot.img: pass --vendor-boot" % hv)

    out_boot = os.path.join(a.outdir, "boot_a23_bringup.img")
    run_mkbootimg(tools, args, out_boot)
    results.append(out_boot)

    if hv >= 3:
        vargs = unpack(tools, a.vendor_boot, os.path.join(work, "vendor_boot"))
        if get(vargs, "--dtb") is None:
            die("stock vendor_boot.img has no DTB section to replace")
        put(vargs, "--dtb", a.dtb)
        out_vb = os.path.join(a.outdir, "vendor_boot_a23_bringup.img")
        # for vendor_boot the output goes through --vendor_boot, not -o
        put(vargs, "--vendor_boot", out_vb)
        subprocess.run([sys.executable, os.path.join(tools, "mkbootimg.py")] + vargs, check=True)
        results.append(out_vb)

    shutil.rmtree(work, ignore_errors=True)
    print("\nwrote:")
    for r in results:
        print("  %s  (%d bytes)" % (r, os.path.getsize(r)))
    print("\nStock images were not touched. Keep them: you need them to get back.")


if __name__ == "__main__":
    main()
