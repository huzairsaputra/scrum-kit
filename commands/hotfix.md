---
description: Perubahan di luar sprint — jalur biasa (perubahan kecil atas persetujuan PO ke branch basis) atau jalur darurat (perbaikan mendesak ke produksi tanpa downtime, lalu back-merge)
argument-hint: "<ID> <deskripsi singkat>"
---

# Hotfix $0

Deskripsi: $ARGUMENTS

Pola ini untuk perubahan yang tidak menunggu sprint (keputusan PO tertulis di chat). Kamu
orkestrator: tidak menulis kode aplikasi sendiri. Baca `CLAUDE.md` dan `.claude/kit.json` dulu;
nomor sprint = sprint berjalan (tanya bila tidak jelas dari `dokumen.serah_terima`).

**Cara mendispatch agen**: baca `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian "Mendispatch
agen" dan ikuti.

## Pilih jalur dulu

- **Darurat** (hotfix sebenarnya): produksi mati atau terganggu berat, celah keamanan terbuka atau
  sedang dieksploitasi, atau data sedang rusak/bocor, **dan** tidak bisa menunggu rilis terjadwal.
  Tujuan MR = `branch.rilis`, atau `branch.basis` bila `branch.rilis` kosong (produksi di-deploy dari
  basis). Konfirmasi jalur ini ke PO dengan satu AskUserQuestion sebelum mulai.
- **Biasa**: perubahan kecil atas keputusan PO (termasuk fitur kecil) yang boleh menunggu deploy basis.
  Tujuan MR = `branch.basis`.
- Bug yang bisa menunggu jadwal rilis bukan hotfix: masukkan ke backlog sprint (coldfix), lalu ikut
  `/scrum-kit:rilis`.

Langkah 1–8 berlaku untuk kedua jalur; `<tujuan>` = tujuan MR jalur yang dipilih. Setiap worktree
dibuat dari `<tujuan>`, bukan dari branch integrasi sprint:
`scripts/kit/worktree-new.sh <wilayah> <id> <n> --base=origin/<tujuan>` (tanpa `--base`, skrip itu
bercabang dari integrasi sprint berjalan dan pekerjaan sprint yang belum selesai ikut terbawa).

**Cara merge** (langkah 7 dan back-merge): baca `${CLAUDE_PLUGIN_ROOT}/docs/alur-bersama.md` bagian
"Cara merge" dan ikuti.

## Langkah

1. **Spesifikasi.** Tulis spesifikasi singkat ke scratchpad: perilaku yang diminta, modul tersentuh,
   endpoint/skema, kasus negatif, hal yang TIDAK berubah. Ambiguitas yang menentukan desain → satu
   AskUserQuestion; sisanya pakai default yang masuk akal dan catat.
2. **Kontrak** (bila ada endpoint): `scrum-kit:api-contract-keeper` di worktree `contract`, catatan
   rilis ikut diperbarui.
3. **Implementasi** paralel per wilayah: `shared-module-owner` (skema/bersama) lebih dulu bila
   dibutuhkan modul lain, lalu `module-dev` per modul. Tiap agen menjalankan gate fmt/lint/build.
4. **QA** per modul: `qa-test-engineer` di worktree `tests --modul=<m>` yang sudah memuat merge
   kontrak + implementasi; suite penuh modul itu hijau; tanpa `skip`.
5. **Review**: `code-reviewer` atas seluruh diff (basis diff `origin/<tujuan>`). Temuan → agen pemilik → QA ulang + review ulang
   sampai BERSIH. Risiko yang sengaja diterima PO dicatat di `dokumen.code_debt`.
6. **Integrasi**: worktree baru dari `origin/<tujuan>`, merge semua branch (versi kontrak
   terakhir harus menang — periksa `git diff <branch-kontrak> HEAD -- <kontrak>` kosong), `gate.ci`
   hijau, perbarui `dokumen.serah_terima` dan laporan review.
7. **MR** ke `<tujuan>` dengan templat proyek dan bukti gate. Tunggu CI sukses pada SHA HEAD (lihat
   "Cara merge") dan centang checklist DoD. Merge:
   - jalur biasa: keputusan PO yang memulai hotfix ini adalah persetujuan merge ke basis (pengecualian
     tertulis atas aturan `/scrum-kit:sprint`), selama cakupan tidak melebar dari keputusan itu;
     cakupan melebar → minta persetujuan ulang;
   - jalur darurat: hanya atas persetujuan PO di chat untuk MR itu, walau semua gate hijau.
8. **Pasca-merge**: pantau pipeline `<tujuan>` sampai deploy (bila ada job migrasi, pastikan lognya
   melaporkan sukses), sinkron dokumentasi turunan, bersihkan worktree dan branch (lihat "Cara merge"), siapkan teks pemberitahuan
   singkat untuk tim klien (FE/mobile) bila kontrak berubah.

## Jalur darurat: aturan tambahan

- **Cakupan minimal**: hanya akar masalah insiden itu. Tanpa fitur, refactor, atau upgrade dependensi;
  temuan lain masuk backlog.
- **Test regresi wajib**: `qa-test-engineer` menulis test yang mereproduksi insiden. Bukti merah
  sebelum perbaikan dan hijau sesudahnya ditempel di laporan, plus suite penuh modul yang tersentuh.
- **Tanpa downtime**: migrasi hanya aditif dan kompatibel mundur: tabel baru, kolom nullable, atau
  indeks yang dibuat tanpa mengunci tabel (mis. `CREATE INDEX CONCURRENTLY` di PostgreSQL,
  `ALGORITHM=INPLACE, LOCK=NONE` di MySQL/MariaDB). Drop, rename, ubah tipe, atau apa pun yang butuh
  restart terjadwal → bukan hotfix: berhenti, beri tahu PO bahwa jalur rilis terjadwal
  (`/scrum-kit:rilis`) membawa seluruh isi basis, dan biarkan PO memutuskan.
- **Review**: `code-reviewer`, ditambah `security-auditor` bila insidennya menyangkut keamanan.
- **Back-merge** bila `<tujuan>` ≠ `branch.basis`: branch `claude/backmerge-$0` dari
  `origin/<branch.basis>`, merge `origin/<tujuan>` (merge commit), MR ke basis. Isinya sudah disetujui
  di langkah 7, jadi MR ini boleh di-merge begitu pipeline hijau. Ada konflik → berhenti dan laporkan
  ke manusia beserta berkas yang konflik; jangan menyelesaikannya sendiri. Tanpa back-merge, perbaikan
  hilang di rilis berikutnya.
- **Tag**: bila proyek memberi tag rilis, naikkan versi patch dari tag terakhir di `<tujuan>`
  (`git describe --tags --abbrev=0 origin/<tujuan>`, format tag mengikuti yang sudah ada), beri tag
  beranotasi pada merge commit di `<tujuan>`, lalu push tag itu.
- **Serah terima**: perbarui baris "Rilis produksi terakhir" (versi, MR, SHA, tanggal).
- **Kajian pascainsiden** di `<dokumen.laporan>/hotfix-$0.md`: kronologi, dampak, akar masalah,
  perbaikan, dan pencegahan. Langkah pencegahan masuk backlog atau `dokumen.code_debt`.

Berhenti dan laporkan bila pipeline merah, review menemukan BLOKER yang mengubah keputusan PO, atau
perubahan ternyata menyentuh wilayah DevOps/infra (usulkan lewat issue, jangan ubah).
