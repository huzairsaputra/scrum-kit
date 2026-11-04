#!/bin/sh
# Cetak path interpreter Python 3 yang BENAR-BENAR jalan; kosong + exit 1 bila tidak ada.
# Dipakai jalankan.sh dan langkah verifikasi /scrum-kit:kit-init:
#   PY=$(sh "${CLAUDE_PLUGIN_ROOT}/hooks/cari-python.sh") && "$PY" -c "..."
#
# Di Windows `python3`/`python` bisa stub Microsoft Store ("Python was not found"), dan PATH
# sesi Claude Code bisa tidak memuat `py` walau Python terpasang — jadi setelah PATH, coba
# lokasi pemasangan bawaan Windows. Kandidat layak hanya bila `-c "import sys"` sukses.

layak() { "$1" -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >/dev/null 2>&1; }

for p in python3 python py; do
	if command -v "$p" >/dev/null 2>&1 && layak "$p"; then
		command -v "$p"
		exit 0
	fi
done

# ponytail: daftar lokasi tetap; tambah di sini bila tim memasang Python di tempat lain.
for p in \
	"$HOME"/AppData/Local/Programs/Python/Launcher/py.exe \
	"$HOME"/AppData/Local/Programs/Python/Python3*/python.exe \
	/c/Windows/py.exe \
	"/c/Program Files"/Python3*/python.exe \
	/c/Python3*/python.exe; do
	if [ -f "$p" ] && layak "$p"; then
		echo "$p"
		exit 0
	fi
done
exit 1
