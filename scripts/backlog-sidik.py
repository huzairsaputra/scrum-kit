#!/usr/bin/env python3
"""Cetak sidik jari SHA-256 berkas backlog, dihitung sama seperti laporan kesiapan Lanewright
Backlog Check (backlog_check.py): SHA-256 isi berkas mentah dengan CRLF dibaca sebagai LF. BOM dan
CR tunggal tidak diubah, jadi hasilnya sama di Windows, macOS, dan Linux.

Dipakai gerbang kesiapan backlog /scrum-kit:sprint (docs/alur-bersama.md):

  PELUNCUR=$(sh "${CLAUDE_PLUGIN_ROOT}/hooks/cari-python.sh" --peluncur)
  $PELUNCUR "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-sidik.py" <berkas>   # cetak 64 karakter hex
  $PELUNCUR "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-sidik.py" --self-test

Exit 0: sukses; 2: argumen salah atau berkas tidak terbaca. Python 3.8+, hanya pustaka standar;
tidak menulis berkas apa pun.
"""

import hashlib
import os
import sys
import tempfile


def sidik(data):
    """SHA-256 (hex) dari bytes dengan CRLF sebagai LF."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sidik_berkas(path):
    with open(path, "rb") as f:
        return sidik(f.read())


def self_test():
    # SHA-256 standar untuk "" dan "abc" (FIPS 180-2).
    assert sidik(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert sidik(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sidik(b"a\r\nb\r\n") == sidik(b"a\nb\n") == hashlib.sha256(b"a\nb\n").hexdigest()
    assert sidik(b"a\rb") != sidik(b"a\nb"), "CR tunggal tidak diubah (sama dengan backlog_check.py)"
    assert sidik(b"\xef\xbb\xbfa") != sidik(b"a"), "BOM ikut dihitung (sama dengan backlog_check.py)"
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(b"| ID |\r\n|---|\r\n")
        assert sidik_berkas(path) == sidik(b"| ID |\n|---|\n")
    finally:
        os.remove(path)
    print("self-test OK")


def main(argv):
    if argv == ["--self-test"]:
        self_test()
        return 0
    if len(argv) != 1 or argv[0].startswith("-"):
        sys.stderr.write("Pemakaian: backlog-sidik.py <berkas> | --self-test\n")
        return 2
    try:
        print(sidik_berkas(argv[0]))
    except OSError as e:
        sys.stderr.write("backlog-sidik: berkas tidak terbaca: %s (%s)\n" % (argv[0], e.strerror or e))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
