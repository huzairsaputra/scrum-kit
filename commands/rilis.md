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
MR-nya belum ada → berhenti dan laporkan SHA branch itu ke manusia. Rilis yang terhenti karena
batas pemakaian mengikuti `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Batas pemakaian";
aturan di atas tetap menentukan `S`.

## Mode lokal (tanpa remote)

Periksa `git remote` sekali di awal. Kosong → rilis berjalan dalam **mode lokal**, seperti
`/scrum-kit:sprint`. Tulis di awal laporan ke manusia: "Mode lokal: tidak ada remote; pemeriksaan
forge (pipeline, MR, CI pada SHA HEAD) dilewati." Semua langkah tetap berlaku, dengan pengganti
berikut:

- Tanpa `git fetch` dan tanpa `git push`; `origin/<branch>` dibaca sebagai `<branch>` lokal. Tidak
  ada yang di-push, termasuk tag.
- Langkah 0: README diperiksa dan ditulis ulang dengan cara yang sama, tetapi tanpa forge tidak ada
  lencana dan tidak ada pemeriksaan coverage: laporkan "Mode lokal: tanpa forge, lencana pipeline,
  coverage, dan rilis dilewati". Perubahan README masuk ke basis sebagai merge lokal
  (`git merge --no-ff`) dari branch `claude/readme-<versi>` setelah `gate.ci` lokal hijau dan PO
  menyetujui di chat.
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
- Langkah 8: tanpa pemantauan pipeline dan tanpa rilis di forge; deploy di luar kit, laporkan ke manusia. Tag beranotasi
  dibuat lokal. Hapus `claude/rilis-<versi>` hanya bila `git merge-base --is-ancestor
  claude/rilis-<versi> <rilis>` sukses.

## Langkah

0. **README dan lencana.** Kerjakan sebelum `S` dicatat, karena perubahan README harus sudah ada di
   basis sebelum isi rilis dibekukan. Baca `README.md` di akar repositori.
   - **Template atau aplikasi?** README masih template stack bila berkasnya tidak ada, atau salah satu
     ini berlaku: memuat teks bawaan framework (mis. "About Laravel", "Create Next App", "bootstrapped
     with", "This template provides a minimal setup", "Getting started with Create React App",
     "Welcome to Goravel", "Getting started / To make it easy for you to get started with GitLab" milik
     GitLab, "This README would normally document" milik Rails); tidak pernah menyebut proyek ini
     (`proyek` di `kit.json`); tidak menjelaskan aplikasi ini untuk apa. Selain itu README sudah
     menjelaskan aplikasi: biarkan.
   - **Tulis ulang README template.** Susun dari yang sudah dicatat proyek: `kit.json` (nama, stack,
     modul, gate), `CLAUDE.md`, SRS dan backlog bila ada, serah terima, dan kodenya. Jelaskan aplikasi
     ini untuk apa, siapa penggunanya, modulnya, cara menjalankan, cara menjalankan gate (hanya perintah
     yang memang ada di `Makefile`, skrip `composer.json`/`package.json`, atau CI), branch, dan lisensi
     bila sebelumnya ada. Buang teks bawaan stack. Tulis dalam bahasa dokumen proyek itu sendiri kecuali
     PO meminta lain. Jangan mengarang: fakta yang tidak ditemukan menjadi baris tampak
     `TODO (PO): <yang kurang>`; jangan baca berkas `.env`.
   - **Lencana, tiga wajib ditambah lencana stack,** dalam satu blok di bawah judul, masing-masing bertaut ke sumbernya
     (`<host>`, `<proyek>` = `forge.proyek`, `<prod>` = `branch.rilis`):
     - GitLab: pipeline `https://<host>/<proyek>/badges/<prod>/pipeline.svg`, coverage
       `https://<host>/<proyek>/badges/<prod>/coverage.svg?job=<job test>` (job yang lognya melaporkan
       coverage), rilis
       `https://<host>/<proyek>/-/badges/release.svg`.
     - GitHub: `badge.svg?branch=<prod>` dari workflow CI; coverage dari layanan coverage tempat CI
       mengunggah (Codecov `https://codecov.io/gh/<proyek>/branch/<prod>/graph/badge.svg`, atau
       Coveralls); rilis `https://img.shields.io/github/v/release/<proyek>`.

     **Lencana stack** menyusul yang tiga itu, satu untuk masing-masing: bahasa atau runtime,
     framework, dan basis data (layanan antrean atau penyimpanan hanya bila dokumen proyek sendiri
     menyebutnya inti). Baca versinya dari repositori, jangan menebak: `go.mod` (baris `go` dan modul
     framework), `composer.json` (`require.php`, `laravel/framework`), `package.json` (`engines`,
     dependensi), `pyproject.toml`; basis data dari image di `docker-compose*.yml` atau
     `DB_CONNECTION` di `.env.example`, bukan dari `.env`. Unsur stack yang tidak bisa dibuktikan tidak
     diberi lencana. Pakai lencana statis yang bertaut ke situs resminya:
     `https://img.shields.io/badge/<Nama>-<versi>-<warna hex>?logo=<slug>&logoColor=white` (spasi di
     nama jadi `_`, tanda hubung jadi `--`), misalnya Go `00ADD8`, PHP `777BB4`, Laravel `FF2D20`,
     Node.js `5FA04E`, React `61DAFB`, PostgreSQL `336791`, MySQL `4479A1`; stack lain memakai `555555`
     tanpa `logo=`. Batasi sekitar lima lencana seluruhnya.

     Tambahkan hanya lencana yang belum ada; lencana yang sudah ada dan isi README yang sungguhan
     dibiarkan.
   - **Coverage harus ada, atau berhenti.** Periksa dari forge, bukan dari gambarnya (lencana proyek
     GitLab privat butuh login): GitLab, pipeline basis terbaru punya nilai `coverage` yang tidak
     kosong; GitHub, workflow CI mengunggah coverage ke layanan yang lencananya dipilih. CI belum
     melaporkan coverage → **berhenti dan tanya PO**: jangan merge lencana yang akan menampilkan
     "unknown". Jelaskan yang kurang (GitLab: kata kunci `coverage:` berisi regex pada job test; GitHub:
     langkah unggah ke Codecov atau Coveralls). Mengubah CI adalah pekerjaan `platform-tooling` dan
     item tersendiri, bukan bagian langkah ini. Lencana rilis menampilkan "no release" sampai
     langkah 8 membuat rilis pertama; itu wajar, bukan kegagalan.
   - **Kirim lewat MR kecil ke basis.** Ada yang perlu diubah → di checkout sendiri (`git worktree add`
     biasa, bukan worktree wilayah) buat branch `claude/readme-<versi>` dari `origin/<basis>`, commit
     hanya `README.md`, push, dan buka MR ke `branch.basis`. Tunjukkan README barunya ke PO di chat
     (seluruh berkas bila ditulis ulang, baris tambahan saja bila tidak), sebut setiap baris
     `TODO (PO)`, dan merge hanya setelah PO menyetujuinya di chat, dengan CI hijau pada SHA HEAD-nya
     ("Cara merge"). Lalu tunggu pipeline basis pada merge itu dan lanjut ke langkah 1. Tidak ada yang
     perlu diubah → tulis "README menjelaskan aplikasi dan punya lencananya" di laporan dan lanjut.
1. **Isi rilis.** `git fetch origin`, catat `S` = `git rev-parse origin/<basis>`. Isi rilis =
   `git log --oneline origin/<rilis>..S`; daftar MR/PR-nya diambil dari pesan merge commit di range
   itu (GitLab: `See merge request !N`; GitHub: `Merge pull request #N`). Kosong → tidak ada yang
   dirilis, berhenti.
2. **Kesiapan basis.**
   - Pipeline basis hijau pada `S`, dan `S` sudah ter-deploy di staging (`dokumen.serah_terima`,
     "terakhir di-deploy"). Beda yang hanya `README.md` dari langkah 0 tidak dihitung.
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
   - Buat rilis di forge dari tag itu dengan catatan rilis langkah 5 (GitHub
     `gh release create <versi> --verify-tag --notes-file <berkas>`; GitLab `glab release create
     <versi> --notes-file <berkas>` atau API Releases), karena lencana rilis menampilkan rilis
     terbaru, bukan tag. Bila rilis tidak bisa dibuat, laporkan bahwa lencana tetap "no release".
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
