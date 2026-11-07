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
# Pemisah `/`: bash (MSYS) membaca backslash sebagai escape.
WORKTREE_NEW = os.path.join(os.path.dirname(AKAR_HOOK), "scripts", "worktree-new.sh").replace("\\", "/")

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
    "dokumen": {
        "backlog": "docs/sprints/sprint-{nn}-backlog.md",
        "laporan": "docs/sprints/reports/sprint-{nn}/",
        "serah_terima": "docs/sprints/serah-terima.md",
        "code_debt": "docs/sprints/code-debt-backlog.md",
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

    def test_laporan_agen_dari_wilayah_mana_pun(self):
        self.assertIzin(self.tulis("sprint-03/admin/BE-1", "docs/sprints/reports/sprint-03/module-dev-BE-1.md"))
        self.assertIzin(self.tulis("sprint-03/tests/QA-1", "docs/sprints/reports/sprint-03/qa-test-engineer-QA-1.md"))

    def test_laporan_hanya_folder_sprint_berangka(self):
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "docs/sprints/reports-palsu/x"))
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "docs/sprints/reports/sprint-x/y.md"))

    def test_backlog_dari_wilayah_modul_ditolak(self):
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "docs/sprints/sprint-03-backlog.md"))
        self.assertTolak(self.tulis("sprint-03/admin/BE-1", "docs/sprints/serah-terima.md"))

    def test_dokumen_sprint_dari_tooling(self):
        for relatif in ("docs/sprints/sprint-03-backlog.md", "docs/sprints/serah-terima.md", "docs/sprints/code-debt-backlog.md"):
            self.assertIzin(self.tulis("sprint-03/tooling/T-1", relatif))
        self.assertTolak(self.tulis("sprint-03/tooling/T-1", "docs/api/x.yaml"))

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

    def test_pola_wilayah_bukan_segmen_utuh_dilewati(self):
        # `sprint-03-admin-BE-1` akan terbaca wilayah `admin-BE`; hook memperingatkan, bukan menolak semua.
        for pola, branch in (("sprint-{nn}-{wilayah}-{id}", "sprint-03-admin-BE-1"), (["sprint-{nn}/{wilayah}/{id}"], "sprint-03/admin/BE-1")):
            kit = dict(KIT, branch=dict(KIT["branch"], wilayah=pola))
            akar = buat_repo(isi_kit=json.dumps(kit))
            try:
                ganti_branch(akar, branch)
                hasil = panggil(payload_tulis(os.path.join(akar, "mobile", "x.go"), akar), akar)
                self.assertEqual(hasil.returncode, 0, hasil.stderr.decode())
                self.assertIn("segmen utuh", hasil.stderr.decode())
            finally:
                shutil.rmtree(akar, ignore_errors=True)

    def kode_dokumen(self, dokumen, relatif):
        akar = buat_repo(isi_kit=json.dumps(dict(KIT, dokumen=dokumen)))
        try:
            ganti_branch(akar, "sprint-03/admin/BE-1")
            hasil = panggil(payload_tulis(os.path.join(akar, *relatif.split("/")), akar), akar)
            return hasil.returncode
        finally:
            shutil.rmtree(akar, ignore_errors=True)

    def test_dokumen_bukan_objek_tetap_menolak(self):
        self.assertEqual(self.kode_dokumen("docs/", "mobile/x.go"), 2)

    def test_nn_di_segmen_tengah_tidak_membuka_wilayah_lain(self):
        dokumen = {"laporan": "docs/{nn}/laporan/"}
        self.assertEqual(self.kode_dokumen(dokumen, "docs/api/v2/laporan/openapi.yaml"), 2)
        self.assertEqual(self.kode_dokumen(dokumen, "docs/03/laporan/module-dev-BE-1.md"), 0)

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


@unittest.skipUnless(shutil.which("sh"), "sh tidak tersedia")
class UjiCariPeluncur(unittest.TestCase):
    """cari-python.sh --peluncur: python3 → python → py -3; stub Microsoft Store (exit 49) dilewati."""

    STUB = '#!/bin/sh\necho "Python was not found; run without arguments to install from the Microsoft Store" >&2\nexit 49\n'
    PY_LAYAK = '#!/bin/sh\n[ "$1" = "-3" ] && [ "$2" = "--version" ] && echo "Python 3.12.0" && exit 0\nexit 9\n'

    def peluncur(self, berkas):
        palsu = tempfile.mkdtemp(prefix="kit-peluncur-")
        try:
            for nama, isi in berkas.items():
                jalur = os.path.join(palsu, nama)
                with open(jalur, "w", encoding="utf-8", newline="\n") as f:
                    f.write(isi)
                os.chmod(jalur, 0o755)
            sh = shutil.which("sh")
            # Direktori palsu di depan: python3/python/py asli di PATH tertutup oleh stub.
            env = dict(LINGKUNGAN, PATH=palsu + os.pathsep + os.path.dirname(sh))
            hasil = subprocess.run([sh, os.path.join(AKAR_HOOK, "cari-python.sh"), "--peluncur"], capture_output=True, env=env, timeout=60)
            return hasil.returncode, hasil.stdout.decode().strip()
        finally:
            shutil.rmtree(palsu, ignore_errors=True)

    def test_stub_store_dilewati_jatuh_ke_py_3(self):
        self.assertEqual(self.peluncur({"python3": self.STUB, "python": self.STUB, "py": self.PY_LAYAK}), (0, "py -3"))

    def test_python3_didahulukan(self):
        layak = '#!/bin/sh\necho "Python 3.11.2"\n'
        self.assertEqual(self.peluncur({"python3": layak, "python": layak, "py": self.PY_LAYAK}), (0, "python3"))

    def test_semua_stub_gagal(self):
        self.assertEqual(self.peluncur({"python3": self.STUB, "python": self.STUB, "py": self.STUB}), (1, ""))


# `which` mengikuti urutan PATH, jadi di Windows bisa mengembalikan System32\bash.exe (WSL), yang tidak
# memahami path Windows; kelas ini dilewati di situ alih-alih gagal.
BASH = shutil.which("bash")
BASH_WSL = bool(BASH) and os.path.normcase(BASH).endswith(os.path.normcase(os.path.join("system32", "bash.exe")))


@unittest.skipUnless(BASH and not BASH_WSL, "bash tidak tersedia atau bash WSL (perlu Git Bash di Windows); worktree-new.sh tidak diuji")
class UjiWorktreeNew(unittest.TestCase):
    def setUp(self):
        self.akar = buat_repo()
        self.kedua = self.akar + "-kedua"
        self.wt = os.path.join(os.path.dirname(self.akar), os.path.basename(self.akar) + "-wt")
        git(self.akar, "worktree", "add", "-q", "-b", "kerja", self.kedua)

    def tearDown(self):
        for d in (self.wt, self.kedua, self.akar):
            shutil.rmtree(d, ignore_errors=True)

    def jalankan(self, *argumen):
        return subprocess.run([BASH, WORKTREE_NEW, *argumen], cwd=self.kedua, capture_output=True, env=LINGKUNGAN, timeout=120)

    def skrip(self, *argumen):
        hasil = self.jalankan(*argumen)
        self.assertEqual(hasil.returncode, 0, hasil.stderr.decode(errors="replace"))
        return hasil

    def tanpa_modul(self):
        # Skrip membaca kit.json worktree pemanggil lebih dulu; tidak perlu di-commit.
        with open(os.path.join(self.kedua, ".claude", "kit.json"), "w", encoding="utf-8") as f:
            json.dump(dict(KIT, modul=[]), f)

    def test_tanpa_modul_tests_tanpa_opsi_modul(self):
        self.tanpa_modul()
        self.skrip("tests", "QA-1", "3", "--base=HEAD")
        self.assertTrue(os.path.isdir(os.path.join(self.wt, "tests-QA-1")))

    def test_tanpa_modul_opsi_modul_ditolak_dengan_pesan_jelas(self):
        self.tanpa_modul()
        hasil = self.jalankan("tests", "QA-1", "3", "--modul=admin", "--base=HEAD")
        self.assertEqual(hasil.returncode, 1)
        self.assertIn("proyek ini tidak punya modul; hilangkan --modul", hasil.stderr.decode(errors="replace"))
        self.assertFalse(os.path.exists(os.path.join(self.wt, "tests-QA-1")))

    def test_base_head_dari_worktree_kedua(self):
        git(self.kedua, "commit", "-q", "--allow-empty", "-m", "di worktree kedua")
        head_kedua = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.kedua, capture_output=True, text=True, env=LINGKUNGAN).stdout.strip()
        self.skrip("shared", "SH-1", "3", "--base=HEAD")
        sha = subprocess.run(["git", "rev-parse", "sprint-03/shared/SH-1"], cwd=self.akar, capture_output=True, text=True, env=LINGKUNGAN).stdout.strip()
        self.assertEqual(sha, head_kedua, "--base=HEAD harus HEAD worktree pemanggil, bukan worktree utama")

    def test_pemanggil_sparse_tidak_diwariskan(self):
        # `git worktree add` (>= 2.36) menyalin pola sparse worktree pemanggil ke worktree baru.
        for relatif in ("admin/a.go", "mobile/m.go"):
            os.makedirs(os.path.join(self.kedua, os.path.dirname(relatif)), exist_ok=True)
            open(os.path.join(self.kedua, relatif), "w").close()
        git(self.kedua, "add", "-A")
        git(self.kedua, "commit", "-q", "-m", "isi")
        git(self.kedua, "sparse-checkout", "set", "--cone", "admin")
        self.assertFalse(os.path.exists(os.path.join(self.kedua, "mobile", "m.go")), "prasyarat: pemanggil sparse")
        self.skrip("shared", "SH-2", "3", "--base=HEAD")
        self.assertTrue(os.path.isfile(os.path.join(self.wt, "shared-SH-2", "mobile", "m.go")), "wilayah tanpa SPARSE harus checkout penuh")


if __name__ == "__main__":
    unittest.main(verbosity=2)
