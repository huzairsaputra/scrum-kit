# Partisipasi riset: disclaimer, formulir persetujuan, dan laporan (draf)

Status: **draf untuk ditinjau PO** (15 Nov 2026). Berlaku untuk semua pengguna scrum-kit: perorangan, tim, instansi
pemerintah, dan perusahaan swasta. Versi bahasa Inggris: [persetujuan-riset.md](persetujuan-riset.md). Isian dalam
`[kurung]` dilengkapi sebelum dipublikasikan. Ini bukan nasihat hukum; teks akhir diperiksa terhadap ketentuan etik
kampus dan UU Pelindungan Data Pribadi (UU 27/2022).

## A. Disclaimer untuk README

> **Riset (opsional).** scrum-kit tidak mengirim apa pun ke mana pun: tanpa telemetri, tanpa laporan otomatis.
> scrum-kit juga bagian dari penelitian doktoral tentang alur kerja terstruktur berbasis spesifikasi untuk agen
> pengode AI. Bila ingin membantu, jalankan `scripts/laporan-riset.py` sesudah sprint. Skrip itu menulis ringkasan
> lokal berisi angka saja (lihat di bawah), tidak pernah kode, nama repositori, teks backlog, nama orang, atau rahasia.
> Anda membacanya, menyuntingnya, dan mengirimkannya sendiri lewat [formulir] hanya sesudah menyetujui pernyataan
> persetujuan. Ikut atau tidak ikut tidak mengubah apa pun pada kit maupun dukungannya.

## B. Pernyataan persetujuan (tampil di formulir, dicentang sebelum mengirim)

**Penelitian:** [judul penelitian], penelitian doktoral oleh Huzair Saputra, [universitas, program studi]. Persetujuan
etik: [nomor].

**Data yang dikumpulkan:** hanya angka di laporan (bagian C), dan jawaban yang Anda pilih untuk diisi di formulir
(peran, ukuran tim, sektor: pemerintah / swasta / pendidikan / perorangan). Tidak ada kode sumber, nama repositori atau
proyek, teks backlog atau tiket, nama, alamat email, akun forge, rahasia, atau data pribadi pengguna, pelanggan, atau
warga Anda.

**Penggunaan:** membandingkan cara tim bekerja dengan agen pengode AI di bawah alur kerja terstruktur. Hasil hanya
dipublikasikan dalam bentuk **agregat** (misalnya rata-rata per sektor atau ukuran tim), tidak pernah per tim atau per
orang.

**Sukarela:** keikutsertaan adalah pilihan bebas Anda. Bila Anda mengirim data sebuah tim, setiap anggota tim yang
pekerjaannya dihitung sudah setuju, dan data ini **tidak dipakai untuk menilai kinerja siapa pun**. Pimpinan tim yang
mengumpulkan data dari stafnya wajib memastikan bahwa menolak tidak membawa akibat apa pun.

**Kewenangan:** bila Anda mengirim atas nama organisasi (instansi pemerintah atau perusahaan), Anda menyatakan berwenang
membagikan metrik ini, dan metrik itu tidak memuat informasi rahasia atau dikecualikan.

**Penyimpanan dan penarikan:** kiriman disimpan di [lokasi] selama [jangka waktu], lalu dihapus. Setiap laporan memuat
ID kiriman acak. Kirim ID itu ke [kontak] untuk menghapus kiriman Anda kapan saja sebelum agregat yang memuatnya
dipublikasikan.

**Konflik kepentingan:** peneliti adalah penulis scrum-kit dan sebuah pack alur kerja berbayar yang terpisah. Pack
berbayar itu tidak mengumpulkan data apa pun dan tidak termasuk pengumpulan data ini.

☐ Saya sudah membaca pernyataan ini dan setuju laporan terlampir dipakai seperti yang dijelaskan.

## C. Isi `scripts/laporan-riset.py` (usulan)

Satu berkas JSON per sprint, dibuat lokal, tidak pernah dikirim oleh skrip:

| Kolom | Contoh | Sumber |
|---|---|---|
| `id_kiriman` | UUID acak | dibuat tiap kali dijalankan |
| `versi_kit` | `1.6.0` | versi plugin |
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
