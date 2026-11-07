# `.claude/kit.json` — konfigurasi proyek

Satu-satunya berkas yang membedakan satu proyek dari proyek lain. Hook kepemilikan, skrip
worktree, perintah `/sprint`, `/hotfix`, dan `/rilis`, serta semua agen membaca berkas ini; tidak ada nama
proyek, modul, atau perintah gate yang ditulis mati di plugin. `/kit-init` membuatnya lewat
wawancara; sesudahnya boleh disunting tangan (di-commit ke repo proyek).

## Contoh (proyek Go/Goravel tiga modul + pustaka bersama)

```json
{
  "proyek": "contoh-backend-api",
  "stack": "go-goravel",
  "branch": {
    "basis": "staging",
    "rilis": "main",
    "integrasi": "integrasi-{n}",
    "wilayah": "sprint-{nn}/{wilayah}/{id}"
  },
  "modul": ["admin", "mobile", "opd"],
  "wilayah": {
    "modul":    { "agen": "module-dev",          "tulis": ["{modul}/**"], "kecuali": ["{modul}/tests/**", "{modul}/**/*_test.go", "*/bootstrap/migrations.go"], "per_modul": true },
    "shared":   { "agen": "shared-module-owner", "tulis": ["shared/**", "*/bootstrap/migrations.go"] },
    "tests":    { "agen": "qa-test-engineer",    "tulis": ["*/tests/**", "**/*_test.go"] },
    "contract": { "agen": "api-contract-keeper", "tulis": ["docs/api/**"] },
    "tooling":  { "agen": "platform-tooling",    "tulis": [".claude/**", "scripts/**", "Makefile", ".gitlab-ci.yml", "*/Dockerfile", "*/.env.example", "README.md"] },
    "security": { "agen": "security-auditor",    "tulis": ["docs/security/**"] },
    "adaptasi": { "agen": "spec-change-adapter", "tulis": ["shared/**", "docs/api/**", "docs/db/**", "admin/**", "mobile/**", "opd/**"], "kecuali": ["*/tests/**", "**/*_test.go"] }
  },
  "checkout_bersama": ["shared/", "docs/", "scripts/"],
  "gate": {
    "ci": "make ci",
    "fmt": "make fmt-check",
    "lint": "make lint-{modul}",
    "build": "make build-{modul}",
    "siapkan_test": "make test-db-up && make migrate-test",
    "test": "make test-{modul}",
    "dod": "make dod-check-{modul}"
  },
  "kontrak": "docs/api/openapi-{modul}.yaml",
  "dokumen": {
    "backlog": "docs/sprints/sprint-{nn}-backlog.md",
    "laporan": "docs/sprints/reports/sprint-{nn}/",
    "serah_terima": "docs/sprints/serah-terima.md",
    "code_debt": "docs/sprints/code-debt-backlog.md"
  },
  "spek_eksternal": { "drive_folder_id": null, "wajib": false },
  "forge": { "jenis": "gitlab", "proyek": "contoh/backend-api" },
  "aturan_tambahan": [
    "Jangan menyalakan server HTTP aplikasi dalam kerja agen; verifikasi lewat test.",
    "Jangan pernah menjalankan migrasi/test terhadap basis data bersama."
  ]
}
```

## Arti setiap kunci

| Kunci | Wajib | Arti |
|---|---|---|
| `proyek` | ya | Nama pendek proyek (judul MR, laporan). |
| `stack` | ya | Label bebas (`go-goravel`, `laravel-12`, `node-express`, …). Agen memakainya untuk memilih idiom; tidak mengubah perilaku hook. |
| `branch.basis` | ya | Branch tujuan MR (biasanya `staging`; `main` bila tidak ada staging). |
| `branch.rilis` | tidak | Branch rilis (produksi). Hanya `/rilis` dan jalur darurat `/hotfix` yang membuka MR ke sini, dan merge-nya selalu menunggu persetujuan PO. Kosong = produksi di-deploy dari basis. |
| `branch.integrasi` | ya | Pola branch integrasi satu sprint. `{n}` = nomor sprint tanpa nol depan. |
| `branch.wilayah` | ya | Pola branch kerja agen (string). Wajib memuat `{wilayah}` sebagai **satu segmen utuh di antara `/`** (`sprint-{nn}/{wilayah}/{id}`, bukan `sprint-{nn}-{wilayah}-{id}`, karena nama wilayah bisa memuat `-`); pola lain ditolak `worktree-new.sh` dan dilewati hook dengan peringatan. `{nn}` = nomor sprint dua digit, `{id}` = ID item. Branch yang tidak cocok pola ini (mis. `main`, `staging`, `integrasi-*`, `claude/*`) **tidak dibatasi** hook — itu wilayah manusia/orkestrator. |
| `modul` | tidak | Daftar modul/aplikasi. Kosong untuk proyek satu modul. |
| `wilayah.<nama>.agen` | ya | Nama agen plugin yang memiliki wilayah itu. |
| `wilayah.<nama>.tulis` | ya | Glob path (relatif akar repo, `/`) yang boleh ditulis. |
| `wilayah.<nama>.kecuali` | tidak | Glob yang tetap ditolak walau cocok `tulis` (pengecualian menang). |
| `wilayah.<nama>.per_modul` | tidak | `true`: wilayah ini berlaku per modul. Nama wilayah di branch adalah nama modulnya (`sprint-03/admin/BE-1`), dan `{modul}` di glob diganti modul itu. |
| `wilayah.adaptasi` | bila Drive dipakai | Wilayah `spec-change-adapter`: tumpang tindih dengan skema, kontrak, dan kode modul, jadi selalu berjalan sendirian (barrier). Tidak perlu bila `spek_eksternal.drive_folder_id` kosong. |
| `checkout_bersama` | tidak | Direktori yang ikut ter-checkout di worktree sparse wilayah modul. Kosong/tidak ada = tanpa sparse-checkout. |
| `gate.*` | `ci` wajib | Perintah gate. `{modul}` diganti nama modul. Agen menjalankan persis perintah ini — CI harus memanggil perintah yang sama. Satu-satunya beda yang boleh: peluncur Python (`python3`, `python`, atau `py -3`) yang dipilih `/kit-init` karena berfungsi di mesin lokal; berkas CI tetap memakai peluncurnya sendiri. |
| `kontrak` | tidak | Lokasi kontrak API per modul. Kosong = proyek tanpa kontrak API (agen kontrak tidak dipakai). |
| `dokumen.*` | ya | Lokasi backlog, laporan agen, serah terima, dan backlog utang kode. Laporan agen ditulis ke `<dokumen.laporan>/<agen>-<id-item>.md` (mis. `module-dev-BE-1.md`), satu berkas per item agar instans paralel tidak bentrok. |
| `spek_eksternal.drive_folder_id` | tidak | ID folder Google Drive sumber spesifikasi (DDL, ERD, changelog). `null` = Langkah -1 `/sprint` dilewati. |
| `spek_eksternal.wajib` | tidak | `true`: `/sprint` BERHENTI bila Drive tak terbaca. `false`: lanjut dengan peringatan. |
| `forge.jenis` / `forge.proyek` | ya | `gitlab` (MCP GitLab) atau `github` (`gh`). Path proyek untuk MR/pipeline. |
| `aturan_tambahan` | tidak | Aturan keras khusus proyek; disalin ke `CLAUDE.md` dan dibaca semua agen. |

## Pencocokan path oleh hook

- Path dinormalisasi ke relatif akar repo dengan `/`.
- Cocok bila salah satu glob `tulis` cocok DAN tidak satu pun glob `kecuali` cocok
  (`fnmatch`; `*` juga melintasi `/`, jadi `*/tests/**` mencakup `a/b/tests/x`; `**/x` juga cocok dengan `x` di akar repo; di Windows perbandingan tanpa membedakan huruf besar/kecil).
- Dokumen agen selalu diizinkan, di luar `tulis`/`kecuali`: path di bawah `dokumen.laporan` untuk semua
  wilayah, ditambah `dokumen.backlog`, `dokumen.serah_terima`, dan `dokumen.code_debt` untuk wilayah
  yang `agen`-nya `platform-tooling`. `{nn}`/`{n}` di path dokumen cocok dengan nomor sprint mana pun (hanya digit:
  `{nn}` dua digit, `{n}` satu digit atau lebih); bagian lain path dokumen dibaca literal, bukan glob.
  `dokumen` yang bukan objek tidak membuka path apa pun.
- Berkas di luar repo (mis. memori atau scratchpad Claude) tidak diperiksa.
- Tidak ada `kit.json`, atau branch di luar pola `branch.wilayah`: hook mengizinkan.
- `branch.wilayah` kosong, bukan string, atau `{wilayah}`-nya bukan satu segmen utuh: hook
  memperingatkan dan mengizinkan (kepemilikan tidak diperiksa sampai polanya diperbaiki).
