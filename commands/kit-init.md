---
description: Pasang scrum-kit di proyek ini — wawancara singkat, lalu buat .claude/kit.json, CLAUDE.md, skrip worktree, templat MR, dan kerangka dokumen sprint
argument-hint: "[--perbarui]"
---

# Pasang scrum-kit

Kamu memasang starter kit agen di repo yang sedang dibuka. Berkas sumber kit ada di
`${CLAUDE_PLUGIN_ROOT}` (spesifikasi `docs/kit-json.md`, templat di `templates/`, skrip di `scripts/`).
Baca `${CLAUDE_PLUGIN_ROOT}/docs/kit-json.md` lebih dulu — itu kontrak setiap kunci.

Argumen: `$ARGUMENTS` (`--perbarui` = `kit.json` sudah ada; tinjau ulang dan perbarui, jangan timpa buta).
Teks bebas lain di argumen adalah batasan dari manusia (mis. "jangan push", "non-interaktif") dan menang atas langkah di bawah.

**Izin:** Claude Code memperlakukan `.claude/**` sebagai berkas sensitif, sehingga penulisan `kit.json` dan `settings.json` selalu meminta persetujuan. Itu wajar; jelaskan singkat sebelum menulis. Pada sesi non-interaktif (`claude -p`) persetujuan itu tidak bisa diberikan: tulis berkas lain dulu, lalu laporkan isi kedua berkas `.claude/` utuh di laporan akhir agar manusia menyalinnya.

## 1. Kenali repo (tanpa bertanya)

- Akar git, remote (`git remote -v` → GitLab/GitHub, path proyek; kosong → mode lokal, lihat langkah 5),
  branch yang ada (`staging`? `main`?).
- Stack per direktori: `go.mod`/`go.work`, `composer.json` (versi Laravel/PHP), `package.json`,
  `pyproject.toml`/`requirements.txt`, `Dockerfile`, `docker-compose*.yml`.
- Calon modul: direktori aplikasi di akar (monorepo) atau satu modul (repo tunggal).
- Perintah gate yang SUDAH ada: target `Makefile`, `composer.json` scripts, `package.json` scripts,
  `.gitlab-ci.yml`/workflow. Utamakan perintah yang dipanggil CI.
- Peluncur Python untuk gate: `PELUNCUR=$(sh "${CLAUDE_PLUGIN_ROOT}/hooks/cari-python.sh" --peluncur)`.
  Skrip mencoba `python3`, `python`, lalu `py -3`; kandidat layak hanya bila `<kandidat> --version`
  jalan dan mencetak versi Python 3. Di Windows `python` sering berupa stub Microsoft Store yang keluar
  dengan kode 49 sebelum menjalankan apa pun, jadi jangan menganggap `python` jalan.
- `CLAUDE.md`, `.claude/` yang sudah ada (jangan hapus isinya; gabungkan).
- Jangan membaca `.env` mana pun.

**`--perbarui`: periksa `branch.wilayah` lebih dulu.** Sejak 1.0.0 hook hanya membaca pola berupa
string dengan `{wilayah}` sebagai satu segmen utuh di antara `/` (mis. `sprint-{nn}/{wilayah}/{id}`).
Pola lain membuat hook diam-diam berhenti memeriksa kepemilikan: peringatannya hanya di stderr dengan
exit 0, yang tidak terlihat oleh model maupun manusia. Bila pola tidak lolos, tunjukkan pola lama dan
usulan penggantinya, lalu tawarkan migrasi:
- list (mis. `["sprint-{nn}/{wilayah}/{id}"]`) → string pertamanya;
- pemisah `-` di sekitar `{wilayah}` (mis. `sprint-{nn}-{wilayah}-{id}`) → `/` (`sprint-{nn}/{wilayah}/{id}`).
Branch worktree lama yang memakai pola lama tidak cocok lagi dengan pola baru, sehingga hook juga tidak
membatasinya. Sebutkan ini di laporan, dan sarankan worktree itu dibuat ulang dengan `worktree-new.sh`
sesudah pekerjaannya di-merge atau dipindahkan.

## 2. Wawancara (AskUserQuestion, maksimal dua putaran)

Tanyakan hanya yang tidak bisa disimpulkan, dengan usulan hasil deteksi sebagai opsi pertama
"(Disarankan)":
1. Modul dan wilayah: daftar modul, apakah ada pustaka/skema bersama, apakah ada kontrak API.
2. Branch: basis MR (`staging` bila ada, selain itu `main`), branch produksi `branch.rilis` (mis. `main`
   bila basis `staging`; kosong bila produksi di-deploy dari basis), pola branch integrasi sprint.
   `branch.rilis` dipakai `/scrum-kit:rilis` dan jalur darurat `/scrum-kit:hotfix`; `--perbarui` pada
   `kit.json` tanpa `branch.rilis` juga menanyakannya.
3. Gate: perintah fmt/lint/build/test/dod per modul (usul dari langkah 1; bila belum ada, usulkan
   perintah stack bawaan dan catat bahwa CI harus memakai perintah yang sama).
   Gate (`ci`, `test`, `build`, dan lainnya) yang memanggil Python ditulis dengan `$PELUNCUR` dari
   langkah 1 (mis. `py -3 -m pytest`, bukan `python -m pytest`). Sebutkan di wawancara dan di laporan
   akhir peluncur yang dipilih dan alasannya (mis. "`python` di mesin ini stub Microsoft Store, exit
   49; dipakai `py -3`"). Berkas CI proyek yang memanggil `python` dibiarkan apa adanya; catat di
   laporan dan di tabel gate `CLAUDE.md` bahwa gate lokal hanya berbeda di peluncur. Tidak ada
   peluncur yang layak → tulis gate persis seperti di CI dan laporkan bahwa gate Python tidak bisa
   dijalankan di mesin ini.
4. Spesifikasi eksternal Google Drive: ID folder atau "tidak ada"; wajib atau opsional.
5. Aturan tambahan proyek (basis data bersama yang tak boleh disentuh, server dev yang tak boleh
   dinyalakan, wilayah DevOps yang tak boleh diubah).

## 3. Tulis berkas (di branch baru `claude/pasang-scrum-kit`)

| Berkas | Isi |
|---|---|
| `.claude/kit.json` | Hasil langkah 1–2, mengikuti `docs/kit-json.md` persis. Wilayah `tooling` memuat `README.md`: perubahan README adalah item milik `platform-tooling` (Definition of Done di `CLAUDE.md`). |
| `CLAUDE.md` | Dari `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md`; isi semua `{{...}}` (`{{rilis_teks}}` = spasi lalu ``maupun `<branch.rilis>` ``, mis. `` maupun `main` `` dengan spasi pembuka; bila `branch.rilis` kosong, `{{rilis_teks}}` dikosongkan dan `` `{{rilis}}`, `` dihapus), hapus komentar `/kit-init`. Bila `CLAUDE.md` sudah ada, sisipkan bagian yang belum ada; jangan buang aturan lama. |
| `scripts/kit/worktree-new.sh` | Salin dari `${CLAUDE_PLUGIN_ROOT}/scripts/worktree-new.sh` (agar tim tanpa plugin pun bisa memakainya). |
| `.gitlab/merge_request_templates/Default.md` (GitLab) atau `.github/pull_request_template.md` (GitHub) | Dari `templates/merge_request.md`, kecuali templat proyek sudah ada. |
| `<dokumen.backlog>` sprint 1, `<dokumen.serah_terima>`, `<dokumen.code_debt>` | Dari `templates/` (`backlog.md`, `serah-terima.md`, `code-debt.md`); hanya bila belum ada. Ganti `{{nn}}` dengan `01` (nama berkas dan isi). |
| `.claude/settings.json` | Gabungkan (jangan timpa): `extraKnownMarketplaces.scrum-kit` (`{"source": {"source": "github", "repo": "huzairsaputra/scrum-kit"}}`), `enabledPlugins["scrum-kit@scrum-kit"]: true`, dan `permissions.deny` untuk `Read(./**/.env)` dan `Edit(./**/.env)` (aturan Edit mencakup semua tool penyunting berkas; aturan `Write(...)` diabaikan Claude Code). |
| `.gitignore` | Pastikan `.env`, `.env.*`, dan `*.env` diabaikan, kecuali contoh (`!.env.example`, `!.env.*.example`). Berkas env yang SUDAH ter-track (`git ls-files '*.env*' '.env*'`, selain contoh) tidak terlindungi `.gitignore`: jangan dibaca, jangan dihapus — catat sebagai utang `SEC` di `dokumen.code_debt` dan laporkan ke manusia (rotasi rahasia + `git rm --cached` adalah keputusannya). |

## 4. Verifikasi

- Interpreter: `PY=$(sh "${CLAUDE_PLUGIN_ROOT}/hooks/cari-python.sh")`. Gagal → laporkan bahwa hook kepemilikan TIDAK akan aktif di mesin ini sampai Python 3 terpasang (jangan anggap verifikasi lulus).
- `kit.json` valid JSON: `"$PY" -c "import json;json.load(open('.claude/kit.json',encoding='utf-8'))"`.
- Hook: di branch contoh yang cocok `branch.wilayah` (buat sementara, hapus lagi), kirim stdin
  `{"tool_name":"Write","tool_input":{"file_path":"<path di luar wilayah>"},"cwd":"<akar>"}` ke
  `sh "${CLAUDE_PLUGIN_ROOT}/hooks/jalankan.sh"` → exit 2; path di dalam wilayah → exit 0.
- `bash -n scripts/kit/worktree-new.sh`.
- `gate.ci` dijalankan sekali; laporkan hasilnya apa adanya (merah bukan alasan mengubah gate).

## 5. Selesai

Commit (bahasa sesuai jawaban, akhiri dengan baris `Co-Authored-By` dari harness). Push branch dan
tawarkan MR ke `branch.basis` — kecuali argumen melarangnya. `git remote` kosong (mode lokal, seperti
`/scrum-kit:sprint`): jangan push dan jangan tawarkan MR; tulis "Mode lokal: tidak ada remote; push
dan MR dilewati", lalu sebutkan perintah merge lokal untuk manusia: `git switch <branch.basis>` lalu
`git merge --no-ff claude/pasang-scrum-kit`. Laporkan ringkas: wilayah yang terbentuk, gate, hasil
verifikasi, dan hal yang masih harus diputuskan manusia. Jangan merge sendiri.
