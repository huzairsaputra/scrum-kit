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
3. `git fetch origin`; buat branch integrasi dari `origin/<branch.basis>` bila belum ada, push.
4. Kelompokkan item menurut wilayah pemiliknya (`wilayah.*.agen`).

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
modul lain.

## Langkah 5 — Review dan merge per item

- `scrum-kit:code-reviewer` untuk tiap item (basis diff `origin/<branch.integrasi>`);
  `scrum-kit:security-auditor` bila item menyentuh autentikasi, data pribadi, atau berkas unggahan.
  Temuan dikirim ke agen pemilik; ulangi sampai BERSIH. Perbaikan butuh keputusan di luar cakupan atau
  wilayah item → tandai item terblokir, tanya manusia sekali beserta opsinya, lanjutkan item lain, dan
  cantumkan di ringkasan.
- Satu MR per item → branch integrasi, dibuka sebagai draft dari branch QA (memuat commit
  implementasinya); branch implementasi tidak mendapat MR sendiri. Tandai siap hanya bila review
  BERSIH dan CI pada SHA HEAD sukses ("Cara merge"); merah = berhenti, baca log job, jangan menumpuk
  MR di atasnya, tidak ada "merah yang diharapkan".
- Merge **hanya lewat MR** (`--no-ff`, satu merge commit per item); centang checklist DoD di deskripsi
  sebelum merge; sesudahnya bersihkan branch item ("Cara merge").

## Langkah 6 — Penutup

1. `api-contract-keeper` sekali lagi: kontrak = kode yang benar-benar ada.
2. Tulis `<dokumen.laporan>/ringkasan.md`: goal, item selesai/tidak (alasannya), item terblokir,
   worktree dan branch item yang belum merge, story point, temuan terbuka, impediment. Perbarui
   `dokumen.serah_terima` dan `dokumen.code_debt`, lalu commit ringkasan, putusan review yang disimpan,
   serah terima, dan code debt di branch integrasi, dan push.
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
- Jangan menonaktifkan/melewati test merah; akar masalahnya yang diperbaiki.
- Agen yang melapor selesai tanpa keluaran gate → kembalikan.
