#!/usr/bin/env bash
# Buat worktree untuk satu agen/wilayah, bercabang dari branch integrasi sprint-nya.
#
# Semua aturan dibaca dari .claude/kit.json proyek (pola branch, wilayah, modul,
# checkout_bersama); tidak ada nama proyek atau modul yang ditulis mati di sini.
# Dokumentasi format: docs/kit-json.md di plugin scrum-kit.
#
# Pemakaian:
#   worktree-new.sh <wilayah> <id-item> <nomor-sprint> [--modul=<m>] [--base=<ref>]
#
# Contoh:
#   worktree-new.sh admin BE-1-S1-02 1                 # wilayah modul: sparse-checkout
#   worktree-new.sh tests QA-S1-01 1 --modul=admin     # test satu modul: sparse-checkout
#   worktree-new.sh shared SH-S1-01 1                  # wilayah lain: checkout penuh
#   worktree-new.sh admin BE-1-S2-02 2 --base=HEAD     # basis berupa commit saat ini
#
# Sparse-checkout hanya membatasi per DIREKTORI; pengecualian setingkat berkas
# ditegakkan hook kepemilikan (hooks/path_ownership.py). Keduanya saling melengkapi.
set -euo pipefail

gagal() {
	echo "GAGAL: $*" >&2
	exit 1
}

# --- interpreter Python yang benar-benar jalan (python3/python bisa stub Microsoft Store)
PY=""
# Sama dengan hooks/cari-python.sh plugin (skrip ini disalin ke proyek, jadi tidak bisa merujuknya):
# PATH dulu, lalu lokasi pemasangan bawaan Windows (PATH sesi Claude Code bisa tanpa `py`).
for kandidat in python3 python py 	"$HOME"/AppData/Local/Programs/Python/Launcher/py.exe 	"$HOME"/AppData/Local/Programs/Python/Python3*/python.exe 	/c/Windows/py.exe "/c/Program Files"/Python3*/python.exe /c/Python3*/python.exe; do
	if { command -v "$kandidat" >/dev/null 2>&1 || [[ -f "$kandidat" ]]; } &&
		"$kandidat" -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >/dev/null 2>&1; then
		PY="$kandidat"
		break
	fi
done
[[ -n "$PY" ]] || gagal "tidak ada interpreter Python yang berfungsi (python3/python/py)."

git rev-parse --git-dir >/dev/null 2>&1 || gagal "bukan di dalam repositori git."

# Worktree UTAMA, bukan worktree tempat skrip dijalankan; tanpa ini menjalankan skrip dari
# dalam worktree membuat tujuan bersarang. Baris pertama `git worktree list` = yang utama.
AKAR="$(git worktree list --porcelain | awk '/^worktree /{print substr($0,10); exit}')"
SAAT_INI="$(git rev-parse --show-toplevel)"
BERKAS_KIT="$SAAT_INI/.claude/kit.json"
[[ -f "$BERKAS_KIT" ]] || BERKAS_KIT="$AKAR/.claude/kit.json"
[[ -f "$BERKAS_KIT" ]] || gagal ".claude/kit.json tidak ditemukan. Buat lewat /kit-init (lihat docs/kit-json.md)."

# --- baca kit.json: satu panggilan Python, keluaran berupa penugasan shell yang sudah di-quote
KIT_ENV="$("$PY" - "$BERKAS_KIT" <<'PYEOF'
import json, shlex, sys

with open(sys.argv[1], encoding="utf-8") as f:
    cfg = json.load(f)

branch = cfg.get("branch") or {}
wilayah = cfg.get("wilayah") or {}
q = shlex.quote

def skalar(nama, nilai):
    print(f"{nama}={q(str(nilai if nilai is not None else ''))}")

def larik(nama, nilai):
    print(f"{nama}=({' '.join(q(str(x)) for x in nilai)})")

skalar("KIT_BASIS", branch.get("basis"))
skalar("KIT_INTEGRASI", branch.get("integrasi"))
skalar("KIT_POLA_WILAYAH", branch.get("wilayah"))
larik("KIT_MODUL", cfg.get("modul") or [])
larik("KIT_BERSAMA", cfg.get("checkout_bersama") or [])
larik("KIT_WILAYAH", [k for k, v in wilayah.items() if not v.get("per_modul")])
skalar("KIT_ADA_PER_MODUL", "1" if any(v.get("per_modul") for v in wilayah.values()) else "")
PYEOF
)" || gagal "kit.json tidak bisa dibaca/diurai: $BERKAS_KIT"
eval "$KIT_ENV"

[[ -n "$KIT_POLA_WILAYAH" && "$KIT_POLA_WILAYAH" == *"{wilayah}"* ]] || gagal "kit.json: branch.wilayah wajib ada dan memuat {wilayah}."
[[ -n "$KIT_BASIS" ]] || gagal "kit.json: branch.basis wajib ada."

NAMA_WILAYAH_SAH=("${KIT_WILAYAH[@]}")
if [[ -n "$KIT_ADA_PER_MODUL" ]]; then NAMA_WILAYAH_SAH+=(${KIT_MODUL[@]+"${KIT_MODUL[@]}"}); fi

pakai() {
	cat >&2 <<EOF
Pemakaian: worktree-new.sh <wilayah> <id-item> <nomor-sprint> [--modul=<m>] [--base=<ref>]

Wilayah yang sah: ${NAMA_WILAYAH_SAH[*]}
  --modul=<m>   hanya untuk wilayah 'tests'; mempersempit worktree ke satu modul
                (${KIT_MODUL[*]:-tanpa modul})
  --base=<ref>  titik cabang; bawaan origin/${KIT_INTEGRASI:-<integrasi>} (lalu ref lokalnya),
                jatuh ke origin/$KIT_BASIS dengan peringatan bila belum ada.
                Pakai --base=HEAD bila perkakas yang dibutuhkan belum ada di basis.
EOF
	exit 2
}

WILAYAH=""
ITEM=""
SPRINT=""
MODUL=""
BASE=""
for arg in "$@"; do
	case "$arg" in
		--modul=*) MODUL="${arg#--modul=}" ;;
		--base=*) BASE="${arg#--base=}" ;;
		-*) pakai ;;
		*)
			if [[ -z "$WILAYAH" ]]; then
				WILAYAH="$arg"
			elif [[ -z "$ITEM" ]]; then
				ITEM="$arg"
			elif [[ -z "$SPRINT" ]]; then
				SPRINT="$arg"
			else
				pakai
			fi
			;;
	esac
done
[[ -n "$WILAYAH" && -n "$ITEM" ]] || pakai

# Nomor sprint wajib hanya bila pola branch memakainya.
PAKAI_SPRINT=""
if [[ "$KIT_POLA_WILAYAH$KIT_INTEGRASI" == *"{n}"* || "$KIT_POLA_WILAYAH$KIT_INTEGRASI" == *"{nn}"* ]]; then
	PAKAI_SPRINT=1
fi
if [[ -n "$PAKAI_SPRINT" ]]; then
	[[ -n "$SPRINT" ]] || pakai
	[[ "$SPRINT" =~ ^[0-9]+$ ]] || gagal "nomor-sprint '$SPRINT' harus angka."
	SPRINT=$((10#$SPRINT)) # "02" -> 2, supaya {n} tanpa nol di depan
else
	SPRINT="${SPRINT:-0}"
fi

# --- validasi wilayah, modul, id
sah=0
for w in "${NAMA_WILAYAH_SAH[@]}"; do [[ "$WILAYAH" == "$w" ]] && sah=1; done
if ((sah == 0)); then
	echo "GAGAL: wilayah '$WILAYAH' tidak dikenal di .claude/kit.json." >&2
	echo "Wilayah yang sah: ${NAMA_WILAYAH_SAH[*]}" >&2
	echo "Nama wilayah menentukan izin tulis lewat hook kepemilikan." >&2
	exit 1
fi

# Wilayah per modul: namanya adalah nama modul itu sendiri.
WILAYAH_MODUL=""
for m in ${KIT_MODUL[@]+"${KIT_MODUL[@]}"}; do [[ "$WILAYAH" == "$m" ]] && WILAYAH_MODUL=1; done

if [[ -n "$MODUL" ]]; then
	[[ "$WILAYAH" == "tests" ]] || gagal "--modul hanya berlaku untuk wilayah 'tests'."
	ada=0
	for m in ${KIT_MODUL[@]+"${KIT_MODUL[@]}"}; do [[ "$MODUL" == "$m" ]] && ada=1; done
	((ada == 1)) || gagal "modul '$MODUL' tidak ada di kit.json (modul: ${KIT_MODUL[*]:-kosong})."
fi
[[ "$ITEM" =~ ^[A-Za-z0-9._-]+$ ]] || gagal "id-item '$ITEM' memuat karakter yang tidak sah untuk nama branch."

# --- nama branch dan tujuan dari pola
isi_pola() {
	local p="$1"
	p="${p//\{nn\}/$(printf '%02d' "$SPRINT")}"
	p="${p//\{n\}/$SPRINT}"
	p="${p//\{wilayah\}/$WILAYAH}"
	p="${p//\{id\}/$ITEM}"
	printf '%s' "$p"
}
BRANCH="$(isi_pola "$KIT_POLA_WILAYAH")"
INTEGRASI="$(isi_pola "$KIT_INTEGRASI")"
NAMA_REPO="$(basename "$AKAR")"
TUJUAN="$(dirname "$AKAR")/${NAMA_REPO}-wt/$WILAYAH-$ITEM"

cd "$AKAR"
[[ ! -e "$TUJUAN" ]] || gagal "$TUJUAN sudah ada. Hapus dulu: git worktree remove '$TUJUAN'"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then gagal "branch $BRANCH sudah ada."; fi

# --- basis. Fetch tidak boleh menggagalkan skrip (offline, atau branch remote sudah dihapus).
ambil() { git fetch --quiet origin "$1" 2>/dev/null; }
FETCH_GAGAL=""
if [[ -z "$BASE" ]]; then
	if [[ -n "$INTEGRASI" ]]; then
		ambil "$INTEGRASI" || FETCH_GAGAL=1
		for k in "origin/$INTEGRASI" "$INTEGRASI"; do
			if git rev-parse --verify --quiet "$k" >/dev/null; then
				BASE="$k"
				break
			fi
		done
	fi
	if [[ -z "$BASE" ]]; then
		echo "CATATAN: branch integrasi '$INTEGRASI' belum ada, jatuh ke basis (origin/$KIT_BASIS, atau $KIT_BASIS lokal bila remote tak ada)." >&2
		[[ -z "$INTEGRASI" ]] || echo "         Buat lebih dulu: git push origin origin/$KIT_BASIS:refs/heads/$INTEGRASI" >&2
		ambil "$KIT_BASIS" || FETCH_GAGAL=1
		BASE="origin/$KIT_BASIS"
		git rev-parse --verify --quiet "$BASE" >/dev/null || BASE="$KIT_BASIS"
	fi
elif [[ "$BASE" == origin/* ]]; then
	ambil "${BASE#origin/}" || FETCH_GAGAL=1
fi
git rev-parse --verify --quiet "$BASE" >/dev/null || gagal "ref '$BASE' tidak ditemukan."
if [[ -n "$FETCH_GAGAL" && "$BASE" != "HEAD" ]]; then
	echo "PERINGATAN: fetch dari origin gagal (offline atau branch remote sudah dihapus); memakai $BASE lokal (bisa usang)." >&2
fi

# --- cakupan checkout. Mode cone selalu menyertakan berkas di akar repo.
SPARSE=()
if ((${#KIT_BERSAMA[@]} > 0)); then
	if [[ -n "$WILAYAH_MODUL" ]]; then
		SPARSE=("$WILAYAH")
	elif [[ "$WILAYAH" == "tests" && -n "$MODUL" ]]; then
		SPARSE=("$MODUL")
	fi
	if ((${#SPARSE[@]} > 0)); then
		for d in "${KIT_BERSAMA[@]}"; do SPARSE+=("${d%/}"); done
		SPARSE+=(.claude)
	fi
fi

git worktree add --quiet -b "$BRANCH" "$TUJUAN" "$BASE"
if ((${#SPARSE[@]} > 0)); then
	git -C "$TUJUAN" sparse-checkout init --cone
	git -C "$TUJUAN" sparse-checkout set "${SPARSE[@]}"
fi

# Berkas yang benar-benar ada di disk: entri skip-worktree ditandai 'S' oleh ls-files -v.
TOTAL="$(git -C "$TUJUAN" ls-files | wc -l | tr -d ' ')"
ADA="$(git -C "$TUJUAN" ls-files -v | { grep -vc '^S' || true; })"
HEMAT=0
if ((TOTAL > 0)); then HEMAT=$((100 - (ADA * 100 / TOTAL))); fi

cat <<EOF

Worktree siap.
  path     : $TUJUAN
  branch   : $BRANCH (dari $BASE)
  wilayah  : $WILAYAH$([[ -n "$MODUL" ]] && echo " (modul $MODUL)")
  berkas   : $ADA dari $TOTAL di disk (${HEMAT}% lebih sedikit)
  cakupan  : ${SPARSE[*]:-seluruh repo}

Langkah berikutnya:
  cd $TUJUAN

Ingat:
  - Hook kepemilikan menolak Write/Edit di luar wilayah '$WILAYAH', termasuk pengecualian
    setingkat berkas yang tidak bisa dijangkau sparse-checkout.
  - Bereskan setelah selesai: git worktree remove '$TUJUAN'
EOF
