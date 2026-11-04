---
description: Rilis terjadwal ke produksi — periksa isi dan kesiapan basis, nilai kebutuhan downtime, catatan rilis, satu MR basis → rilis, merge atas persetujuan PO, tag, beres-beres
argument-hint: "[versi] [jadwal]"
---

# Rilis

Argumen: $ARGUMENTS. Kata pertama adalah versi hanya bila cocok pola semver (`1.2.3` atau `v1.2.3`);
sisanya (atau semuanya, bila kata pertama bukan versi) adalah jadwal.

Kamu orkestrator: mempromosikan `branch.basis` ke `branch.rilis` (produksi) secara terjadwal. Ini
jalur untuk semua perubahan yang boleh menunggu jadwal (fitur sprint, bugfix, coldfix). Perbaikan
yang tidak bisa menunggu adalah `/scrum-kit:hotfix` jalur darurat. Tidak ada kode aplikasi yang
ditulis di sini, jadi tidak ada agen yang perlu didispatch.

Baca `CLAUDE.md` dan `.claude/kit.json` dulu. `branch.rilis` kosong → berhenti: produksi proyek ini
di-deploy dari basis, tidak ada yang perlu dipromosikan (isi `branch.rilis` lewat
`/scrum-kit:kit-init --perbarui` bila proyek punya branch produksi).

**Cara merge**: selalu merge commit, tanpa squash, rebase, atau fast-forward. GitLab:
`detailed_merge_status` = `mergeable`, merge dengan `sha` dan `squash` = false. GitHub:
`gh pr view <n> --json mergeStateStatus` = `CLEAN`, lalu
`gh pr merge <n> --merge --match-head-commit <sha>`.

## Langkah

1. **Isi rilis.** `git fetch origin`, catat `S` = `git rev-parse origin/<basis>`. Isi rilis =
   `git log --oneline origin/<rilis>..S`; daftar MR/PR-nya diambil dari pesan merge commit di range
   itu (GitLab: `See merge request !N`; GitHub: `Merge pull request #N`). Kosong → tidak ada yang
   dirilis, berhenti.
2. **Kesiapan basis.**
   - Pipeline basis hijau pada `S`, dan `S` sudah ter-deploy di staging (`dokumen.serah_terima`,
     "terakhir di-deploy").
   - MR integrasi sprint yang masih terbuka: isinya belum ada di basis. Tanya PO apakah rilis
     menunggunya.
   - Item di "Sedang berjalan" yang sudah masuk basis tetapi belum selesai: tanya PO apakah ikut
     rilis atau rilis ditunda.
   - `git log --oneline --no-merges S..origin/<rilis>` harus kosong. Ada commit → hotfix yang belum
     di-back-merge; back-merge dulu (lihat `/scrum-kit:hotfix`).
   - Checklist "sebelum rilis ke produksi" di serah terima tercentang semua; yang belum → tanya PO.
3. **Downtime.** Periksa migrasi dan konfigurasi di `git diff origin/<rilis> S`.
   - Migrasi destruktif (drop, rename, ubah tipe), indeks atau perubahan yang mengunci tabel besar,
     perubahan env/infra, atau apa pun yang butuh restart terjadwal → rilis ini butuh jendela
     pemeliharaan (coldfix). Siapkan teks pengumuman untuk pengguna: waktu, perkiraan durasi, dampak.
   - Perubahan kontrak yang tidak kompatibel mundur → siapkan teks pemberitahuan untuk tim klien
     (FE/mobile).
   - Perubahan infra produksi milik DevOps manusia: cantumkan sebagai langkah mereka, jangan dikerjakan.
4. **Versi.** Dari argumen bila ada. Bila tidak, usulkan dari tag terakhir
   (`git describe --tags --abbrev=0 origin/<rilis>`, format mengikuti tag yang sudah ada): patch bila
   hanya perbaikan, minor bila ada fitur, major bila ada perubahan yang tidak kompatibel. Belum ada tag
   sama sekali → tanya PO versi pertamanya. Konfirmasi versi dan jadwal ke PO dalam satu pertanyaan.
5. **Catatan rilis** di deskripsi MR: per kelompok (fitur, perbaikan, keamanan, migrasi, perubahan
   kontrak), satu baris per MR beserta tautannya; kebutuhan downtime dan langkah DevOps bila ada.
6. **MR.** Bekukan isi rilis: `git push origin S:refs/heads/claude/rilis-<versi>`, lalu MR
   `claude/rilis-<versi>` → `branch.rilis` berjudul `rilis: <proyek> <versi>`. Merge lain yang masuk
   ke basis sesudahnya tidak ikut rilis ini. Tunggu pipeline hijau pada `S`.
7. **Merge hanya atas persetujuan PO di chat** untuk MR itu, pada jadwal yang disepakati.
   - Jadwal belum tiba → berhenti dan laporkan: tautan MR, `S`, versi, jadwal, dan teks pengumuman.
     Saat jadwal tiba, manusia menjalankan ulang `/scrum-kit:rilis <versi>`; lanjutkan dari MR yang
     sudah ada, pastikan HEAD-nya masih `S`.
   - Merge dengan `sha` = `S`.
8. **Pasca-merge.**
   - Pantau pipeline rilis sampai deploy; bila ada job migrasi, pastikan lognya melaporkan sukses.
   - Tag beranotasi `<versi>` pada merge commit di `branch.rilis`, lalu push tag itu. Hapus branch
     `claude/rilis-<versi>`.
   - Perbarui `dokumen.serah_terima`: "Rilis produksi terakhir" (versi, MR, SHA, tanggal), kosongkan
     checklist produksi yang sudah terpenuhi.
   - Serahkan teks pengumuman/pemberitahuan ke PO; jangan mengirimnya sendiri.

## Aturan

- Jangan pernah push langsung ke `branch.rilis` maupun basis; semua lewat MR.
- Pipeline merah, konflik basis ↔ rilis, atau deploy gagal → berhenti dan laporkan; jangan
  menambal di branch rilis. Perbaikan yang mendesak lewat `/scrum-kit:hotfix` jalur darurat.
- Rollback produksi adalah keputusan PO dan DevOps; siapkan informasinya (SHA rilis sebelumnya,
  migrasi yang harus dibalik), jangan jalankan sendiri.
