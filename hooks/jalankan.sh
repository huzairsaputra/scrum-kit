#!/bin/sh
# Pembungkus hook scrum-kit: memilih interpreter Python yang BENAR-BENAR jalan, lalu
# menyerahkan stdin dan exit code ke path_ownership.py.
#
# Di Windows `python3`/`python` bisa berupa stub Microsoft Store yang gagal dengan
# "Python was not found", jadi sebuah interpreter hanya dianggap layak bila
# `$p -c "import sys"` sukses (lihat cari-python.sh).
# Bila tidak ada yang layak: peringatan ke stderr dan exit 0 (fail-open).
#
# Dipanggil dari hooks.json: sh "${CLAUDE_PLUGIN_ROOT}/hooks/jalankan.sh"

# Tanpa perintah eksternal (dirname) supaya tetap jalan walau PATH minim.
case "$0" in
	*/* | *\\*) direktori=${0%[/\\]*} ;; # CLAUDE_PLUGIN_ROOT di Windows bisa berbackslash
	*) direktori=. ;;
esac

skrip="$direktori/path_ownership.py"
if [ ! -f "$skrip" ]; then
	echo "[scrum-kit] PERINGATAN: $skrip tidak ditemukan; hook kepemilikan dilewati." >&2
	exit 0 # python yang gagal membuka berkas keluar dengan kode 2 = akan memblokir kerja
fi

# Pemilihan interpreter (PATH lalu lokasi pemasangan bawaan Windows) ada di cari-python.sh.
if p=$(sh "$direktori/cari-python.sh"); then
	exec "$p" "$skrip"
fi

echo "[scrum-kit] PERINGATAN: tidak ada interpreter Python 3 yang berfungsi (lihat hooks/cari-python.sh); hook kepemilikan dilewati." >&2
exit 0
