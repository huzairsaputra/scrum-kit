# scrum-kit — starter kit agen pengembangan

> [English](README.md) · **Bahasa Indonesia**

Plugin Claude Code untuk proyek dengan stack apa pun (Go, Laravel, Node, Python, …). Isinya alur
kerja tim agen ala Scrum yang sudah dipakai di beberapa proyek produksi, tanpa hal yang ditulis mati
untuk satu proyek:

- **Wilayah kepemilikan per branch.** Hook menolak Write/Edit di luar wilayah agen, berdasarkan nama
  branch dan `.claude/kit.json`.
- **Delapan peran agen:** `module-dev`, `shared-module-owner`, `api-contract-keeper`,
  `qa-test-engineer`, `code-reviewer`, `platform-tooling`, `security-auditor`, `spec-change-adapter`.
- **Perintah:**
  - `/scrum-kit:kit-init`: memasang kit di sebuah proyek;
  - `/scrum-kit:sprint <n>`: menjalankan satu sprint;
  - `/scrum-kit:hotfix <ID> <deskripsi>`: perubahan di luar sprint, jalur biasa (perubahan kecil ke
    branch basis) atau jalur darurat (perbaikan mendesak ke produksi, lalu back-merge);
  - `/scrum-kit:rilis [versi] [jadwal]`: rilis terjadwal branch basis → branch rilis (produksi).
- **Gate Definition of Done** memakai perintah proyek sendiri, yaitu perintah yang sama yang
  dipanggil CI.
- **Sinkron spesifikasi Google Drive** bersifat opsional per proyek, lewat `spek_eksternal.drive_folder_id`.

> **Butuh versi berbahasa Inggris yang juga jalan di agen selain Claude Code?**
> [Lanewright](https://www.agensi.io/r/HUZAIRSAPUTRA?to=/skills/lanewright-sprint-workflow-for-ai-coding-agent-teams) adalah versi berbayar scrum-kit yang dibangun ulang dalam bahasa Inggris: satu
> skill dengan lima mode, pemeriksaan kepemilikan yang juga jalan di Codex CLI dan agen lain, dan
> [benchmark publik](https://github.com/huzairsaputra/lanewright). (Link referral; scrum-kit tetap gratis dan MIT.)

## Pasang

Prasyarat: Claude Code, git, Python 3 (`python3`, `python`, atau `py`), dan bash (Git Bash di Windows).

Di sesi Claude Code:

```
/plugin marketplace add huzairsaputra/scrum-kit
/plugin install scrum-kit@scrum-kit
```

Lalu, di repo proyek:

```
/scrum-kit:kit-init
```

Perintah ini mewawancarai Anda, lalu menulis `.claude/kit.json`, `CLAUDE.md`,
`scripts/kit/worktree-new.sh`, templat MR/PR, dan kerangka dokumen sprint ke branch
`claude/pasang-scrum-kit`. Setelah itu ia menawarkan MR (tanpa remote: tanpa push dan tanpa MR).
`.claude/settings.json` proyek ikut mendaftarkan marketplace ini, sehingga rekan tim cukup
mempercayai folder proyek untuk mendapatkan plugin yang sama.

### Catatan upgrade ke 1.2.0

- Hook hanya membaca `branch.wilayah` berupa string dengan `{wilayah}` sebagai satu segmen utuh di
  antara `/` (mis. `sprint-{nn}/{wilayah}/{id}`). List atau pola seperti `sprint-{nn}-{wilayah}-{id}`
  kini mematikan pemeriksaan kepemilikan dengan peringatan (dulu memblokir semua penulisan). Jalankan
  `/scrum-kit:kit-init --perbarui` untuk memvalidasi dan memigrasikannya.
- Laporan agen kini ditulis ke `<dokumen.laporan>/<agen>-<id-item>.md` (dulu `<agen>.md`).
- Dispatch agen memakai `env -u ANTHROPIC_API_KEY claude -p ...` agar CLI memakai langganan, bukan
  menagih key API (lihat `docs/alur-bersama.md`).

## Cara kerja

**Mode lokal.** Tanpa remote git (`git remote` kosong), `/scrum-kit:sprint` menyatakannya dan
melewati pemeriksaan forge, membuat branch integrasi secara lokal dari branch basis, me-merge tiap
branch item ke sana dengan merge commit, dan me-merge branch integrasi ke branch basis secara lokal
hanya sesudah product owner menyetujui. Tidak ada yang di-push; `gate.ci` lokal yang hijau menggantikan
CI forge. `/scrum-kit:hotfix` dan `/scrum-kit:rilis` bekerja dengan cara yang sama (merge commit lokal
sesudah product owner menyetujui, tag lokal), dan `/scrum-kit:kit-init` meng-commit branch-nya tanpa
push dan tanpa menawarkan MR.

**Gerbang kesiapan backlog.** Sebelum meng-commit dokumen sprint, `/scrum-kit:sprint` mencari
`docs/sprints/backlog-check-<nn>.md`, laporan kesiapan dari skill gratis Backlog Check
([Lanewright Planning](https://github.com/huzairsaputra/lanewright-planning)). Tanpa laporan, ia menyampaikannya sekali dan bertanya apakah lanjut tanpa laporan; laporan
ini tidak pernah wajib. SHA-256 backlog di laporan yang berbeda dari berkas saat ini berarti laporan
usang, dan orkestrator bertanya sekali. Putusan BELUM SIAP (NOT READY) atau blok persetujuan yang
kosong menghentikan sprint sampai product owner memutuskan, dan keputusan itu dicatat di serah
terima. Orkestrator tidak pernah mengisi blok persetujuan sendiri.

## Struktur

| Path | Isi |
|---|---|
| `.claude-plugin/plugin.json`, `marketplace.json` | Manifest plugin. Repo ini sekaligus menjadi marketplace-nya. |
| `agents/` | Delapan peran agen (nama berlingkup `scrum-kit:<agen>`). |
| `commands/` | `kit-init`, `sprint`, `hotfix`, `rilis`. |
| `hooks/` | `hooks.json`, `jalankan.sh` (memilih interpreter Python), `path_ownership.py` beserta self-test. |
| `scripts/worktree-new.sh` | Membuat worktree + branch wilayah, dengan sparse-checkout opsional. |
| `scripts/backlog-sidik.py` | SHA-256 backlog dengan CRLF dibaca sebagai LF, sama dengan laporan Backlog Check; dipakai gerbang kesiapan backlog `/scrum-kit:sprint`. |
| `scripts/panggil_llm.py` | Satu pintu pemanggilan LLM untuk skrip proyek: Gemini → Anthropic → CLI `claude` (lalu sesi Claude Desktop). Pustaka (`panggil_llm()`) atau CLI (prompt lewat stdin). Hanya stdlib; SDK `anthropic` opsional. |
| `templates/` | CLAUDE.md, templat MR/PR, backlog, serah terima, utang kode. |
| `docs/kit-json.md` | Kontrak `.claude/kit.json`. Baca ini sebelum menyunting konfigurasi proyek. |
| `docs/alur-bersama.md` | Cara mendispatch agen (CLI headless tanpa key API) dan cara merge, dipakai bersama `sprint`, `hotfix`, `rilis`. |

## Uji

```bash
py -I hooks/test_path_ownership.py
```

```bash
py -I scripts/panggil_llm.py --uji
```

```bash
py -I scripts/backlog-sidik.py --self-test
```

```bash
claude plugin validate .
```

Pengembangan lokal: `claude --plugin-dir .` di repo proyek uji, lalu `/reload-plugins` setelah berkas
plugin berubah.

## Batasan yang disengaja

- Hook bersifat *fail-open*: kit.json tidak ada, branch di luar pola, atau galat hook berarti
  path diizinkan. Penegakan keras tetap ada di review dan proteksi branch GitLab/GitHub.
- Kit tidak membuat Makefile/CI untuk Anda. Ia memakai perintah yang sudah ada, atau mencatat
  perintah yang harus dibuat `platform-tooling`.
- Agen plugin mengabaikan `permissionMode` dan hook per agen (batasan Claude Code). Izin diatur di
  `.claude/settings.json` proyek.

## Lisensi

[MIT](LICENSE) © 2026 Huzair Saputra
