# Partisipasi riset: disclaimer, pernyataan persetujuan, dan laporan (draf)

Status: **draf untuk ditinjau PO** (15 Nov 2026). Berlaku untuk semua pengguna scrum-kit: perorangan, tim, instansi
pemerintah, dan perusahaan swasta. Versi bahasa Inggris: [persetujuan-riset.md](persetujuan-riset.md). Isian dalam
`[kurung]` dilengkapi sesudah persetujuan etik keluar; **tidak ada yang dipublikasikan sebelum itu**. Ini bukan nasihat
hukum; teks akhir diperiksa terhadap ketentuan etik kampus dan UU Pelindungan Data Pribadi (UU 27/2022).

Keputusan (15 Nov 2026): kiriman lewat **formulir issue GitHub** di repositori ini; kiriman mentah disimpan **5 tahun**;
urusan privat lewat kanal pelaporan privat GitHub, penarikan lewat issue itu sendiri.

## A. Disclaimer untuk README

> **Riset (opsional).** scrum-kit tidak mengirim apa pun ke mana pun: tanpa telemetri, tanpa laporan otomatis.
> scrum-kit juga bagian dari penelitian doktoral tentang alur kerja terstruktur berbasis spesifikasi untuk agen
> pengode AI. Bila ingin membantu, jalankan `scripts/laporan-riset.py` sesudah sprint. Skrip itu menulis berkas lokal
> pendek berisi angka saja, tidak pernah kode, nama repositori, teks backlog, nama orang, atau rahasia. Baca, sunting,
> lalu kirim sendiri lewat formulir issue **Laporan riset**. Issue bersifat publik. Ikut atau tidak ikut tidak mengubah
> apa pun pada kit maupun dukungannya.

## B. Pernyataan persetujuan (di formulir issue; semua kotak wajib dicentang)

**Penelitian:** [judul penelitian], penelitian doktoral oleh Huzair Saputra, [universitas, program studi]. Persetujuan
etik: [nomor].

**Yang Anda bagikan:** hanya angka di laporan terlampir (bagian C) dan jawaban formulir yang Anda pilih untuk diisi
(peran, ukuran tim, sektor: pemerintah / swasta / pendidikan / perorangan). Tidak pernah kode sumber, nama repositori atau
proyek, teks backlog atau tiket, nama, alamat email, akun forge, rahasia, atau data pribadi pengguna, pelanggan, atau
warga Anda.

**Publik sejak awal:** issue GitHub bersifat publik. Laporan Anda dan akun GitHub pengirimnya bisa dilihat siapa saja.
Kirim dari akun yang Anda tidak keberatan tampil. Dataset penelitian menyimpan laporan tanpa nama akun Anda.

**Penggunaan:** meneliti cara tim bekerja dengan agen pengode AI di bawah alur kerja terstruktur. Publikasi penelitian
hanya memuat **agregat** (misalnya rata-rata per sektor atau ukuran tim), tidak pernah satu tim atau satu orang.

**Sukarela:** keikutsertaan adalah pilihan bebas Anda. Bila laporan mencakup sebuah tim, setiap anggota yang
pekerjaannya dihitung sudah setuju, dan data ini **tidak pernah dipakai untuk menilai kinerja siapa pun**. Pimpinan tim
yang mengumpulkan data dari stafnya memastikan bahwa menolak tidak membawa akibat apa pun.

**Kewenangan:** bila Anda mengirim atas nama organisasi (instansi pemerintah atau perusahaan), Anda berwenang membagikan
metrik ini, dan metrik itu tidak memuat informasi rahasia atau dikecualikan.

**Penyimpanan dan penarikan:** kiriman mentah disimpan **5 tahun** lalu dihapus; agregat yang sudah dipublikasikan tetap
ada. Untuk menarik kiriman, beri komentar `tarik` di issue Anda (atau hapus laporannya dari issue): issue dihapus dan
laporan dikeluarkan dari setiap dataset yang belum dipublikasikan. Untuk hal yang tidak ingin Anda sampaikan secara
publik, pakai kanal pelaporan privat repositori di GitHub.

**Konflik kepentingan:** peneliti adalah penulis scrum-kit dan sebuah pack alur kerja berbayar yang terpisah. Pack
berbayar itu tidak mengumpulkan data apa pun dan tidak termasuk penelitian ini.

- [ ] Saya sudah membaca pernyataan ini dan setuju laporan terlampir dipakai seperti yang dijelaskan.
- [ ] Laporan tidak memuat kode, nama, akun, rahasia, atau data pribadi.
- [ ] Bila mencakup tim atau organisasi, saya sudah mendapat persetujuan tim dan izin organisasi.

## C. Isi `scripts/laporan-riset.py` (usulan)

Satu berkas JSON per sprint, dibuat lokal, tidak pernah dikirim oleh skrip:

| Kolom | Contoh | Sumber |
|---|---|---|
| `id_kiriman` | UUID acak | dibuat tiap kali dijalankan |
| `versi_kit` | `1.7.0` | versi plugin |
| `agen_platform` | `claude-code`, `codex`, `lain` | ditanyakan sekali |
| `mode_jalan` | `claude-code`, `portable` | ringkasan sprint |
| `ukuran_tim`, `jumlah_posisi` | `6`, `6` | hitungan `pemilik`, tanpa nama |
| `jumlah_item`, `item_selesai` | `4`, `3` | backlog dan merge |
| `dod_terpenuhi` | `5/7` per item | laporan sprint |
| `putaran_review`, `mr_ditolak` | hitungan | forge, tanpa teks |
| `durasi_sprint_jam`, `durasi_mr_median_jam` | angka | cap waktu git dan forge |
| `ci_gagal_sebelum_hijau` | hitungan | forge |
| `persetujuan_pemilik_tercatat` | `true/false` per item, dihitung | forge |

Sengaja tidak dimuat: path, nama branch, pesan commit, username, email, cap waktu lebih rinci dari harian, dan apa pun
yang belum dilihat pengguna di berkas sebelum mengirim.

## D. Formulir issue

Draf di [`laporan-riset.issue-form.yml`](laporan-riset.issue-form.yml), dua bahasa: sektor, peran, ukuran tim, JSON yang ditempel,
dan tiga kotak wajib di bagian B. Baru dipindah ke `.github/ISSUE_TEMPLATE/` sesudah persetujuan etik, supaya tidak tayang tanpa sengaja.
