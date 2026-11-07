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

    echo "Halo" | python3 panggil_llm.py [--sistem "..."] [--json] [--tanpa-cache]
    python3 panggil_llm.py --uji     # uji urutan tanpa jaringan

Cache prompt (Anthropic API): bagian sistem dikirim sebagai blok dengan `cache_control`, sehingga
panggilan berulang dengan sistem yang sama (dalam 5 menit, atau 1 jam dengan SCRUM_KIT_CACHE_TTL=1h)
membaca masukan dari cache dengan harga sekitar sepersepuluh. Hemat hanya bila awalan yang sama
dipakai berulang; panggilan tunggal dengan sistem unik justru membayar tulis cache 1,25x. Awalan di
bawah 512 token tidak di-cache. UJI YANG HARUS TANPA CACHE (mis. mengukur biaya masukan mentah)
mematikannya dengan SCRUM_KIT_TANPA_CACHE=1, argumen `cache=False`, atau `--tanpa-cache`.
Pemakaian token (masukan, tulis cache, baca cache, keluaran) dicetak ke stderr tiap panggilan.
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
INSTRUKSI_JSON = "Balas hanya JSON valid, tanpa pagar kode atau teks lain."
ENV_TANPA_CACHE = "SCRUM_KIT_TANPA_CACHE"
ENV_CACHE_TTL = "SCRUM_KIT_CACHE_TTL"


class PanggilanLLMGagal(RuntimeError):
    """Semua backend skrip gagal atau tidak tersedia."""


def _peringatan(pesan: str) -> None:
    print(f"PERINGATAN: {pesan}", file=sys.stderr)


def teks_gemini(hasil: dict) -> str | None:
    """Teks dari respons generateContent; None bila jawabannya tidak selesai normal (mis. MAX_TOKENS)."""
    kandidat = hasil["candidates"][0]
    alasan = kandidat.get("finishReason")
    if alasan and alasan != "STOP":
        _peringatan(f"Gemini API berhenti ({alasan}) -- lanjut ke Anthropic API.")
        return None
    return kandidat["content"]["parts"][0]["text"].strip() or None


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
        return teks_gemini(hasil)
    except urllib.error.HTTPError as e:
        _peringatan(f"Gemini API gagal (HTTP {e.code}) -- lanjut ke Anthropic API.")
        return None
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, IndexError, TypeError, ValueError) as e:
        _peringatan(f"Gemini API gagal ({type(e).__name__}) -- lanjut ke Anthropic API.")
        return None


def cache_aktif(cache: bool | None = None) -> bool:
    """Cache prompt menyala kecuali dimatikan: argumen `cache=False` menang, lalu env ENV_TANPA_CACHE."""
    if cache is not None:
        return cache
    return os.environ.get(ENV_TANPA_CACHE, "").strip().lower() not in ("1", "true", "ya")


def blok_sistem(sistem: str | None, cache: bool | None = None, ttl: str | None = None):
    """Nilai parameter `system`: teks biasa, atau satu blok dengan `cache_control` bila cache menyala.
    Awalan stabil (sistem) di-cache; prompt yang berubah-ubah tetap di `messages`, setelah titik cache."""
    if not sistem or not cache_aktif(cache):
        return sistem
    kontrol = {"type": "ephemeral"}
    if (ttl or os.environ.get(ENV_CACHE_TTL, "")) == "1h":
        kontrol["ttl"] = "1h"
    return [{"type": "text", "text": sistem, "cache_control": kontrol}]


def permintaan_batch(custom_id: str, prompt: str, sistem: str | None = None, cache: bool | None = None,
                     ttl: str = "1h") -> dict:
    """Satu baris permintaan Message Batches API (`{custom_id, params}`) dengan sistem ber-cache.
    TTL 1 jam sebagai bawaan, karena batch bisa berjalan lebih lama dari 5 menit; cache di batch
    bersifat upaya terbaik. Kirim lewat `client.messages.batches.create(requests=[...])`."""
    params = {
        "model": os.environ.get("SCRUM_KIT_ANTHROPIC_MODEL", ANTHROPIC_MODEL_BAWAAN),
        "max_tokens": 64000,
        "messages": [{"role": "user", "content": prompt}],
    }
    if sistem:
        params["system"] = blok_sistem(sistem, cache, ttl)
    return {"custom_id": custom_id, "params": params}


def _catat_pemakaian(pesan) -> None:
    u = pesan.usage
    print(
        "pemakaian anthropic: masukan=%s tulis_cache=%s baca_cache=%s keluaran=%s" % (
            u.input_tokens, getattr(u, "cache_creation_input_tokens", 0) or 0,
            getattr(u, "cache_read_input_tokens", 0) or 0, u.output_tokens),
        file=sys.stderr,
    )


def panggil_anthropic(prompt: str, sistem: str | None = None, cache: bool | None = None) -> str | None:
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
        argumen["system"] = blok_sistem(sistem, cache)
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

    _catat_pemakaian(pesan)
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
    # Tanpa ANTHROPIC_API_KEY: bila ada, `claude -p` menagih API, bukan langganan.
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    try:
        proses = subprocess.run(
            perintah, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT_DETIK, env=env
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


def panggil_llm(prompt: str, sistem: str | None = None, json_saja: bool = False,
                cache: bool | None = None) -> tuple[str, str]:
    """Kembalikan (teks, nama_backend) dari backend pertama yang berhasil:
    gemini -> anthropic -> claude-cli. Lempar PanggilanLLMGagal bila semua gagal
    (langkah 4: kerjakan di sesi Claude Desktop). `json_saja`: jawaban yang bukan
    JSON valid dianggap gagal dan backend berikutnya dicoba."""
    sistem_lain = sistem
    if json_saja:  # Gemini memakai responseMimeType; backend lain lewat instruksi sistem.
        sistem_lain = f"{sistem}\n\n{INSTRUKSI_JSON}" if sistem else INSTRUKSI_JSON
    for nama, panggil in (
        ("gemini", lambda: panggil_gemini(prompt, sistem, json_saja)),
        ("anthropic", lambda: panggil_anthropic(prompt, sistem_lain, cache=cache)),
        ("claude-cli", lambda: panggil_claude_cli(prompt, sistem_lain)),
    ):
        teks = panggil()
        if teks is None:
            continue
        if json_saja:
            try:
                json.loads(teks)
            except ValueError:
                _peringatan(f"{nama} tidak membalas JSON valid -- lanjut ke backend berikutnya.")
                continue
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
    argumen: list[tuple] = []

    def tiruan(nama, hasil):
        def f(*a, **_k):
            jejak.append(nama)
            argumen.append(a)
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

        # --json: jawaban bukan JSON -> backend berikutnya; instruksi JSON sampai ke Anthropic/CLI.
        jejak.clear()
        argumen.clear()
        modul.panggil_gemini = tiruan("gemini", "bukan json")
        modul.panggil_anthropic = tiruan("anthropic", '{"a": 1}')
        assert panggil_llm("x", "S", json_saja=True) == ('{"a": 1}', "anthropic"), jejak
        assert argumen[1] == ("x", f"S\n\n{INSTRUKSI_JSON}"), argumen
    finally:
        modul.panggil_gemini, modul.panggil_anthropic, modul.panggil_claude_cli = asli

    # Gemini: jawaban terpotong bukan sukses.
    def respons(alasan):
        kandidat = {"content": {"parts": [{"text": " ok "}]}}
        if alasan:
            kandidat["finishReason"] = alasan
        return {"candidates": [kandidat]}

    assert teks_gemini(respons("STOP")) == "ok"
    assert teks_gemini(respons(None)) == "ok"
    assert teks_gemini(respons("MAX_TOKENS")) is None

    assert main(["--sistem"]) == 2  # tanpa nilai: pesan pemakaian, bukan IndexError

    # Cache prompt: sistem jadi blok ber-cache; dimatikan oleh argumen, env, atau --tanpa-cache.
    env_asli = {k: os.environ.pop(k, None) for k in (ENV_TANPA_CACHE, ENV_CACHE_TTL)}
    try:
        assert blok_sistem("S") == [{"type": "text", "text": "S", "cache_control": {"type": "ephemeral"}}]
        assert blok_sistem("S", ttl="1h")[0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
        assert blok_sistem("S", cache=False) == "S" and blok_sistem(None) is None
        os.environ[ENV_TANPA_CACHE] = "1"
        assert blok_sistem("S") == "S", "env harus mematikan cache"
        assert blok_sistem("S", cache=True)[0]["cache_control"]["type"] == "ephemeral", "argumen menang atas env"
        del os.environ[ENV_TANPA_CACHE]
        os.environ[ENV_CACHE_TTL] = "1h"
        assert blok_sistem("S")[0]["cache_control"].get("ttl") == "1h"
        baris = permintaan_batch("a1", "P", "S")
        assert baris["custom_id"] == "a1" and baris["params"]["messages"][0]["content"] == "P"
        assert baris["params"]["system"][0]["cache_control"]["ttl"] == "1h"
        assert permintaan_batch("a2", "P", "S", cache=False)["params"]["system"] == "S"
        assert "system" not in permintaan_batch("a3", "P")["params"]
        # panggil_llm meneruskan `cache` ke backend Anthropic sebagai argumen kata kunci.
        diteruskan: dict = {}
        asli_a = modul.panggil_anthropic
        modul.panggil_anthropic = lambda p, s=None, cache=None: diteruskan.update(cache=cache) or "ok"
        modul.panggil_gemini = lambda *a, **k: None
        try:
            panggil_llm("x", "S", cache=False)
        finally:
            modul.panggil_anthropic = asli_a
        assert diteruskan == {"cache": False}, diteruskan
    finally:
        modul.panggil_gemini = asli[0]
        for k in (ENV_TANPA_CACHE, ENV_CACHE_TTL):
            os.environ.pop(k, None)
            if env_asli[k] is not None:
                os.environ[k] = env_asli[k]
    print("OK: urutan gemini -> anthropic -> claude-cli -> PanggilanLLMGagal, --json, finishReason, --sistem, cache prompt")


def main(argv: list[str]) -> int:
    if "--uji" in argv:
        _uji()
        return 0
    if "--tanpa-cache" in argv:
        os.environ[ENV_TANPA_CACHE] = "1"
    sistem = None
    if "--sistem" in argv:
        i = argv.index("--sistem") + 1
        if i >= len(argv):
            print('Pemakaian: panggil_llm.py [--sistem "<teks>"] [--json] [--tanpa-cache] < prompt', file=sys.stderr)
            return 2
        sistem = argv[i]
    # Byte mentah: sys.stdin memakai code page ANSI di Windows.
    prompt = sys.stdin.buffer.read().decode("utf-8", errors="replace")
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
