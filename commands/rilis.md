---
description: Rilis terjadwal ke produksi — periksa isi dan kesiapan basis, nilai kebutuhan downtime, catatan rilis, satu MR basis → rilis, merge atas persetujuan PO, tag, beres-beres
argument-hint: "[versi] [jadwal]"
---

# Rilis $ARGUMENTS

Kamu orkestrator: mempromosikan `branch.basis` ke `branch.rilis` (produksi) secara terjadwal. Ini
jalur untuk semua perubahan yang boleh menunggu jadwal (fitur sprint, bugfix, coldfix). Perbaikan
yang tidak bisa menunggu adalah `/scrum-kit:hotfix` jalur darurat. Tidak ada kode aplikasi yang
ditulis di sini, jadi tidak ada agen yang perlu didispatch.

Baca `CLAUDE.md` dan `.claude/kit.json` dulu. `branch.rilis` kosong → berhenti: produksi proyek ini
di-deploy dari basis, tidak ada yang perlu dipromosikan.

## Langkah

1. **Isi rilis.** `git fetch origin`, lalu `git log --oneline origin/<rilis>..origin/<basis>` dan
   daftar MR yang sudah merge ke basis sejak rilis terakhir. Kosong → tidak ada yang dirilis, berhenti.
2. **Kesiapan basis.**
   - Pipeline basis hijau pada HEAD, dan HEAD itu sudah ter-deploy di staging (`dokumen.serah_terima`,
     "terakhir di-deploy").
   - Tidak ada pekerjaan setengah jadi di basis: MR integrasi sprint yang sedang berjalan belum merge,
     atau item di "Sedang berjalan" yang sudah masuk basis tetapi belum selesai → tanya PO apakah ikut
     rilis atau ditunda.
   - `git log --oneline --no-merges origin/<basis>..origin/<rilis>` harus kosong. Ada commit → hotfix
     yang belum di-back-merge; back-merge dulu (lihat `/scrum-kit:hotfix`).
   - Checklist "sebelum rilis ke produksi" di serah terima tercentang semua; yang belum → tanya PO.
3. **Downtime.** Periksa migrasi dan konfigurasi di `git diff origin/<rilis>..origin/<basis>`.
   - Migrasi destruktif (drop, rename, ubah tipe, kunci tabel besar), perubahan env/infra, atau apa
     pun yang butuh restart terjadwal → rilis ini butuh jendela pemeliharaan (coldfix). Siapkan teks
     pengumuman untuk pengguna: waktu, perkiraan durasi, dampak. PO yang menetapkan jadwal; jangan
     merge sebelum jadwal itu.
   - Perubahan kontrak yang tidak kompatibel mundur → siapkan teks pemberitahuan untuk tim klien
     (FE/mobile).
   - Perubahan infra produksi milik DevOps manusia: cantumkan sebagai langkah mereka, jangan dikerjakan.
4. **Versi.** Argumen pertama bila ada. Bila tidak, usulkan dari tag terakhir (`git describe --tags
   --abbrev=0 origin/<rilis>`): patch bila hanya perbaikan, minor bila ada fitur, major bila ada
   perubahan yang tidak kompatibel. Konfirmasi ke PO bersama jadwal.
5. **Catatan rilis** di deskripsi MR: per kelompok (fitur, perbaikan, keamanan, migrasi, perubahan
   kontrak), satu baris per MR beserta tautannya; kebutuhan downtime dan langkah DevOps bila ada.
6. **MR** `branch.basis` → `branch.rilis` dengan judul `rilis: <proyek> <versi>`. Branch sumber
   **tidak** dihapus saat merge. Tunggu pipeline hijau pada HEAD dan status "mergeable".
7. **Merge hanya atas persetujuan PO di chat** untuk MR itu, pada jadwal yang disepakati. Merge
   dengan SHA HEAD.
8. **Pasca-merge.**
   - Pantau pipeline rilis sampai deploy; bila ada job migrasi, pastikan lognya melaporkan sukses.
   - Tag beranotasi `<versi>` pada merge commit di `branch.rilis`, lalu push tag itu.
   - Perbarui `dokumen.serah_terima`: rilis terakhir (versi, MR, SHA, tanggal), kosongkan checklist
     produksi yang sudah terpenuhi.
   - Serahkan teks pengumuman/pemberitahuan ke PO; jangan mengirimnya sendiri.

## Aturan

- Jangan pernah push langsung ke `branch.rilis` maupun basis; semua lewat MR.
- Pipeline merah, konflik basis ↔ rilis, atau deploy gagal → berhenti dan laporkan; jangan
  menambal di branch rilis. Perbaikan yang mendesak lewat `/scrum-kit:hotfix` jalur darurat.
- Rollback produksi adalah keputusan PO dan DevOps; siapkan informasinya (SHA rilis sebelumnya,
  migrasi yang harus dibalik), jangan jalankan sendiri.
