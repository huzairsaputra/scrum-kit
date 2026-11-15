# Rancangan: pemilik agen (`pemilik`) di scrum-kit 1.6.0

Status: **draf untuk keputusan PO** (15 Nov 2026). Belum ada kode. Ditulis baru untuk scrum-kit (MIT); tidak menyalin Versi bahasa Inggris: [pemilik-agen.md](pemilik-agen.md).
teks atau kode dari produk lain.

## 1. Tujuan

Setiap wilayah agen (`wilayah.<nama>`) punya **satu manusia pemilik** dengan akun forge. Pemilik meninjau dan
menyetujui MR di wilayahnya, menerima eskalasi agen wilayah itu, dan namanya tercatat di backlog. Sumber datanya adalah
**Form Pemilik Agen** (satu baris per posisi: posisi, nama, akun forge, wilayah yang dipegang, siapa yang disetujui).

Batas yang disengaja (dari uji form 11 Nov):

- Berlaku **per repositori**. Proyek empat repo = empat `kit.json`; satu orang boleh muncul di beberapa repo.
  Persetujuan lintas repo (mis. kontrak API yang menyentuh backend dan frontend) di luar jangkauan, dan ditulis begitu.
- Pemetaan berubah lewat **serah terima** (satu blok yang diperbarui, peristiwanya dicatat di serah terima), bukan blok
  per periode.
- Orkestrator tetap **satu orang**; merge akhir oleh orkestrator atau PO.

## 2. Bentuk di `kit.json`

```json
"pemilik": {
  "backend-admin":  { "nama": "Nama A", "akun_forge": "user-a", "wilayah": ["admin"] },
  "backend-mobile": { "nama": "Nama B", "akun_forge": "user-b", "wilayah": ["mobile", "bersama"] },
  "devops":         { "nama": "Nama C", "akun_forge": "user-c", "wilayah": ["tooling", "skema"] }
},
"persetujuan_pemilik": "peringatan"
```

| Kunci | Wajib | Arti |
|---|---|---|
| `pemilik.<posisi>` | tidak | Satu posisi tim. Nama posisi bebas (bukan nama orang), dipakai di backlog: `module-dev (backend-admin)`. |
| `.nama` | ya | Nama yang ditampilkan di MR dan laporan. |
| `.akun_forge` | ya | Username GitLab/GitHub; dipakai sebagai reviewer MR dan di CODEOWNERS. |
| `.wilayah` | ya | Daftar nama wilayah dari `wilayah.*` (atau nama modul bila wilayah `per_modul`). |
| `persetujuan_pemilik` | tidak | `peringatan` (bawaan) atau `wajib`. Lihat bagian 4. |

Tanpa `pemilik`, scrum-kit bekerja persis seperti 1.5.0.

**Validasi** (`/kit-init` dan `worktree-new.sh`, pesan berbahasa Indonesia):

- satu wilayah dipegang dua posisi → **ditolak**, kecuali saat serah terima tercatat (bagian 5);
- wilayah yang tidak ada di `wilayah.*` → ditolak;
- wilayah tanpa pemilik → **peringatan**, tidak menghalangi;
- `akun_forge` kosong atau sama untuk dua posisi → peringatan (tim kecil boleh satu orang dua posisi, tapi ia tidak
  boleh menyetujui MR buatannya sendiri).

## 3. Alur sprint

1. **Backlog:** kolom pemilik item ditulis `agen (posisi)` sebelum backlog ditandatangani (sidik backlog tetap utuh).
   Item yang ditugaskan sesudah tanda tangan dicatat di serah terima, bukan di backlog.
2. **Awal sprint:** bila belum ada, `/sprint` **mengusulkan** blok CODEOWNERS dari `pemilik` (GitLab:
   `.gitlab/CODEOWNERS` atau `CODEOWNERS`; GitHub: `.github/CODEOWNERS`), satu pola path per baris dari glob `tulis`
   wilayah itu. Manusia yang menyetujui dan mengomitnya; agen tidak mengubah CODEOWNERS sendiri.
3. **MR item:** pemilik wilayah dijadikan reviewer MR; deskripsi MR menyebut posisinya.
4. **Merge:** lihat bagian 4. Penulis MR tidak pernah dihitung sebagai penyetuju; bila pemilik adalah penulisnya,
   persetujuan datang dari pemilik lain atau PO.

## 4. Persetujuan

Sama untuk semua forge (GitLab, GitHub). Sebelum merge, orkestrator membaca persetujuan MR lewat forge (MCP GitLab atau
`gh`) dan memeriksa bahwa pemilik wilayah, bukan penulis MR, sudah menyetujui.

- `peringatan` (bawaan): bila persetujuan pemilik belum ada, merge tetap boleh, dan peringatannya tercatat di MR dan
  laporan sprint.
- `wajib`: orkestrator **menahan** merge sampai pemilik menyetujui; bila pemilik tidak tersedia, PO yang menyetujui dan
  alasannya dicatat.

Bila forge proyek juga menegakkan aturan pemilik kode (CODEOWNERS dengan persetujuan wajib), aturan itu berlaku di
samping pemeriksaan scrum-kit; scrum-kit tidak bergantung padanya.

## 5. Serah terima

Saat pemilik berganti (pindah proyek, cuti panjang):

- blok `pemilik` diperbarui, dan peristiwanya (tanggal, posisi, dari siapa ke siapa, wilayah) dicatat di
  `serah-terima.md`;
- masa peralihan: dua posisi boleh memegang wilayah yang sama **hanya** bila serah terima itu tercatat;
- item terbuka milik pemilik lama **kembali ke backlog** sampai wilayahnya dipegang ulang secara tertulis.

## 6. Perubahan berkas

`docs/kit-json.md`, `commands/kit-init.md`, `commands/sprint.md`, `commands/hotfix.md` (persetujuan pemilik untuk
hotfix), `templates/backlog.md`, `templates/serah-terima.md`, `templates/merge_request.md`, `scripts/worktree-new.sh`
(validasi), `CHANGELOG.md`, `README.md`/`README.id.md`. Uji: kit contoh dengan dan tanpa `pemilik`, wilayah ganda,
wilayah tak dikenal, wilayah tanpa pemilik.

## 7. Keputusan PO

1. Nama kunci `pemilik` dan `persetujuan_pemilik`, bawaan `peringatan`?
2. Masuk scrum-kit 1.6.0 (freeze 15 Des, rilis 22 Des) bersama tambalan mode jalan dan opsi merge?
3. Pilot: satu repo, satu sprint, sebelum keempat repo.
