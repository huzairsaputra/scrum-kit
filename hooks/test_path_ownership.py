#!/usr/bin/env python3
"""Self-test hook path_ownership.py dan pembungkus jalankan.sh (unittest stdlib).

Jalankan: py -I hooks/test_path_ownership.py   (atau python3 hooks/test_path_ownership.py)
Hook dijalankan sebagai subprocess terhadap repo git sementara.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

AKAR_HOOK = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(AKAR_HOOK, "path_ownership.py")
PEMBUNGKUS = os.path.join(AKAR_HOOK, "jalankan.sh")

# Contoh dari docs/kit-json.md (bagian yang dipakai hook).
KIT = {
    "proyek": "contoh",
    "stack": "go-goravel",
    "branch": {
        "basis": "staging",
        "rilis": "main",
        "integrasi": "integrasi-{n}",
        "wilayah": "sprint-{nn}/{wilayah}/{id}",
    },
    "modul": ["admin", "mobile", "opd"],
    "wilayah": {
        "modul": {
            "agen": "module-dev",
            "tulis": ["{modul}/**"],
            "kecuali": ["{modul}/tests/**", "*/bootstrap/migrations.go"],
            "per_modul": True,
        },
        "shared": {"agen": "shared-module-owner", "tulis": ["shared/**", "*/bootstrap/migrations.go"]},
        "tests": {"agen": "qa-test-engineer", "tulis": ["*/tests/**", "**/*_test.go"]},
        "contract": {"agen": "api-contract-keeper", "tulis": ["docs/api/**"]},
        "tooling": {"agen": "platform-tooling", "tulis": [".claude/**", "scripts/**", "Makefile"]},
    },
}

LINGKUNGAN = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(direktori, *argumen):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *argumen],
        cwd=direktori,
        check=True,
        capture_output=True,
        env=LINGKUNGAN,
    )


def buat_repo(dengan_kit=True, commit=True, isi_kit=None):
    akar = os.path.realpath(tempfile.mkdtemp(prefix="kit-uji-"))
    git(akar, "init", "-q")
    if dengan_kit:
        os.makedirs(os.path.join(akar, ".claude"))
        with open(os.path.join(akar, ".claude", "kit.json"), "w", encoding="utf-8") as f:
            f.write(isi_kit if isi_kit is not None else json.dumps(KIT))
    if commit:
        git(akar, "add", "-A")
        git(akar, "commit", "-q", "--allow-empty", "-m", "awal")
    return akar


def ganti_branch(akar, branch):
    git(akar, "checkout", "-q", "-B", branch)


def panggil(payload_mentah, cwd, perintah=None, env=None):
    data = payload_mentah if isinstance(payload_mentah, str) else json.dumps(payload_mentah)
    return subprocess.run(
        perintah or [sys.executable, HOOK],
        input=data.encode("utf-8"),
        cwd=cwd,
        capture_output=True,
        env=env or LINGKUNGAN,
        timeout=60,
    )


def payload_tulis(berkas, cwd, tool="Write", kunci="file_path"):
    return {"tool_name": tool, "tool_input": {kunci: berkas}, "cwd": cwd}


class UjiKepemilikan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.akar = buat_repo()
        cls.luar = os.path.realpath(tempfile.mkdtemp(prefix="kit-luar-"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.akar, ignore_errors=True)
        shutil.rmtree(cls.luar, ignore_errors=True)

    def tulis(self, branch, relatif, **kw):
        ganti_branch(self.akar, branch)
        berkas = os.path.join(self.akar, *relatif.split("/"))  # bentuk path asli OS
        return panggil(payload_tulis(berkas, self.akar, **kw), self.akar)

    def assertIzin(self, hasil):
        self.assertEqual(hasil.returncode, 0, hasil.stderr.decode())
        self.assertEqual(hasil.stdout, b"", "hook tidak boleh mencetak ke stdout")

    def assertTolak(self, hasil):
        self.assertEqual(hasil.returncode, 2, hasil.stderr.decode())
        self.assertEqual(hasil.stdout, b"", "penolakan hanya lewat stderr, bukan JSON stdout")

    # --- kasus wajib

    def test_orkestrator_bebas(self):
        for branch in ("integrasi-3", "main", "staging", "claude/apa-saja"):
            self.assertIzin(self.tulis(branch, "admin/tests/a_test.go"))

    def test_modul_menulis_modulnya(self):
        self.assertIzin(self.tulis("sprint-03/admin/BE-1", "admin/x.go"))

    def test_modul_tidak_boleh_tests(self):
        hasil = self.tulis("sprint-03/admin/BE-1", "admin/tests/a_test.go")
        self.assertTolak(hasil)
        pesan = hasil.stderr.decode()
        self.assertIn("admin", pesan)
        self.assertIn("admin/tests/a_test.go", pesan)
        self.assertIn("admin/**", pesan)  # glob yang diizinkan
        self.assertIn("qa-test-engineer", pesan)  # saran pemilik

    def test_modul_tidak_boleh_modul_lain(self):
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "mobile/x.go"))

    def test_tests_menulis_tests(self):
        self.assertIzin(self.tulis("sprint-03/tests/QA-1", "admin/tests/a.go"))

    def test_shared_menulis_bootstrap(self):
        self.assertIzin(self.tulis("sprint-03/shared/SH-1", "admin/bootstrap/migrations.go"))

    def test_bootstrap_ditolak_untuk_modul_dan_disarankan_ke_shared(self):
        hasil = self.tulis("sprint-03/admin/BE-1", "admin/bootstrap/migrations.go")
        self.assertTolak(hasil)
        self.assertIn("shared-module-owner", hasil.stderr.decode())

    def test_wilayah_tak_dikenal(self):
        hasil = self.tulis("sprint-03/frontend/FE-1", "admin/x.go")
        self.assertTolak(hasil)
        self.assertIn("frontend", hasil.stderr.decode())

    def test_wilayah_per_modul_dipakai_langsung_ditolak(self):
        self.assertTolak(self.tulis("sprint-03/modul/X-1", "admin/x.go"))

    def test_berkas_di_luar_repo(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        berkas = os.path.join(self.luar, "catatan.md")
        self.assertIzin(panggil(payload_tulis(berkas, self.akar), self.akar))

    def test_json_stdin_rusak(self):
        hasil = panggil("{bukan json", self.akar)
        self.assertEqual(hasil.returncode, 0)
        self.assertIn("PERINGATAN", hasil.stderr.decode())

    # --- tambahan

    def test_pola_branch_tidak_cocok_bebas(self):
        # {nn} wajib dua digit
        self.assertIzin(self.tulis("sprint-3/admin/BE-1", "mobile/x.go"))

    def test_glob_pada_akar_dan_bersarang(self):
        self.assertIzin(self.tulis("sprint-03/tests/QA-1", "foo_test.go"))
        self.assertIzin(self.tulis("sprint-03/tests/QA-1", "shared/a/b_test.go"))
        self.assertTolak(self.tulis("sprint-03/tests/QA-1", "admin/x.go"))

    def test_notebook_path(self):
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "mobile/n.ipynb", tool="NotebookEdit", kunci="notebook_path"))
        self.assertIzin(self.tulis("sprint-03/admin/BE-1", "admin/n.ipynb", tool="NotebookEdit", kunci="notebook_path"))

    def test_notebook_jatuh_ke_file_path(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        berkas = os.path.join(self.akar, "mobile", "n.ipynb")
        payload = {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": "", "file_path": berkas}, "cwd": self.akar}
        self.assertTolak(panggil(payload, self.akar))

    def test_tool_lain_diabaikan(self):
        self.assertIzin(self.tulis("sprint-03/admin/BE-1", "mobile/x.go", tool="Read"))

    def test_path_relatif_terhadap_cwd(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        payload = {"tool_name": "Write", "tool_input": {"file_path": os.path.join("mobile", "x.go")}, "cwd": self.akar}
        self.assertTolak(panggil(payload, self.akar))

    def test_berkas_baru_di_direktori_belum_ada(self):
        self.assertIzin(self.tulis("sprint-03/admin/BE-1", "admin/baru/dalam/sekali/x.go"))
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "mobile/baru/dalam/x.go"))

    def test_segmen_titik_titik_dinormalisasi(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        berkas = os.path.join(self.akar, "admin", "..", "mobile", "x.go")
        self.assertTolak(panggil(payload_tulis(berkas, self.akar), self.akar))

    def test_bentuk_slash_biasa(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        berkas = os.path.join(self.akar, "mobile", "x.go").replace("\\", "/")
        self.assertTolak(panggil(payload_tulis(berkas, self.akar), self.akar))

    @unittest.skipUnless(os.name == "nt", "khusus Windows")
    def test_windows_huruf_besar_kecil(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        berkas = os.path.join(self.akar.upper(), "ADMIN", "TESTS", "a.go")
        self.assertTolak(panggil(payload_tulis(berkas, self.akar), self.akar))
        berkas = os.path.join(self.akar.upper(), "Mobile", "x.go")
        self.assertTolak(panggil(payload_tulis(berkas, self.akar), self.akar))
        berkas = os.path.join(self.akar.upper(), "Admin", "x.go")
        self.assertIzin(panggil(payload_tulis(berkas, self.akar), self.akar))

    @unittest.skipUnless(os.name == "nt", "khusus Windows")
    def test_windows_bentuk_git_bash(self):
        ganti_branch(self.akar, "sprint-03/admin/BE-1")
        d = self.akar.replace("\\", "/")
        bash = "/" + d[0].lower() + d[2:]  # C:/x -> /c/x
        self.assertTolak(panggil(payload_tulis(bash + "/mobile/x.go", self.akar), self.akar))
        self.assertIzin(panggil(payload_tulis(bash + "/admin/x.go", self.akar), self.akar))

    def test_worktree_terpisah(self):
        ganti_branch(self.akar, "main")
        wt = os.path.realpath(tempfile.mkdtemp(prefix="kit-wt-"))
        shutil.rmtree(wt)
        try:
            git(self.akar, "worktree", "add", "-q", "-b", "sprint-04/mobile/M-1", wt)
            self.assertTolak(panggil(payload_tulis(os.path.join(wt, "admin", "x.go"), wt), wt))
            self.assertIzin(panggil(payload_tulis(os.path.join(wt, "mobile", "x.go"), wt), wt))
        finally:
            git(self.akar, "worktree", "remove", "--force", wt)


class UjiTanpaKonfigurasi(unittest.TestCase):
    def test_tanpa_kit_json(self):
        akar = buat_repo(dengan_kit=False)
        try:
            ganti_branch(akar, "sprint-03/admin/BE-1")
            hasil = panggil(payload_tulis(os.path.join(akar, "mobile", "x.go"), akar), akar)
            self.assertEqual(hasil.returncode, 0, hasil.stderr.decode())
        finally:
            shutil.rmtree(akar, ignore_errors=True)

    def test_kit_json_rusak_fail_open(self):
        akar = buat_repo(isi_kit="{rusak")
        try:
            ganti_branch(akar, "sprint-03/admin/BE-1")
            hasil = panggil(payload_tulis(os.path.join(akar, "mobile", "x.go"), akar), akar)
            self.assertEqual(hasil.returncode, 0)
            self.assertIn("PERINGATAN", hasil.stderr.decode())
        finally:
            shutil.rmtree(akar, ignore_errors=True)

    def test_repo_tanpa_commit(self):
        akar = buat_repo(commit=False)
        try:
            git(akar, "symbolic-ref", "HEAD", "refs/heads/sprint-03/admin/BE-1")
            hasil = panggil(payload_tulis(os.path.join(akar, "mobile", "x.go"), akar), akar)
            self.assertEqual(hasil.returncode, 2, hasil.stderr.decode())
        finally:
            shutil.rmtree(akar, ignore_errors=True)


@unittest.skipUnless(shutil.which("sh"), "sh tidak tersedia")
class UjiPembungkus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.akar = buat_repo()
        ganti_branch(cls.akar, "sprint-03/admin/BE-1")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.akar, ignore_errors=True)

    def lewat_sh(self, relatif, env=None, sh=None):
        berkas = os.path.join(self.akar, *relatif.split("/"))
        return panggil(payload_tulis(berkas, self.akar), self.akar, [sh or "sh", PEMBUNGKUS], env)

    def test_meneruskan_stdin_dan_exit_code(self):
        self.assertEqual(self.lewat_sh("admin/x.go").returncode, 0)
        hasil = self.lewat_sh("mobile/x.go")
        self.assertEqual(hasil.returncode, 2, hasil.stderr.decode())
        self.assertEqual(hasil.stdout, b"")
        self.assertIn("scrum-kit", hasil.stderr.decode())

    def test_tanpa_interpreter_fail_open(self):
        kosong = tempfile.mkdtemp(prefix="kit-path-")
        try:
            env = dict(LINGKUNGAN, PATH=kosong)
            hasil = self.lewat_sh("mobile/x.go", env=env, sh=shutil.which("sh"))
            self.assertEqual(hasil.returncode, 0, hasil.stderr.decode())
            self.assertIn("PERINGATAN", hasil.stderr.decode())
        finally:
            shutil.rmtree(kosong, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
