# CLAUDE.md — {{proyek}}

Panduan kerja untuk Claude Code dan seluruh subagen di repositori ini. Berkas ini sumber kebenaran
aturan kerja; konfigurasi mesin-baca ada di `.claude/kit.json` (dibaca hook, skrip, dan agen plugin
`scrum-kit`). Bila keduanya berbeda, `kit.json` yang menang untuk wilayah dan gate, berkas
ini untuk aturan.

## 1. Bentuk repositori

{{ringkasan_struktur}}
<!-- /kit-init: tabel modul (direktori, stack, peran) + catatan basis data/infra yang dipakai bersama. -->

## 2. Perintah

Selalu lewat perintah gate di `kit.json` — jangan menghafal perintah lepas:

| Gate | Perintah |
|---|---|
{{tabel_gate}}

{{catatan_penyiapan}}
<!-- /kit-init: langkah penyiapan pertama (env uji, basis data uji, kunci) bila ada. -->

### Kebiasaan kerja agen

- **Urutan sesi: Claude Code CLI → Anthropic API → Claude Desktop sebagai orkestrator.** Claude Desktop
  menjadi orkestrator tetap: ia membagi pekerjaan, menjaga gate, membuka MR, dan memperbarui serah terima.
  Pekerjaan berat dikerjakan **Claude Code CLI** (`claude -p` headless atau sesi interaktif). Bila CLI
  mencapai batas pemakaian, pindah ke **Anthropic API**: Message Batches API untuk pekerjaan yang tidak
  mendesak (hemat 50%, hasil asinkron sampai 24 jam), Messages API biasa untuk yang menahan merge. Desktop
  baru mengerjakan sendiri bila keduanya habis. Sebelum berhenti karena batas, perbarui serah terima.
- **Eksplorasi kode: graphify dulu, bila tersedia.** Bila perintah `graphify` jalan dan proyek punya
  `graphify-out/graph.json`, jawab pertanyaan struktural (siapa memanggil X, jalur A→B) lewat
  `graphify explain "Simbol()"` / `graphify path "A" "B"`, lalu buka hanya file:baris yang ditunjuk.
  `grep` untuk teks persis. Segarkan di awal sesi dan sesudah merge: `graphify update .` untuk kode (AST,
  tanpa LLM); bila dokumen ikut berubah (`graphify check-update .`), `/graphify . --update`, yang memakai
  backend LLM untuk dokumen yang berubah saja, dengan urutan Gemini API → Anthropic API → `--backend
  claude-cli` → sesi host sendiri (tidak pernah subagen). Edge INFERRED diverifikasi di file dulu. Bila graphify tidak tersedia, langsung pakai
  grep/Read.
- **Urutan backend LLM untuk SEMUA skrip (graphify, sinkron Scalar, skrip baru):** Gemini API
  (`GEMINI_API_KEY`) → Anthropic API (`ANTHROPIC_API_KEY`, model `claude-opus-5-5`, key terikat workspace)
  → CLI `claude` → sesi Claude Desktop. Lanjut ke langkah berikutnya bila key tidak ada atau panggilan
  gagal (kredensial, kuota, kredit habis, penolakan). Skrip baru tidak menulis ulang urutan ini, melainkan
  mengimpor `scripts/panggil_llm.py` dari scrum-kit (`panggil_llm(prompt, sistem)` → `(teks, backend)`).
  Key dibaca dari environment dan tidak pernah dicetak atau ditulis ke repo.
- **Test lokal hemat CPU.** Selama iterasi dan di setiap putaran review: gate cepat + hanya test yang
  terkait (filter nama test). Suite penuh modul yang tersentuh **sekali**, sesudah perubahan kode
  terakhir dan sebelum merge, dijalankan serial; jangan dua suite penuh bersamaan. Basis data uji dibuat
  ulang hanya bila migrasi berubah.
- **Bukti gate di setiap review.** Lampirkan SHA HEAD yang diuji, perintah gate, dan hasil suite saat
  meminta review, dan pastikan HEAD yang direview sama dengan HEAD yang diuji.

## 3. Aturan keras

1. **Satu wilayah satu pemilik.** Agen hanya menulis di wilayahnya (`kit.json` → `wilayah`). Hook
   `PreToolUse` plugin menolak Write/Edit di luar wilayah berdasarkan nama branch.
2. **Implementer tidak menulis test; QA tidak menulis kode non-test.**
3. **Jangan pernah commit `.env`** atau rahasia apa pun. Hanya contoh env (`.env.example`) yang masuk git.
4. **Jangan push langsung ke `{{basis}}`{{rilis_teks}}.** Pekerjaan mengalir lewat Merge Request.
5. **Pipeline MR harus hijau pada commit HEAD sebelum merge.** Gate lokal tidak menggantikannya;
   pipeline merah = berhenti dan baca log job-nya. Pengecualian: repo tanpa remote (mode lokal
   `/scrum-kit:sprint`, `/scrum-kit:hotfix`, `/scrum-kit:rilis`) tidak punya MR maupun pipeline; di
   sana `gate.ci` lokal yang hijau pada HEAD menjadi syaratnya, dan merge lokal ke `{{basis}}`{{rilis_teks}}
   hanya atas persetujuan product owner.
6. **Dependensi berpenulis tunggal:** hanya pemilik modul yang mengubah berkas dependensi modul itu.
{{aturan_tambahan}}

## 4. Konvensi

- Bahasa commit message, judul/isi MR, komentar, dan dokumentasi: {{bahasa}}.
- Istilah domain mengikuti bahasa pemangku kepentingan; nama teknis mengikuti konvensi stack.
- Validasi input dan otorisasi mengikuti pola framework (tidak bertebaran di controller).
{{konvensi_stack}}

## 5. Wilayah kepemilikan dan branch

Format branch wilayah: `{{pola_wilayah}}`. Branch integrasi sprint: `{{pola_integrasi}}`.

| Wilayah | Agen | Boleh menulis | Kecuali |
|---|---|---|---|
{{tabel_wilayah}}

Branch di luar pola wilayah (`{{basis}}`, `{{rilis}}`, integrasi, `claude/*`) tidak dibatasi hook —
itu wilayah manusia dan orkestrator. Worktree agen dibuat dengan
`scripts/kit/worktree-new.sh <wilayah> <id-item> <nomor-sprint>`.

## 6. Definition of Done

Sebuah item selesai bila **semuanya** benar:

1. Gate fmt/lint/build/test/dod untuk modul itu hijau (perintah di §2).
2. Perilaku baru diuji, termasuk minimal satu kasus negatif otorisasi; data milik pengguna tidak
   dapat diakses pengguna lain.
3. Endpoint/kontrak publik terdokumentasi{{kontrak_teks}}.
4. Ditinjau `code-reviewer` sampai BERSIH.
5. MR dengan checklist DoD tercentang, pipeline MR hijau pada HEAD (mode lokal: checklist di laporan
   item dan `gate.ci` lokal hijau, lihat aturan keras 5).

Butir yang tidak berlaku untuk sebuah item (mis. uji negatif otorisasi di proyek tanpa login) boleh
ditandai "tidak berlaku" hanya bila alasannya tertulis di dokumen serah terima sprint
(`{{serah_terima}}`, bagian "Butir DoD tidak berlaku") dan disetujui product owner. Tidak pernah
diam-diam. Persetujuan itu datang dari kolom `Butir DoD tidak berlaku (disetujui):` di blok
persetujuan laporan kesiapan backlog sprint (hanya bila blok itu terisi dan laporannya tidak usang),
atau dari product owner di chat. Selama belum disetujui, butir itu "menunggu persetujuan product
owner" dan tidak dihitung terpenuhi: item boleh merge ke branch integrasi bila semua butir lain
terpenuhi, tetapi branch integrasi tidak di-merge ke `{{basis}}` sampai product owner menyetujui.

Dokumentasi API publik di kode (fungsi, kelas, modul) ditulis implementer modul sebagai docstring di
kode wilayahnya. Perubahan README adalah item terpisah milik wilayah tooling (`platform-tooling`),
bukan bagian item implementasi; implementer yang melihat README perlu berubah mencatatnya sebagai
temuan. Dengan begitu butir 3 tidak pernah meminta implementer menulis di luar wilayahnya.

## 7. Otomasi

- `/scrum-kit:sprint <n>` — orkestrasi satu sprint (backlog di `{{backlog}}`).
- `/scrum-kit:hotfix <id> <deskripsi>` — perubahan di luar sprint dengan alur kontrak →
  implementasi → QA → review → MR: jalur biasa ke `{{basis}}`, atau jalur darurat ke produksi
  (perbaikan mendesak tanpa downtime, lalu back-merge).
- `/scrum-kit:rilis [versi] [jadwal]` — rilis terjadwal `{{basis}}` → produksi, merge atas
  persetujuan PO.
- Laporan agen: `{{laporan}}<nama-agen>-<id-item>.md` (`<id-item>` = ID item dari prompt
  orkestrator, bagian `{id}` branch wilayah; satu berkas per item agar agen paralel tidak bentrok).
  Serah terima: `{{serah_terima}}`.
