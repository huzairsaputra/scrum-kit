---
description: Orkestrasi satu sprint — sinkron spesifikasi, fondasi, kontrak, implementasi paralel, QA, review, lalu satu MR integrasi ke branch basis
argument-hint: "<nomor-sprint>"
---

# Orkestrasi Sprint $0

Kamu adalah orkestrator (Scrum Master). Kamu **tidak menulis kode aplikasi**; kamu membagi kerja ke
agen plugin (`scrum-kit:<agen>`) lewat CLI headless (lihat "Cara mendispatch agen"), menjaga barrier,
dan menyiapkan branch serta MR.

## Cara mendispatch agen

Setiap kali langkah di bawah menyebut agen `scrum-kit:<agen>`, jalankan agen itu sebagai proses
Claude Code CLI terpisah, **bukan** lewat tool Agent/subagen:

- Lewat Bash dengan `run_in_background`, dari dalam worktree item:
  `cd <worktree> && claude -p --agent scrum-kit:<agen> --permission-mode auto "<prompt>"`.
  Prompt panjang atau berisi tanda kutip: tulis ke berkas di scratchpad, lalu
  `cd <worktree> && claude -p --agent scrum-kit:<agen> --permission-mode auto < <berkas-prompt>`.
- Hasil agen dibaca dari keluaran perintah itu (kamu diberi tahu saat prosesnya selesai; jangan
  polling). Laporan tanpa keluaran gate diperlakukan sama seperti agen yang belum selesai.
- CLI terkena batas pemakaian (*usage/session limit*) atau gagal → Anthropic API. Tool Agent/subagen
  hanya dipakai bila CLI dan Anthropic API sama-sama habis atau gagal, atau bila pengguna memintanya
  di sesi ini. Bila sudah terlanjur memakai subagen, laporkan ke pengguna dan pindah ke CLI.
- `claude -p` tidak bisa memberi persetujuan tulis `.claude/**`. Agen (terutama `platform-tooling`)
  yang perlu mengubah berkas di `.claude/` menulis berkas lain dulu, lalu melaporkan isi utuh berkas
  `.claude/` itu; kamu yang menulisnya di sesi interaktif (dengan persetujuan) dan meng-commit-nya.

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
2. `gate.ci` hijau di basis. Merah → serahkan ke `scrum-kit:platform-tooling` lebih dulu.
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

## Langkah 4 — Pengujian

Begitu build sebuah modul hijau, `scrum-kit:qa-test-engineer` untuk modul itu
(`worktree-new.sh tests <id> $0 --modul=<m>`), di atas branch implementasinya. Tidak perlu menunggu
modul lain.

## Langkah 5 — Review dan merge per item

- `scrum-kit:code-reviewer` untuk tiap item; `scrum-kit:security-auditor` bila item menyentuh
  autentikasi, data pribadi, atau berkas unggahan. Temuan dikirim ke agen pemilik; ulangi sampai BERSIH.
- MR item → branch integrasi. **Pipeline MR harus hijau pada HEAD** sebelum merge; merah = berhenti,
  baca log job, jangan menumpuk MR di atasnya, tidak ada "merah yang diharapkan".
- Implementasi yang sengaja membuat test lama merah tidak dibuka sebagai MR sendiri: MR dibuka dari
  branch QA yang memuat implementasinya.
- Merge **hanya lewat MR** (`--no-ff`, satu merge commit per item); lepas status draft dulu; centang
  checklist DoD di deskripsi sebelum merge.

## Langkah 6 — Penutup

1. `api-contract-keeper` sekali lagi: kontrak = kode yang benar-benar ada.
2. Tulis `<dokumen.laporan>/ringkasan.md`: goal, item selesai/tidak (alasannya), story point,
   temuan terbuka, impediment.
3. **SATU** MR draft branch integrasi → `branch.basis`, isi dari templat MR proyek. Setelah merge,
   pekerjaan baru masuk backlog sprint berikutnya, bukan MR susulan dari branch integrasi.
4. Sesudah merge: sinkron dokumentasi turunan (koleksi Postman, portal dokumentasi) bila proyek
   punya targetnya; jangan sebelum merge.
5. Laporkan ke manusia: status MR + pipeline, temuan terbuka, keputusan yang dibutuhkan; susun temuan
   yang belum jadi backlog sebagai "kandidat sprint berikutnya" atau "perlu perubahan mendesak"
   (wajib beralasan cacat kritis).
6. Perbarui `dokumen.serah_terima` dan `dokumen.code_debt`; bersihkan worktree dan branch item.

## Aturan

- Jangan merge MR ke `branch.basis` tanpa persetujuan manusia; jangan pernah push langsung ke basis
  maupun `branch.rilis`; jangan membuka MR ke `branch.rilis` tanpa diminta (itu tugas `/scrum-kit:rilis`).
- Jangan menonaktifkan/melewati test merah; akar masalahnya yang diperbaiki.
- Agen yang melapor selesai tanpa keluaran gate → kembalikan.
