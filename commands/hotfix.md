---
description: Perubahan kecil atas persetujuan PO langsung ke branch basis — kontrak, implementasi, QA, review, satu MR, sinkron dokumentasi, beres-beres
argument-hint: "<ID> <deskripsi singkat>"
---

# Hotfix $0

Deskripsi: $ARGUMENTS

Pola ini untuk perubahan kecil yang tidak menunggu sprint (keputusan PO tertulis di chat). Kamu
orkestrator: tidak menulis kode aplikasi sendiri. Baca `CLAUDE.md` dan `.claude/kit.json` dulu;
nomor sprint = sprint berjalan (tanya bila tidak jelas dari `dokumen.serah_terima`).

**Cara mendispatch agen.** Setiap agen di bawah (`scrum-kit:<agen>`) dijalankan sebagai proses Claude
Code CLI terpisah, **bukan** lewat tool Agent/subagen:

- Lewat Bash dengan `run_in_background`, dari dalam worktree item:
  `cd <worktree> && claude -p --agent scrum-kit:<agen> --permission-mode auto "<prompt>"`.
  Prompt panjang atau berisi tanda kutip: tulis ke berkas di scratchpad, lalu
  `cd <worktree> && claude -p --agent scrum-kit:<agen> --permission-mode auto < <berkas-prompt>`.
- Hasil agen dibaca dari keluaran perintah itu (kamu diberi tahu saat prosesnya selesai; jangan
  polling). Laporan tanpa keluaran gate = belum selesai, kembalikan.
- CLI terkena batas pemakaian atau gagal → Anthropic API. Tool Agent/subagen hanya dipakai bila CLI
  dan Anthropic API sama-sama habis atau gagal, atau bila pengguna memintanya di sesi ini.
- `claude -p` tidak bisa memberi persetujuan tulis `.claude/**`. Agen yang perlu mengubah berkas di
  `.claude/` melaporkan isi utuh berkas itu; kamu yang menulisnya di sesi interaktif dan meng-commit-nya.

1. **Spesifikasi.** Tulis spesifikasi singkat ke scratchpad: perilaku yang diminta, modul tersentuh,
   endpoint/skema, kasus negatif, hal yang TIDAK berubah. Ambiguitas yang menentukan desain → satu
   AskUserQuestion; sisanya pakai default yang masuk akal dan catat.
2. **Kontrak** (bila ada endpoint): `scrum-kit:api-contract-keeper` di worktree `contract`, catatan
   rilis ikut diperbarui.
3. **Implementasi** paralel per wilayah: `shared-module-owner` (skema/bersama) lebih dulu bila
   dibutuhkan modul lain, lalu `module-dev` per modul. Tiap agen menjalankan gate fmt/lint/build.
4. **QA** per modul: `qa-test-engineer` di worktree `tests --modul=<m>` yang sudah memuat merge
   kontrak + implementasi; suite penuh modul itu hijau; tanpa `skip`.
5. **Review**: `code-reviewer` atas seluruh diff. Temuan → agen pemilik → QA ulang + review ulang
   sampai BERSIH. Risiko yang sengaja diterima PO dicatat di `dokumen.code_debt`.
6. **Integrasi**: worktree baru dari `origin/<branch.basis>`, merge semua branch (versi kontrak
   terakhir harus menang — periksa `git diff <branch-kontrak> HEAD -- <kontrak>` kosong), `gate.ci`
   hijau, perbarui `dokumen.serah_terima` dan laporan review.
7. **MR** ke `branch.basis` dengan templat proyek dan bukti gate. Tunggu pipeline hijau pada HEAD,
   centang checklist DoD, pastikan status merge "mergeable", merge dengan SHA HEAD.
8. **Pasca-merge**: pantau pipeline basis sampai deploy (bila ada job migrasi, pastikan lognya
   melaporkan sukses), sinkron dokumentasi turunan, hapus worktree + branch, siapkan teks pemberitahuan
   singkat untuk tim klien (FE/mobile) bila kontrak berubah.

Berhenti dan laporkan bila pipeline merah, review menemukan BLOKER yang mengubah keputusan PO, atau
perubahan ternyata menyentuh wilayah DevOps/infra (usulkan lewat issue, jangan ubah).
