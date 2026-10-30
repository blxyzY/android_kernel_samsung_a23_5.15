# Galaxy A23 4G (SM-A235F, board rev 9): percobaan boot pertama kernel 5.15

**Status: berhasil dikompilasi dan di-link, tetapi belum pernah dijalankan di perangkat.**
Anggap flash pertama sebagai eksperimen yang bisa saja tidak boot. Simpan `boot.img` stok
(dan `vendor_boot.img` / `dtbo.img` stok) supaya bisa dikembalikan lewat Download Mode.

## Isi paket (`a23-bringup-r09.tar.gz`)

| File | Fungsi |
|---|---|
| `Image` | kernel `5.15.216-a23-bringup`, arm64, ~30 MB, clang 18, tanpa LTO/CFI/debug info |
| `khaje-base.dtb` | DTB dasar khaje (tidak digabung). **Ini yang masuk ke boot.img.** |
| `dtbo_r09.img` | overlay board rev 9 saja. **Pakai ini dulu.** |
| `dtbo.img` | overlay r00, r01, r08, r09 (semua entri `id=0 rev=0`, persis hasil `mkdtimg` di `build.sh` 4.19) |
| `khaje-a23_eur_open_w00_r09.dtb` | base + overlay r09 sudah digabung. Hanya untuk referensi/diagnosis. |
| `repack_boot.py` | mengganti kernel dan DTB di `boot.img` stokmu (header v0 s/d v4) |
| `System.map`, `kernel.config` | untuk membaca alamat dari log crash |

Alurnya mengikuti `build.sh` 4.19 milikmu: DTB dasar ada di boot.img, overlay board ada di
partisi `dtbo`. Karena itu **dtbo stok (overlay 4.19) tidak cocok** dengan DTB dasar 5.15 dan
harus diganti bersama kernel.

## Yang sudah dicek dan yang belum

Sudah: kompilasi + link penuh; DTB r09 (identitas board, binding driver, tidak ada region
reserved-memory yang bertabrakan); `repack_boot.py` diuji dengan `mkbootimg` asli pada
boot image sintetis header v2 dan v4 (+ vendor_boot): hanya kernel dan DTB yang berubah,
ramdisk/cmdline/offset/os_version tetap sama.

**Belum, dan tidak bisa dicek tanpa perangkat:** boot itu sendiri, probe UFS/eMMC, USB, PMIC,
touch. Tidak ada emulator SM6225.

## Batasan yang akan terlihat

1. **Tidak ada tampilan layar.** DT panel/audio/kamera tidak ikut (labelnya berasal dari repo DT
   display/audio/kamera Qualcomm yang tidak ada di checkout A05s). Meskipun kernel berjalan, layar
   kemungkinan besar tetap hitam. **Jangan memakai layar untuk menilai berhasil/tidaknya boot.**
2. **Ramdisk stok mengharapkan modul 4.19.** Modul di `vendor_boot`/`vendor_dlkm` tidak cocok
   dengan kernel 5.15. Driver kritis sudah built-in, tetapi first-stage init Android bisa
   berhenti saat memuat modul gagal. Kalau itu yang terjadi, langkah berikutnya mengubah ramdisk,
   bukan kernel.
3. **Debug Samsung (`SEC_DEBUG`, `SEC_QC_DEBUG`) dimatikan** karena menyebabkan simbol tak
   terpecahkan pada objek built-in. Akibatnya tidak ada penanganan upload-mode/crash-reason Samsung.
4. Opsi sanitizer (`UBSAN`, `KASAN`, `KFENCE`) sengaja dimatikan: `UBSAN_TRAP` mengubah pelanggaran
   batas array di kode vendor hasil port menjadi panic.

## Langkah

1. Ambil image **milikmu sendiri** dari firmware yang sedang terpasang: `boot.img`, `dtbo.img`, dan
   `vendor_boot.img` bila ada. Cek versi header:
   `python3 unpack_bootimg.py --boot_img boot.img` (header v3/v4 berarti ada `vendor_boot.img`).
2. Buat boot image baru (image stok tidak disentuh):

   ```
   python3 repack_boot.py --boot boot_stok.img --kernel Image \
       --dtb khaje-base.dtb --outdir out
   # header v3/v4: tambahkan  --vendor-boot vendor_boot_stok.img
   ```
   Hasil: `out/boot_a23_bringup.img` (dan `out/vendor_boot_a23_bringup.img` untuk v3/v4).
   Skrip ini mengambil `mkbootimg` AOSP terbaru dari mirror GitHub ke `~/.cache/a23-mkbootimg`
   (atau pakai `--mkbootimg-dir`).
3. Flash dengan cara yang biasa kamu pakai untuk kernel 4.19 (bootloader harus unlocked dan
   verifikasi vbmeta dimatikan): `boot_a23_bringup.img`, `dtbo_r09.img` sebagai partisi `dtbo`, dan
   `vendor_boot_a23_bringup.img` bila header v3/v4. Salah flash bisa menyebabkan bootloop.
4. Pastikan bisa kembali ke stok: Download Mode (Volume Atas+Bawah sambil colok USB), lalu flash
   boot/dtbo (dan vendor_boot) stok.

## Membaca log setelah boot gagal (tanpa layar)

DTB mendefinisikan region `ramoops` tetap di `0x78c20000` (0x80000) dengan zona **console tepat
di `0x78c40000–0x78c80000`**, alamat dan ukuran yang sama dengan zona console kernel stok 4.19
(`ramoops@78c00000`). Jadi setelah boot 5.15 gagal, flash balik boot/dtbo stok, boot ke Android
stok, lalu:

```
adb shell su -c 'cat /sys/fs/pstore/console-ramoops-0'
```

Isinya adalah log kernel 5.15 dari percobaan terakhir. Ini upaya terbaik, bukan jaminan:
- log kosong berarti kegagalan terjadi sebelum pstore diinisialisasi (sangat awal: bootloader
  menolak image/DTB, header Image, atau pemilihan DT), atau bootloader membersihkan RAM;
- jika kernel 5.15 sendiri sampai ke userspace, log yang sama ada di `/sys/fs/pstore/` di sana.

## Yang perlu dikirim balik

- isi `console-ramoops-0` setelah percobaan gagal;
- versi header `boot.img` stokmu (keluaran `unpack_bootimg.py`), dan apakah ada `vendor_boot.img`;
- jika gagal sangat awal (log kosong): `dtbo.img` dan `vendor_boot.img` stokmu.

Dengan itu iterasi berikutnya terarah, bukan menebak.
