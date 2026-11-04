#!/usr/bin/env python3
"""Satu pintu pemanggilan LLM untuk skrip proyek (scrum-kit).

Urutan backend (sama untuk graphify, sinkron dokumentasi API, dan skrip baru):
berhenti di backend pertama yang berhasil.

  1. Gemini API     -- GEMINI_API_KEY / GOOGLE_API_KEY (model: GEMINI_MODEL,
                       bawaan gemini-3.6-flash).
  2. Anthropic API  -- ANTHROPIC_API_KEY (+ ANTHROPIC_WORKSPACE_ID bila key
                       tidak terikat workspace), SDK `anthropic`, model
                       SCRUM_KIT_ANTHROPIC_MODEL (bawaan claude-opus-5-5).
                       Model sengaja TIDAK dibaca dari ANTHROPIC_MODEL, karena
                       variabel itu juga dibaca Claude Code.
  3. CLI `claude`   -- sesi Claude Code yang sudah login (kuota langganan).
  4. Claude Desktop -- tidak dapat dipanggil dari skrip; bila ketiganya gagal,
                       PanggilanLLMGagal dilempar dan pekerjaan diambil sesi
                       host (manusia/orkestrator).

Tiap langkah dilewati bila key/SDK/CLI tidak ada, atau panggilannya gagal
(kredensial, kuota, kredit habis, jaringan, penolakan, keluaran terpotong).
Key tidak pernah dicetak.

Pakai sebagai pustaka:

    from panggil_llm import panggil_llm
    teks, backend = panggil_llm("Ringkas ini: ...", sistem="Jawab dalam Bahasa Indonesia.")

Pakai dari shell (prompt lewat stdin, jawaban ke stdout, backend ke stderr):

    echo "Halo" | python3 panggil_llm.py [--sistem "..."] [--json]
    python3 panggil_llm.py --uji     # uji urutan tanpa jaringan
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

TIMEOUT_DETIK = 900
GEMINI_MODEL_BAWAAN = "gemini-3.6-flash"
ANTHROPIC_MODEL_BAWAAN = "claude-opus-5-5"


class PanggilanLLMGagal(RuntimeError):
    """Semua backend skrip gagal atau tidak tersedia."""


def _peringatan(pesan: str) -> None:
    print(f"PERINGATAN: {pesan}", file=sys.stderr)


def panggil_gemini(prompt: str, sistem: str | None = None, json_saja: bool = False) -> str | None:
    """Gemini lewat REST (stdlib saja). None bila key tidak ada atau gagal."""
    kunci = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not kunci:
        return None

    model = os.environ.get("GEMINI_MODEL", GEMINI_MODEL_BAWAAN)
    badan = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    if sistem:
        badan["systemInstruction"] = {"parts": [{"text": sistem}]}
    if json_saja:
        badan["generationConfig"] = {"responseMimeType": "application/json"}

    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(badan).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": kunci},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_DETIK) as resp:
            hasil = json.loads(resp.read().decode("utf-8"))
        teks = hasil["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        _peringatan(f"Gemini API gagal (HTTP {e.code}) -- lanjut ke Anthropic API.")
        return None
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, IndexError, TypeError, ValueError) as e:
        _peringatan(f"Gemini API gagal ({type(e).__name__}) -- lanjut ke Anthropic API.")
        return None
    return teks or None


def panggil_anthropic(prompt: str, sistem: str | None = None) -> str | None:
    """Anthropic Messages API (streaming). None bila key/SDK tidak ada atau gagal."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ModuleNotFoundError:
        _peringatan("SDK `anthropic` belum terpasang (pip install anthropic) -- lanjut ke CLI claude.")
        return None

    workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    klien = anthropic.Anthropic(
        timeout=TIMEOUT_DETIK,
        default_headers={"anthropic-workspace-id": workspace} if workspace else None,
    )
    argumen = {
        "model": os.environ.get("SCRUM_KIT_ANTHROPIC_MODEL", ANTHROPIC_MODEL_BAWAAN),
        "max_tokens": 64000,
        "messages": [{"role": "user", "content": prompt}],
    }
    if sistem:
        argumen["system"] = sistem
    try:
        with klien.messages.stream(**argumen) as aliran:
            pesan = aliran.get_final_message()
    except anthropic.APIStatusError as e:
        # Termasuk 401/403 kredensial, 429 batas laju, 400 kredit habis, 5xx.
        _peringatan(f"Anthropic API gagal (HTTP {e.status_code}) -- lanjut ke CLI claude.")
        return None
    except anthropic.APIConnectionError:
        _peringatan("Anthropic API tidak terjangkau -- lanjut ke CLI claude.")
        return None

    if pesan.stop_reason in ("refusal", "max_tokens"):
        _peringatan(f"Anthropic API berhenti ({pesan.stop_reason}) -- lanjut ke CLI claude.")
        return None
    teks = "".join(b.text for b in pesan.content if b.type == "text").strip()
    return teks or None


def panggil_claude_cli(prompt: str, sistem: str | None = None) -> str | None:
    """`claude -p` (sesi Claude Code yang sudah login). None bila tidak ada atau gagal."""
    if shutil.which("claude") is None:
        return None

    perintah = ["claude", "-p", "--output-format", "json"]
    if sistem:
        perintah += ["--append-system-prompt", sistem]
    try:
        proses = subprocess.run(
            perintah, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT_DETIK
        )
        hasil = json.loads(proses.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        _peringatan(f"CLI claude gagal ({type(e).__name__}).")
        return None
    # `claude -p` bisa keluar non-zero dengan alasan di stdout (mis. batas sesi).
    if proses.returncode != 0 or hasil.get("is_error"):
        _peringatan(f"CLI claude gagal: {str(hasil.get('result'))[:300]}")
        return None
    teks = str(hasil.get("result") or "").strip()
    return teks or None


def panggil_llm(prompt: str, sistem: str | None = None, json_saja: bool = False) -> tuple[str, str]:
    """Kembalikan (teks, nama_backend) dari backend pertama yang berhasil:
    gemini -> anthropic -> claude-cli. Lempar PanggilanLLMGagal bila semua gagal
    (langkah 4: kerjakan di sesi Claude Desktop)."""
    for nama, panggil in (
        ("gemini", lambda: panggil_gemini(prompt, sistem, json_saja)),
        ("anthropic", lambda: panggil_anthropic(prompt, sistem)),
        ("claude-cli", lambda: panggil_claude_cli(prompt, sistem)),
    ):
        teks = panggil()
        if teks is not None:
            return teks, nama
    raise PanggilanLLMGagal(
        "Semua backend gagal atau tidak tersedia (Gemini, Anthropic, CLI claude): "
        "lanjutkan di sesi Claude Desktop."
    )


def _uji() -> None:
    """Uji urutan dan fallback tanpa jaringan (fungsi backend diganti tiruan)."""
    modul = sys.modules[__name__]
    asli = (modul.panggil_gemini, modul.panggil_anthropic, modul.panggil_claude_cli)
    jejak: list[str] = []

    def tiruan(nama, hasil):
        def f(*_a, **_k):
            jejak.append(nama)
            return hasil
        return f

    try:
        for harapan, hasil in (
            (("ok-g", "gemini"), ("ok-g", None, None)),
            (("ok-a", "anthropic"), (None, "ok-a", None)),
            (("ok-c", "claude-cli"), (None, None, "ok-c")),
        ):
            jejak.clear()
            modul.panggil_gemini = tiruan("gemini", hasil[0])
            modul.panggil_anthropic = tiruan("anthropic", hasil[1])
            modul.panggil_claude_cli = tiruan("claude-cli", hasil[2])
            assert panggil_llm("x") == harapan, harapan
            assert jejak == ["gemini", "anthropic", "claude-cli"][: len(jejak)], jejak
            assert jejak[-1] == harapan[1], jejak

        modul.panggil_gemini = modul.panggil_anthropic = modul.panggil_claude_cli = tiruan("-", None)
        try:
            panggil_llm("x")
            raise AssertionError("seharusnya PanggilanLLMGagal")
        except PanggilanLLMGagal:
            pass
    finally:
        modul.panggil_gemini, modul.panggil_anthropic, modul.panggil_claude_cli = asli
    print("OK: urutan gemini -> anthropic -> claude-cli -> PanggilanLLMGagal")


def main(argv: list[str]) -> int:
    if "--uji" in argv:
        _uji()
        return 0
    sistem = None
    if "--sistem" in argv:
        sistem = argv[argv.index("--sistem") + 1]
    prompt = sys.stdin.read()
    if not prompt.strip():
        print("GAGAL: prompt kosong (kirim lewat stdin).", file=sys.stderr)
        return 2
    try:
        teks, backend = panggil_llm(prompt, sistem, json_saja="--json" in argv)
    except PanggilanLLMGagal as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return 1
    print(f"backend: {backend}", file=sys.stderr)
    print(teks)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
