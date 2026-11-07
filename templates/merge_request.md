# Ringkasan

<!-- Apa yang berubah dan mengapa. Sebutkan ID item backlog. -->

Item backlog:
Modul:

## Perubahan

<!-- Daftar endpoint/berkas penting yang berubah. -->

## Definition of Done

- [ ] Gate fmt dan lint bersih
- [ ] Gate build dan test hijau (keluaran di bawah)
- [ ] Gate DoD tanpa temuan
- [ ] Kontrak/dokumentasi endpoint diperbarui (contoh request, respons sukses, respons error)
- [ ] Validasi input dan otorisasi mengikuti pola framework; minimal satu uji negatif otorisasi
- [ ] Tidak ada rahasia/`.env`; perubahan tidak keluar dari wilayah kepemilikan
- [ ] Ditinjau `code-reviewer` (BERSIH) dan pipeline MR hijau pada HEAD
- [ ] Butir yang ditandai "tidak berlaku" punya alasan di serah terima sprint dan disetujui PO, di laporan kesiapan atau di chat (atau tidak ada). Persetujuan belum ada → jangan centang; tulis "menunggu persetujuan product owner" beserta butirnya (MR integrasi ke basis tidak di-merge selama itu)

## Bukti gate

```
<!-- Tempelkan keluaran gate. -->
```

## Catatan untuk peninjau

<!-- Keputusan desain, utang teknis yang sengaja ditinggalkan, risiko yang diterima PO. -->
