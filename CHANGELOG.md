# Changelog

All notable changes to scrum-kit. Versions follow [Semantic Versioning](https://semver.org/):
a breaking change to `.claude/kit.json`, a command name, or an agent name bumps the major version.

## v1.3.0 — 2026-11-07

Enam perbaikan dari uji end-to-end, di titik-titik tempat agen harus menebak atau berhenti.

- **Peluncur Python di gate:** `kit-init` memilih peluncur yang benar-benar jalan lewat
  `hooks/cari-python.sh --peluncur` (`python3`, `python`, lalu `py -3`; layak hanya bila `--version`
  mencetak versi Python 3). Di Windows `python` sering stub Microsoft Store yang keluar dengan kode 49.
  Gate `ci`/`test`/`build` ditulis dengan peluncur itu dan pilihannya dijelaskan; berkas CI proyek
  tidak diubah, gate lokal hanya berbeda di peluncur.
- **Sprint, dokumen ter-commit:** langkah 0.3 baru memastikan backlog sprint, `docs/requirements/`, dan
  rencana mingguan sudah ter-commit di branch basis sebelum worktree pertama dibuat. Bila belum,
  orkestrator menunjukkan daftarnya dan, sesudah dikonfirmasi, meng-commit hanya berkas itu. Branch
  integrasi dibuat dari basis lokal itu; basis tidak di-push.
- **Sprint dan QA, bentuk item QA:** item QA terpisah (`Menguji: <ID>`) mendapat branch dan MR sendiri
  di atas branch item yang diujinya; item implementasi tanpa item QA mendapat MR dari branch-nya
  sendiri dengan catatan "tanpa item QA"; item QA tanpa implementasi (mis. fixture) bercabang dari
  integrasi. Branch dan laporan memakai ID item itu sendiri. Model lama (QA di item implementer) tetap.
- **`worktree-new.sh`:** `--modul` opsional. Pada `kit.json` dengan `modul` kosong, `--modul` ditolak
  dengan pesan "proyek ini tidak punya modul; hilangkan --modul"; `/sprint` dan `/hotfix` menyebut
  untuk menghilangkannya.
- **Definition of Done:** butir boleh ditandai "tidak berlaku" hanya dengan alasan di dokumen serah
  terima sprint dan persetujuan PO, tidak pernah diam-diam (bagian baru di templat serah terima, butir
  baru di checklist MR). Dokumentasi API publik ditulis implementer modul sebagai docstring; perubahan
  README adalah item terpisah milik `platform-tooling` (`README.md` masuk wilayah `tooling` contoh).
- **Mode lokal:** tanpa remote (`git remote` kosong), `/sprint` melewati pemeriksaan forge dengan pesan
  eksplisit, membuat branch integrasi lokal dari basis, me-merge branch item secara lokal dengan merge
  commit, dan me-merge integrasi ke basis secara lokal sesudah PO menyetujui; tidak ada yang di-push.
  Tercantum juga di `docs/alur-bersama.md` dan kedua README. `worktree-new.sh` tidak lagi
  memperingatkan "fetch gagal" tanpa remote.
- Self-test hook: 37 → 44 uji.

Proyek yang sudah memasang kit: salin ulang `scripts/kit/worktree-new.sh`, lalu jalankan
`/scrum-kit:kit-init --perbarui` untuk menyisipkan teks DoD baru ke `CLAUDE.md`, bagian "Butir DoD
tidak berlaku" ke serah terima, dan `README.md` ke wilayah `tooling`.

## v1.2.1 — 2026-11-06

Correctness fixes found by running real sprints (Claude Code and Codex CLI) against the same
process; no new features.

- **Merging:** a merge needs a successful CI run on the MR's exact head SHA. "No checks" is never
  green: GitHub reports `CLEAN` on a repository without required checks even when nothing ran.
  Wait for CI with one blocking command (`gh run watch`); when no run appears, stop and ask a human,
  who alone may start CI by hand.
- **Sprint:** step 0 checks the base locally and on the forge; one draft MR per item, from the QA
  branch, marked ready only after a CLEAN review and green CI; items that edit the same file run one
  after the other; an item that needs a decision outside its scope is marked blocked, asked once,
  and the sprint goes on; the integration MR opens only when at least one item merged.
- **Review:** the reviewer diffs against the MR target (`origin/<branch.integrasi>`, or the hotfix
  target), leaves the reports folder out of its diff, and reads reports only after its verdict.
- **Gates:** run only configured gates, exactly as written, nothing appended; shell syntax goes
  through `bash -c`; an unconfigured gate is "not configured", not a failure.
- **Cleanup:** item branches are deleted, locally and on the remote, only after
  `git merge-base --is-ancestor` confirms they are merged.
- A negative authorization test is required only when the item touches authentication,
  authorization, endpoints or personal data. The example config keeps module implementers out of
  `{modul}/**/*_test.go`.

## v1.2.0 — 2026-11-05

Fixes from a whole-repo audit (13 findings) and an independent review of those fixes.

- **Hook:** agents may write their own reports under `dokumen.laporan`. `platform-tooling` may also write
  the backlog, handover, and code-debt docs. Before, every agent report was blocked. Document paths match
  by regex: `{nn}` and `{n}` only accept digits, and a malformed `dokumen` key never opens other paths.
- **Hook:** `branch.wilayah` must be a string with `{wilayah}` as one whole segment between `/`. Other
  patterns warn and skip the check; `worktree-new.sh` refuses them; `kit-init --perbarui` offers a
  migration. The unused list form and the never-sent `MultiEdit` tool were removed.
- **Dispatch:** `env -u ANTHROPIC_API_KEY claude -p …`, and `panggil_llm.py` runs the `claude` CLI
  without that key. A key in the environment made `claude -p` bill the API instead of the subscription,
  so the CLI fallback failed exactly when the API was out of credit.
- **Reports:** every agent writes `<dokumen.laporan>/<agent>-<item-id>.md`, so two `module-dev`
  instances no longer collide on merge.
- **`worktree-new.sh`:** `--base=HEAD` now means the caller's worktree, not the main one. A new worktree
  without sparse paths no longer inherits the caller's sparse checkout. Both are covered by new tests.
- **`panggil_llm.py`:**
  - a Gemini answer cut off (`finishReason` ≠ `STOP`) falls through to the next backend;
  - `--json` is enforced on every backend, and an answer that is not JSON falls through;
  - stdin is read as UTF-8 on Windows;
  - `--sistem` without a value prints usage instead of crashing.
- **Commands:** the agent dispatch and merge rules live once, in `docs/alur-bersama.md`, instead of in
  three commands.
- Hook self-test: 28 → 37 tests.

## v1.1.0 — 2026-11-05

- `/scrum-kit:hotfix` now has two paths, picked up front. The **normal** path is a small change approved
  by the product owner, to `branch.basis`. The **emergency** path is a real hotfix for
  a production incident (outage, open security hole, data being corrupted or leaked):
  - worktrees are cut from `branch.rilis` (or `branch.basis` when `rilis` is empty);
  - minimal scope, only the root cause;
  - a regression test with red-before and green-after evidence;
  - additive, backward-compatible migrations only, so no downtime;
  - merge to production only on the product owner's approval in chat;
  - merge back into base, a patch tag, and a post-incident review.

  A bug that can wait for the release schedule is a coldfix: it goes to the sprint backlog.
- New `/scrum-kit:rilis [version] [schedule]`: scheduled promotion of `branch.basis` to `branch.rilis`.
  - Checks release readiness: base pipeline, staging deploy, half-done work, production checklist.
  - Refuses while a hotfix has not been merged back into base.
  - Assesses downtime from migrations and config; when needed, drafts a maintenance-window notice.
  - Proposes a semver version and writes the release notes.
  - Opens one MR/PR, merged only on the product owner's approval, then tags the release.
- Both paths of `/hotfix` now cut worktrees from the merge target (`--base=origin/<target>`). Before,
  the normal path branched from the running sprint's integration branch and carried unfinished sprint
  work into the hotfix MR.
- The normal `/hotfix` path's self-merge is now a written exception: the product owner's go-ahead that
  starts the hotfix is the merge approval, as long as the scope stays within it.
- Hotfix, merge-back, and release MRs always use a merge commit (no squash, rebase, or fast-forward),
  so `/rilis` can detect hotfixes not yet merged back. Merge steps are spelled out for GitLab and GitHub.
- `/rilis` freezes the release at a recorded base SHA on a `claude/rilis-<version>` branch, stops and
  reports when the schedule has not arrived yet, and resumes from the same MR when rerun.
- `kit-init` now asks for `branch.rilis`, also with `--perbarui` on configs that lack it, and spells
  out how to fill the `{{rilis}}` / `{{rilis_teks}}` template placeholders.
- Merges stop when forge settings would override the merge-commit rule (GitLab `merge_method`,
  `squash_option`) or when the forge requires approval; never `--admin`.
- A conflict during a hotfix merge-back stops the hotfix and is reported to a human.
- `docs/kit-json.md`, the `CLAUDE.md` and handover templates (new "last production release" line), and
  the `/sprint` rule about the release branch follow suit.

## v1.0.1 — 2026-11-05

- `kit-init` no longer writes a `Write(./**/.env)` deny rule. Claude Code ignores `Write(...)` in file
  permissions and warns on every start; `Edit(./**/.env)` already covers every file-editing tool.
  Existing projects can delete that line from `.claude/settings.json`.

## v1.0.0 — 2026-11-05

Scrum sprints for Claude Code agent teams, installable.

- Eight agent roles: `module-dev`, `shared-module-owner`, `api-contract-keeper`, `qa-test-engineer`,
  `code-reviewer`, `platform-tooling`, `security-auditor`, `spec-change-adapter`
- Per-branch file ownership: a `PreToolUse` hook blocks Write/Edit outside the agent's area, read from
  `.claude/kit.json` (28 self-tests)
- `/scrum-kit:kit-init`, `/scrum-kit:sprint <n>`, `/scrum-kit:hotfix <id> <description>`
- Definition of Done gate that runs the project's own CI commands; GitLab and GitHub
- Orchestrator dispatches heavy work to headless `claude -p` processes instead of in-session subagents
- `scripts/panggil_llm.py`: one LLM entry point for project scripts (Gemini → Anthropic → `claude` CLI)
- Optional Google Drive spec sync (DDL, ERD, changelog) per project
- MIT license

**Install**
```
/plugin marketplace add huzairsaputra/scrum-kit
/plugin install scrum-kit@scrum-kit
```

**Upgrading from the private 0.x kit:** the plugin was renamed. Replace the old plugin name with `scrum-kit` in
`.claude/settings.json` (`extraKnownMarketplaces`, `enabledPlugins`), in `CLAUDE.md`, and in any
`claude -p --agent` call. The model env var is now `SCRUM_KIT_ANTHROPIC_MODEL`. `kit.json` is unchanged.

One agent, one turf. The merge conflict that never happened has never woken anyone up.

## 0.x — 2026-10-16 to 2026-11-04 (private pre-release)

Built and used privately before the public release, under a different name.

- **0.4.1** — Orchestrator dispatches agents through headless `claude -p`, not subagents.
- **0.4.0** — One LLM backend order for every script, plus the `panggil_llm.py` helper.
- **0.3.0** — Session order in the `CLAUDE.md` template: CLI → API → desktop orchestrator.
- **0.2.0** — Agent work habits in the template: graph-first exploration, CPU-light tests, gate evidence in reviews.
- **0.1.0** — First version: agents, ownership hook, `kit-init`, `sprint`, `hotfix`, LF line endings.
