#!/usr/bin/env python3
"""Hook PreToolUse (plugin scrum-kit): menolak Write/Edit/NotebookEdit di luar wilayah agen.

Identitas agen tidak ada di payload hook, jadi kepemilikan ditentukan dari NAMA BRANCH
git pada worktree tempat berkas berada. Aturannya dibaca dari `<akar repo>/.claude/kit.json`
(lihat docs/kit-json.md): pola `branch.wilayah`, tabel `wilayah` (`tulis`/`kecuali`/
`per_modul`), dan daftar `modul`. Tidak ada nama proyek atau modul yang ditulis mati di sini.

Kontrak
-------
- Diizinkan (exit 0) bila: berkas di luar repo git, tidak ada kit.json, branch tidak cocok
  pola `branch.wilayah` (branch manusia/orkestrator), atau path cocok `tulis` dan tidak
  cocok `kecuali`.
- Ditolak (exit 2, pesan di stderr, stdout kosong): wilayah tak dikenal, atau path di luar
  wilayah.
- Galat tak terduga (JSON rusak, git gagal, kit.json rusak): fail-open. Peringatan ke stderr
  dan exit 0; hook tidak boleh memblokir kerja karena bug-nya sendiri.

Uji mandiri: py -I hooks/test_path_ownership.py
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys

NAMA_PLUGIN = "scrum-kit"
TOOL_DIPERIKSA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
WINDOWS = os.name == "nt"


# --------------------------------------------------------------------------- utilitas


def peringatan(pesan: str) -> None:
    sys.stderr.write(f"[{NAMA_PLUGIN}] PERINGATAN path_ownership: {pesan}\n")


def jalankan_git(direktori: str, *argumen: str) -> str | None:
    """Keluaran git (strip) atau None bila gagal."""
    try:
        hasil = subprocess.run(
            ["git", "-C", direktori, *argumen],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except FileNotFoundError:
        peringatan("git tidak ditemukan di PATH; kepemilikan tidak diperiksa, penulisan diizinkan.")
        return None
    except (OSError, subprocess.SubprocessError):
        return None
    if hasil.returncode != 0:
        return None
    return hasil.stdout.strip() or None


def normalisasi_windows(path: str) -> str:
    """`/c/xampp/x` (Git Bash), `/mnt/c/x`, `/cygdrive/c/x` -> `C:/xampp/x`. No-op di non-Windows."""
    if not WINDOWS:
        return path
    cocok = re.match(r"^/(?:mnt/|cygdrive/)?([A-Za-z])(?:/(.*))?$", path)
    if cocok:
        return f"{cocok.group(1).upper()}:/{cocok.group(2) or ''}"
    return path


def path_absolut(berkas: str, cwd: str) -> str:
    berkas = normalisasi_windows(berkas)
    if not os.path.isabs(berkas):
        berkas = os.path.join(cwd, berkas)
    return os.path.realpath(os.path.normpath(berkas))


def direktori_ada(path: str, cadangan: str) -> str:
    """Leluhur terdekat yang sudah ada (berkas baru boleh berada di direktori yang belum ada)."""
    d = os.path.dirname(path)
    while d and not os.path.isdir(d):
        induk = os.path.dirname(d)
        if induk == d:
            return cadangan
        d = induk
    return d or cadangan


def kunci(path: str) -> str:
    """Bentuk pembanding: `/` sebagai pemisah, huruf kecil di Windows (sistem berkas case-insensitive)."""
    p = path.replace("\\", "/")
    return p.lower() if WINDOWS else p


def relatif_terhadap(akar: str, path: str) -> str | None:
    """Path relatif akar dengan `/` (huruf asli dipertahankan), atau None bila di luar akar."""
    a, p = kunci(akar).rstrip("/"), kunci(path)
    if p == a:
        return ""
    if not p.startswith(a + "/"):
        return None
    return path.replace("\\", "/")[len(a) + 1 :]


def cocok_glob(path: str, pola: str) -> bool:
    if WINDOWS:
        path, pola = path.lower(), pola.lower()
    if fnmatch.fnmatchcase(path, pola):
        return True
    # `**/x` juga harus mencakup `x` di akar repo (fnmatch mewajibkan satu `/`).
    return pola.startswith("**/") and fnmatch.fnmatchcase(path, pola[3:])


# --------------------------------------------------------------------------- konfigurasi


def regex_branch(pola: str) -> re.Pattern[str]:
    """Pola `branch.wilayah` -> regex. {nn}=\\d{2}, {n}=\\d+, {wilayah}=grup bernama, {id}=.+"""
    bagian = re.split(r"(\{nn\}|\{n\}|\{wilayah\}|\{id\})", pola)
    keluar: list[str] = []
    sudah_wilayah = False
    for b in bagian:
        if b == "{nn}":
            keluar.append(r"\d{2}")
        elif b == "{n}":
            keluar.append(r"\d+")
        elif b == "{wilayah}":
            keluar.append(r"(?P=wilayah)" if sudah_wilayah else r"(?P<wilayah>[^/]+)")
            sudah_wilayah = True
        elif b == "{id}":
            keluar.append(r".+")
        else:
            keluar.append(re.escape(b))
    return re.compile("".join(keluar))


def cari_wilayah(cfg: dict, nama: str) -> tuple[dict, str | None] | str | None:
    """Kembalikan (definisi wilayah, modul|None), pesan galat (str), atau None bila tak dikenal."""
    semua = cfg.get("wilayah") or {}
    if nama in semua:
        if semua[nama].get("per_modul"):
            return (
                f"Wilayah '{nama}' berlaku per modul: nama di branch harus nama modulnya "
                f"({', '.join(cfg.get('modul') or []) or 'daftar modul kosong'})."
            )
        return semua[nama], None
    if nama in (cfg.get("modul") or []):
        for definisi in semua.values():
            if definisi.get("per_modul"):
                return definisi, nama
    return None


def glob_efektif(definisi: dict, kunci_daftar: str, modul: str | None) -> list[str]:
    daftar = definisi.get(kunci_daftar) or []
    if modul:
        return [g.replace("{modul}", modul) for g in daftar]
    return list(daftar)


def diizinkan(definisi: dict, modul: str | None, path: str) -> bool:
    tulis = glob_efektif(definisi, "tulis", modul)
    kecuali = glob_efektif(definisi, "kecuali", modul)
    if not any(cocok_glob(path, g) for g in tulis):
        return False
    return not any(cocok_glob(path, g) for g in kecuali)


def pemilik_lain(cfg: dict, path: str, kecuali_nama: str) -> list[str]:
    """Agen dari wilayah lain yang boleh menulis path ini (untuk saran di pesan penolakan)."""
    agen: list[str] = []
    for nama, definisi in (cfg.get("wilayah") or {}).items():
        if definisi.get("per_modul"):
            kandidat = [(m, m) for m in (cfg.get("modul") or [])]
        else:
            kandidat = [(nama, None)]
        for label, modul in kandidat:
            if label == kecuali_nama:
                continue
            if diizinkan(definisi, modul, path):
                nama_agen = definisi.get("agen")
                if nama_agen and nama_agen not in agen:
                    agen.append(nama_agen)
    return agen


def pesan_tolak(nama: str, branch: str, path: str, definisi: dict, modul: str | None, cfg: dict) -> str:
    tulis = glob_efektif(definisi, "tulis", modul)
    kecuali = glob_efektif(definisi, "kecuali", modul)
    baris = [
        f"[{NAMA_PLUGIN}] Penulisan ditolak: '{path}' di luar wilayah '{nama}' (branch '{branch}').",
        f"  Wilayah ini hanya boleh menulis: {', '.join(tulis) or '(kosong)'}",
    ]
    if kecuali:
        baris.append(f"  Kecuali: {', '.join(kecuali)}")
    pemilik = pemilik_lain(cfg, path, nama)
    if pemilik:
        baris.append(f"  Saran: serahkan perubahan ini ke agen {' atau '.join(pemilik)}; jangan tulis sendiri.")
    else:
        baris.append("  Saran: serahkan ke orkestrator/manusia, atau ubah aturannya di .claude/kit.json.")
    return "\n".join(baris)


# --------------------------------------------------------------------------- inti


def keputusan(payload: dict) -> tuple[int, str]:
    """(kode keluar, pesan stderr)."""
    nama_tool = payload.get("tool_name")
    if nama_tool and nama_tool not in TOOL_DIPERIKSA:
        return 0, ""

    masukan = payload.get("tool_input") or {}
    berkas = masukan.get("notebook_path") or masukan.get("file_path")
    if not berkas:
        return 0, ""

    cwd = payload.get("cwd") or os.getcwd()
    path = path_absolut(str(berkas), str(cwd))
    direktori = direktori_ada(path, str(cwd))

    akar = jalankan_git(direktori, "rev-parse", "--show-toplevel")
    if not akar:
        return 0, ""  # di luar repo git mana pun
    akar = os.path.realpath(akar)
    relatif = relatif_terhadap(akar, path)
    if not relatif:
        return 0, ""  # di luar akar ini (atau akar itu sendiri)

    berkas_kit = os.path.join(akar, ".claude", "kit.json")
    if not os.path.isfile(berkas_kit):
        return 0, ""
    with open(berkas_kit, encoding="utf-8") as f:
        cfg = json.load(f)

    pola = (cfg.get("branch") or {}).get("wilayah")
    if isinstance(pola, list):
        pola = pola[0] if pola else None
    if not pola:
        peringatan("kit.json tanpa branch.wilayah; dilewati.")
        return 0, ""

    branch = jalankan_git(akar, "rev-parse", "--abbrev-ref", "HEAD") or jalankan_git(
        akar, "symbolic-ref", "--short", "-q", "HEAD"  # repo baru tanpa commit
    )
    if not branch:
        return 0, ""
    cocok = regex_branch(str(pola)).fullmatch(branch)
    if not cocok:
        return 0, ""  # branch manusia/orkestrator

    nama = cocok.group("wilayah")
    hasil = cari_wilayah(cfg, nama)
    if hasil is None:
        sah = sorted(k for k, v in (cfg.get("wilayah") or {}).items() if not v.get("per_modul"))
        sah += sorted(cfg.get("modul") or [])
        return 2, (
            f"[{NAMA_PLUGIN}] Penulisan ditolak: branch '{branch}' memakai wilayah '{nama}' "
            f"yang tidak dikenal di .claude/kit.json.\n  Wilayah yang sah: {', '.join(sah) or '(kosong)'}"
        )
    if isinstance(hasil, str):
        return 2, f"[{NAMA_PLUGIN}] Penulisan ditolak: {hasil}"

    definisi, modul = hasil
    if diizinkan(definisi, modul, relatif):
        return 0, ""
    return 2, pesan_tolak(nama, branch, relatif, definisi, modul, cfg)


def main() -> int:
    for aliran in (sys.stderr, sys.stdout):
        try:
            aliran.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
        if not isinstance(payload, dict):
            raise ValueError("payload bukan objek JSON")
        kode, pesan = keputusan(payload)
    except Exception as galat:  # noqa: BLE001 - fail-open disengaja
        peringatan(f"{type(galat).__name__}: {galat}; penulisan diizinkan.")
        return 0
    if pesan:
        sys.stderr.write(pesan + "\n")
    return kode


if __name__ == "__main__":
    sys.exit(main())
