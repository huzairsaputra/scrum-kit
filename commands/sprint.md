---
description: Orkestrasi satu sprint — sinkron spesifikasi, fondasi, kontrak, implementasi paralel, QA, review, lalu satu MR integrasi ke branch basis
argument-hint: "<nomor-sprint>"
---

# Orkestrasi Sprint $0

Kamu adalah orkestrator (Scrum Master). Kamu **tidak menulis kode aplikasi**; kamu membagi kerja ke
agen plugin (`scrum-kit:<agen>`) lewat CLI headless (lihat "Cara mendispatch agen"), menjaga barrier,
dan menyiapkan branch serta MR.

## Cara mendispatch agen

Baca `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Mendispatch agen" dan ikuti.

**Cara merge** (termasuk syarat CI dan bersih-bersih branch): baca berkas yang sama bagian "Cara
merge" dan ikuti.

Baca dulu `CLAUDE.md` dan `.claude/kit.json`. Semua nama berikut berasal dari `kit.json`:
`{n}` = $0, `{nn}` = $0 dua digit; branch integrasi `branch.integrasi`, basis `branch.basis`,
backlog `dokumen.backlog`, laporan `dokumen.laporan`, gate `gate.*`.

## Mode lokal (tanpa remote)

Periksa `git remote` sekali di awal. Kosong → sprint berjalan dalam **mode lokal**. Tulis di awal
laporan ke manusia dan di ringkasan: "Mode lokal: tidak ada remote; pemeriksaan forge (pipeline, MR,
CI pada SHA HEAD) dilewati." Semua langkah tetap berlaku, dengan pengganti berikut:

- Tanpa `git fetch` dan tanpa `git push`; `origin/<branch>` dibaca sebagai `<branch>` lokal (mis.
  basis diff reviewer = `<branch.integrasi>`). Tidak ada yang di-push.
- Langkah 0: pipeline basis dilewati (hanya `gate.ci` lokal); branch integrasi dibuat lokal dari
  branch basis: `git branch <branch.integrasi> <branch.basis>`.
- Langkah 5: tanpa MR. Syarat CI diganti `gate.ci` lokal yang hijau pada HEAD branch yang akan
  di-merge (keluarannya di laporan), dan checklist DoD dicentang di laporan item. Branch item (branch
  yang sama yang akan menjadi sumber MR, lihat Langkah 5) di-merge ke branch integrasi dengan merge
  commit: `git switch <branch.integrasi>` lalu `git merge --no-ff <branch item>`.
- Langkah 6: tanpa MR integrasi. Sesudah product owner menyetujui di chat: `git switch
  <branch.basis>` lalu `git merge --no-ff <branch.integrasi>`. Belum disetujui → berhenti dan
  laporkan; branch integrasi tetap ada.
- Bersih-bersih dan merge mengikuti "Cara merge", bagian "Mode lokal".

## Langkah -1 — Spesifikasi eksternal

Hanya bila `spek_eksternal.drive_folder_id` terisi; selain itu lewati.

1. Baca folder Drive itu lewat konektor Google Drive.
   - Tidak terbaca dan `spek_eksternal.wajib` = true → **HENTIKAN sprint**, laporkan cara memperbaiki
     akses, tunggu manusia. Jangan memakai salinan lama sebagai pengganti.
   - Tidak terbaca dan tidak wajib → lanjut dengan peringatan tertulis di ringkasan sprint.
2. `scrum-kit:spec-change-adapter` (sendirian, barrier) membandingkan Drive dengan skema, kontrak, dan
   laporan sprint sebelumnya. Ada drift → item penyesuaian untuk sprint $0 saja; MR-nya merge dulu.

## Langkah 0 — Persiapan

1. Baca backlog sprint $0. Belum ada/kosong → berhenti, minta manusia mengisinya. Jangan mengarang backlog.
2. Jalankan `gate.ci` secara lokal di basis, dan periksa juga pipeline basis bila forge punya;
   laporkan keduanya. Merah → serahkan ke `scrum-kit:platform-tooling` lebih dulu.
3. **Gerbang kesiapan backlog.** Cara membaca laporan dan baris serah terimanya:
   `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Gerbang kesiapan backlog". Laporannya:
   `docs/sprints/backlog-check-{nn}.md`.
   - Tidak ada → sampaikan sekali bahwa belum ada laporan kesiapan, dan bahwa skill gratis
     "Backlog Check" dari Lanewright Planning membuatnya; tanya apakah lanjut tanpa laporan. Laporan
     ini tidak wajib: lanjut bila pengguna berkata begitu, selain itu berhenti.
   - Ada → baca putusan, tabel berkas yang diperiksa, dan blok persetujuan. Hitung sidik jari backlog
     sprint $0 saat ini: `PELUNCUR=$(sh "${CLAUDE_PLUGIN_ROOT}/hooks/cari-python.sh" --peluncur)`, lalu
     `$PELUNCUR "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-sidik.py" <backlog>`; bandingkan dengan baris
     backlog itu di tabel.
   - Sidik jari berbeda → laporan usang (backlog berubah sesudah diperiksa): sampaikan, lalu tanya
     sekali: lanjut, atau berhenti untuk menjalankan ulang Backlog Check.
   - Putusan NOT READY / BELUM SIAP, atau blok persetujuan kosong (belum ada yang menyetujui) →
     berhenti dan tanya product owner sekali. Lanjut hanya atas keputusan eksplisitnya, dicatat di
     serah terima sebagai baris "Gerbang laporan: dilanjutkan tanpa persetujuan, alasan <alasan>".
     Bila laporan juga usang, satukan dalam pertanyaan yang sama.
   - Sidik jari cocok, putusan READY / READY WITH WARNINGS (atau padanan Indonesianya), dan
     persetujuan terisi → lanjut dan catat di serah terima.
   - Baca juga kolom `Butir DoD tidak berlaku (disetujui):` / `DoD not applicable (approved):` di blok
     persetujuan. Himpunan butir DoD tidak berlaku yang disetujui = butir yang disebut di sana, hanya
     bila persetujuan terisi dan sidik jari cocok; selain itu (termasuk tanpa laporan, atau laporan
     tanpa kolom itu) kosong. Himpunan ini dipakai di langkah 5 dan 6.
   Jangan pernah mengisi blok persetujuan atau mengubah laporan itu sendiri.
4. **Dokumen sprint ter-commit di basis, sebelum worktree pertama dibuat.** Worktree peran hanya
   melihat berkas yang ter-commit; backlog yang belum ter-commit terlihat sebagai templat kosong, dan
   ID yang dikutip kriteria penerimaan (mis. F-01, BR-03, A-04) tidak bisa dicari. Daftar: backlog
   sprint $0, ditambah `docs/requirements/`, rencana mingguan, dan laporan kesiapan bila ada, serta
   `dokumen.serah_terima` bila langkah 3 menulis barisnya.
   - Di branch basis (`git switch <branch.basis>`, `git fetch origin`,
     `git merge --ff-only origin/<branch.basis>`): `git status --porcelain -- <daftar>` harus kosong
     dan `git ls-files -- <daftar>` memuat setiap berkas.
   - Belum → tunjukkan daftar berkas yang belum ter-commit ke manusia. Sesudah dikonfirmasi, commit
     hanya berkas itu: `git add -- <daftar>` lalu `git commit -m "docs: dokumen sprint $0" -- <daftar>`
     (perubahan lain yang ter-stage tidak ikut). Tidak dikonfirmasi → berhenti.
   - Dokumen ini milik orkestrator. Hook kepemilikan tidak membatasi branch basis (di luar pola
     `branch.wilayah`), dan ia tidak memeriksa `git commit`. Commit ini **tidak** di-push ke basis; ia
     sampai ke basis lewat MR integrasi (langkah 5).
5. `git fetch origin`; buat branch integrasi bila belum ada dari `<branch.basis>` lokal (=
   `origin/<branch.basis>` ditambah commit dokumen langkah 4; `git merge-base --is-ancestor
   origin/<branch.basis> <branch.basis>` harus sukses, selain itu berhenti), push. Branch integrasi
   sudah ada tetapi tanpa backlog itu (`git cat-file -e <branch.integrasi>:<backlog>` gagal) → merge
   `<branch.basis>` lokal ke branch integrasi (merge commit), push.
6. Kelompokkan item menurut wilayah pemiliknya (`wilayah.*.agen`).

## Langkah 1 — Fondasi (barrier)

Item skema/pustaka bersama (`shared-module-owner`) dan perkakas (`platform-tooling`) paralel, masing-
masing di worktree sendiri (`scripts/kit/worktree-new.sh <wilayah> <id> $0`). Keduanya merge ke branch
integrasi sebelum lanjut. Lewati bila tidak ada.

## Langkah 2 — Kontrak lebih dulu

Bila `kontrak` terisi: `scrum-kit:api-contract-keeper` menetapkan kontrak seluruh endpoint sprint ini.
Implementer tidak mulai sebelum kontraknya ada.

## Langkah 3 — Implementasi (paralel)

Satu `scrum-kit:module-dev` per modul, worktree per item. Prompt agen memuat: modul, ID item, path
backlog, branch, dan pengingat membaca `CLAUDE.md`. Maksimal dua item berjalan per agen.
Item yang menyunting berkas yang sama berjalan berurutan: worktree item kedua dibuat dari branch
integrasi (`git fetch origin` dulu) sesudah item pertama merge.

## Langkah 4 — Pengujian

Begitu build sebuah modul hijau, `scrum-kit:qa-test-engineer` untuk modul itu
(`worktree-new.sh tests <id> $0 --modul=<m>`), di atas branch implementasinya. Tidak perlu menunggu
modul lain. Bila `modul` di `kit.json` kosong (proyek satu modul), hilangkan `--modul`:
`worktree-new.sh tests <id> $0`.

Itu model bawaan: QA mengerjakan item implementer, dengan ID item itu. Backlog bisa juga memuat
**item QA sendiri** (item berwilayah `tests` dengan ID-nya sendiri). Worktree, branch, laporan, dan MR
item QA selalu memakai ID item QA itu sendiri:

- **(a) Item QA yang menyebut item yang diujinya** (penanda `Menguji: <ID>` atau `Tests: <ID>` di
  teks item; Sprint Planner menulis `Tests:`, keduanya sama artinya): dibuat sesudah
  build item yang diuji hijau, di atas branch item itu:
  `worktree-new.sh tests <id-QA> $0 --base=<branch item yang diuji>` (ditambah `--modul=<m>` bila
  ada modul). Branch item yang diuji tidak ada (sudah merge, atau di luar sprint) → tanpa `--base`.
  Menguji beberapa item → `--base` ke branch item pertama, lalu merge branch item lainnya ke worktree
  itu (`git merge --no-ff`) sebelum agen mulai. Prompt agen memuat ID item QA dan ID item yang diuji.
- **(b) Item implementasi tanpa item QA**: begitu minimal satu item backlog memuat penanda itu, model
  bawaan tidak dipakai di sprint ini; item implementasi yang tidak disebut penanda item mana pun
  tidak mendapat QA.
- **(c) Item QA tanpa item implementasi** (mis. fixture; tanpa penanda): worktree dari branch
  integrasi (`worktree-new.sh tests <id-QA> $0`), tanpa menunggu item lain.

## Langkah 5 — Review dan merge per item

- `scrum-kit:code-reviewer` untuk tiap item (basis diff `origin/<branch.integrasi>`);
  `scrum-kit:security-auditor` bila item menyentuh autentikasi, data pribadi, atau berkas unggahan.
  Temuan dikirim ke agen pemilik; ulangi sampai BERSIH. Perbaikan butuh keputusan di luar cakupan atau
  wilayah item → tandai item terblokir, tanya manusia sekali beserta opsinya, lanjutkan item lain, dan
  cantumkan di ringkasan.
- Satu MR per item → branch integrasi, dibuka sebagai draft dari branch QA (memuat commit
  implementasinya); branch implementasi tidak mendapat MR sendiri. Backlog dengan item QA sendiri
  (Langkah 4):
  - (a) MR dari branch item QA itu sendiri. Item yang diuji ikut di MR itu (commitnya ada di branch
    QA) dan tidak mendapat MR sendiri; deskripsi MR menyebut kedua ID.
  - (b) MR dari branch item implementasi itu sendiri, dengan catatan terlihat **"tanpa item QA"** di
    judul dan di awal deskripsi MR. Butir pengujian di checklist DoD tidak dicentang, tetapi ditandai
    "tanpa item QA".
  - (c) MR dari branch item QA itu sendiri.

  Tandai siap hanya bila review
  BERSIH dan CI pada SHA HEAD sukses ("Cara merge"); merah = berhenti, baca log job, jangan menumpuk
  MR di atasnya, tidak ada "merah yang diharapkan".
- Butir DoD yang ditandai "tidak berlaku" oleh peran atau peninjau: ikuti
  `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Butir DoD tidak berlaku selama sprint" (diterima
  bila ada di himpunan langkah 0.3, selain itu tanya product owner sekali). Butir yang "menunggu
  persetujuan product owner" tidak dicentang dan tidak dihitung terpenuhi; item tetap merge ke branch
  integrasi hanya bila semua butir DoD lainnya terpenuhi.
- Merge **hanya lewat MR** (`--no-ff`, satu merge commit per item); centang checklist DoD di deskripsi
  sebelum merge; sesudahnya bersihkan branch item ("Cara merge").

## Langkah 6 — Penutup

1. `api-contract-keeper` sekali lagi: kontrak = kode yang benar-benar ada.
2. Tulis `<dokumen.laporan>/ringkasan.md`: goal, item selesai/tidak (alasannya), item terblokir,
   item yang merge "tanpa item QA",
   worktree dan branch item yang belum merge, story point, temuan terbuka, impediment. Perbarui
   `dokumen.serah_terima` dan `dokumen.code_debt`, lalu commit ringkasan, putusan review yang disimpan,
   serah terima, dan code debt di branch integrasi, dan push.
   Ada persetujuan butir DoD yang tertunda → cantumkan setiap persetujuan itu (item, butir, alasan) di
   ringkasan dan di serah terima (bagian "Menunggu pihak lain"), lalu berhenti di sini: tanpa merge
   branch integrasi ke basis, langsung ke langkah 5, dan laporkan bahwa merge akhir menunggu product
   owner. Sesudah product owner menyetujui semuanya, lanjutkan dari langkah 3.
3. Hanya bila minimal satu item sudah merge: **SATU** MR draft branch integrasi → `branch.basis`, isi
   dari templat MR proyek. Tidak ada item yang merge → tanpa MR integrasi; laporkan. Setelah merge,
   pekerjaan baru masuk backlog sprint berikutnya, bukan MR susulan dari branch integrasi.
4. Sesudah merge: sinkron dokumentasi turunan (koleksi Postman, portal dokumentasi) bila proyek
   punya targetnya; jangan sebelum merge.
5. Laporkan ke manusia: status MR + pipeline, temuan terbuka, keputusan yang dibutuhkan; susun temuan
   yang belum jadi backlog sebagai "kandidat sprint berikutnya" atau "perlu perubahan mendesak"
   (wajib beralasan cacat kritis).
6. Worktree dan branch item yang belum merge tetap disimpan (tercantum di ringkasan).

## Aturan

- Jangan merge MR ke `branch.basis` tanpa persetujuan manusia (pengecualian tertulis: hotfix jalur biasa
  dan back-merge di `/scrum-kit:hotfix`); jangan pernah push langsung ke basis
  maupun `branch.rilis`; jangan membuka MR ke `branch.rilis` tanpa diminta (itu tugas `/scrum-kit:rilis`).
- Jangan pernah merge ke `branch.basis` selama ada persetujuan butir DoD "tidak berlaku" yang tertunda.
- Jangan membuat worktree sebelum langkah 0.4 lulus: peran tidak pernah mulai dari backlog yang belum
  ter-commit.
- Jangan menonaktifkan/melewati test merah; akar masalahnya yang diperbaiki.
- Agen yang melapor selesai tanpa keluaran gate → kembalikan.
