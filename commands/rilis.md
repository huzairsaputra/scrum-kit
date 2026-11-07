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

**Cara merge**: baca `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Cara merge" dan ikuti.

**Lanjutan**: bila MR `claude/rilis-<versi>` → `branch.rilis` sudah terbuka (perintah dijalankan ulang
saat jadwal tiba), ambil `S` dari baris `S: <sha>` di deskripsinya dan langsung ke langkah 7. Jangan
menghitung ulang `S` dan jangan push ulang branch itu. Branch `claude/rilis-<versi>` sudah ada tetapi
MR-nya belum ada → berhenti dan laporkan SHA branch itu ke manusia.

## Mode lokal (tanpa remote)

Periksa `git remote` sekali di awal. Kosong → rilis berjalan dalam **mode lokal**, seperti
`/scrum-kit:sprint`. Tulis di awal laporan ke manusia: "Mode lokal: tidak ada remote; pemeriksaan
forge (pipeline, MR, CI pada SHA HEAD) dilewati." Semua langkah tetap berlaku, dengan pengganti
berikut:

- Tanpa `git fetch` dan tanpa `git push`; `origin/<branch>` dibaca sebagai `<branch>` lokal. Tidak
  ada yang di-push, termasuk tag.
- Langkah 1: daftar perubahan diambil dari merge commit lokal (`Merge branch '<branch>'`), bukan
  nomor MR/PR.
- Langkah 2: pipeline basis diganti `gate.ci` lokal yang hijau pada `S` (di worktree sementara pada
  `S`, keluarannya di laporan). "MR integrasi sprint yang masih terbuka" = branch integrasi sprint
  yang belum masuk basis (`git branch --no-merged <basis>`).
- Langkah 5–6: tanpa MR. Bekukan isi rilis dengan `git branch claude/rilis-<versi> S`. Catatan rilis
  (diawali baris `rilis: <proyek> <versi>`, lalu `S: <sha>`) ditulis ke berkas di scratchpad dan
  ditunjukkan ke PO.
- **Lanjutan**: branch `claude/rilis-<versi>` sudah ada → `S` = `git rev-parse claude/rilis-<versi>`,
  susun ulang catatan rilis dari isi rilis pada `S`, lalu langsung ke langkah 7.
- Langkah 7: sesudah PO menyetujui di chat: `git switch <rilis>` lalu
  `git merge --no-ff -F <berkas catatan> claude/rilis-<versi>` (catatan rilis menjadi pesan merge
  commit).
- Langkah 8: tanpa pemantauan pipeline; deploy di luar kit, laporkan ke manusia. Tag beranotasi
  dibuat lokal. Hapus `claude/rilis-<versi>` hanya bila `git merge-base --is-ancestor
  claude/rilis-<versi> <rilis>` sukses.

## Langkah

1. **Isi rilis.** `git fetch origin`, catat `S` = `git rev-parse origin/<basis>`. Isi rilis =
   `git log --oneline origin/<rilis>..S`; daftar MR/PR-nya diambil dari pesan merge commit di range
   itu (GitLab: `See merge request !N`; GitHub: `Merge pull request #N`). Kosong → tidak ada yang
   dirilis, berhenti.
2. **Kesiapan basis.**
   - Pipeline basis hijau pada `S`, dan `S` sudah ter-deploy di staging (`dokumen.serah_terima`,
     "terakhir di-deploy").
   - MR integrasi sprint yang masih terbuka: isinya belum ada di basis. Tanya PO apakah rilis
     menunggunya. Menunggu → berhenti; jalankan ulang perintah ini sesudah MR itu merge.
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
5. **Catatan rilis** di deskripsi MR, diawali baris `S: <sha>`: per kelompok (fitur, perbaikan, keamanan, migrasi, perubahan
   kontrak), satu baris per MR beserta tautannya; kebutuhan downtime dan langkah DevOps bila ada.
6. **MR.** Bekukan isi rilis:
   `git push --force-with-lease=refs/heads/claude/rilis-<versi>: origin S:refs/heads/claude/rilis-<versi>`
   (nilai harapan kosong: push gagal bila branch sudah ada; gagal → lihat **Lanjutan**). Lalu MR
   `claude/rilis-<versi>` → `branch.rilis` berjudul `rilis: <proyek> <versi>`. Merge lain yang masuk
   ke basis sesudahnya tidak ikut rilis ini. Tunggu pipeline hijau pada `S`; bila CI tidak memicu
   pipeline untuk branch itu, pipeline basis yang hijau pada `S` (langkah 2) menjadi buktinya.
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

- Jangan pernah push langsung ke `branch.rilis` maupun basis; semua lewat MR (mode lokal: merge lokal
  atas persetujuan PO, lihat "Mode lokal").
- Pipeline merah, konflik basis ↔ rilis, atau deploy gagal → berhenti dan laporkan; jangan
  menambal di branch rilis. Perbaikan yang mendesak lewat `/scrum-kit:hotfix` jalur darurat.
- Rollback produksi adalah keputusan PO dan DevOps; siapkan informasinya (SHA rilis sebelumnya,
  migrasi yang harus dibalik), jangan jalankan sendiri.
