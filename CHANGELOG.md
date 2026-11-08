# Changelog

All notable changes to scrum-kit. Versions follow [Semantic Versioning](https://semver.org/):
a breaking change to `.claude/kit.json`, a command name, or an agent name bumps the major version.

## v1.4.2 — 2026-11-08

Four fixes from the third test's approved-path sprints, at the points where the run had to guess.

- **Names with a semicolon in the "not applicable" approval:** the sign-off field separates names with
  `;`, but a proposed item can contain one. The orchestrator now matches the field against the report's
  own list of proposals first (a proposal whose full name appears counts as one item) and splits only
  what is left on `;`. The Planning skills (Sprint Planner, Backlog Check 1.0.3) also write proposal
  names without a semicolon.
- **Gate line when the verdict is NOT READY but the sign-off is filled:** it used to read "continued
  without sign-off", which is wrong there. It now has its own line with the approver, the date, the
  approved set and the reason. The line for an empty sign-off is unchanged.
- **Integration branch that already exists:** step 0.5 merged the base into it only when the backlog
  was missing, so role worktrees could see an older sign-off than the orchestrator. It now merges the
  base whenever the local base is not yet part of the integration branch.
- **Security audit and personal data:** "personal data" is whatever the SRS or backlog calls personal
  data, even when the whole team may see it. Skipping the audit for such an item needs the product
  owner's decision written in the handover, not the orchestrator's own judgment.

Upgrade: update the plugin. No change to `.claude/kit.json` or to project files.

## v1.4.1 — 2026-11-07

Seven fixes from a second end-to-end test, at the points where an agent had to guess or stop.

- **Definition of Done, "not applicable" approvals:** at the readiness gate (step 0.3) the
  orchestrator also reads the sign-off field `Butir DoD tidak berlaku (disetujui):` /
  `DoD not applicable (approved):` of the Backlog Check report. The items named there are approved
  only when the rest of the sign-off is filled and the fingerprint matches; otherwise, and for reports
  without the field, none are. An item marked "not applicable" during the sprint is accepted when it
  is in that set (recorded in the handover as approved in the readiness report), otherwise the product
  owner is asked once in chat. When nobody can answer, the DoD line is marked "menunggu persetujuan
  product owner" and not counted as met; the item branch still merges into integration if every other
  DoD item is met, but the sprint stops after the summary, lists every pending approval, and the
  integration branch is never merged into the base branch while one is pending. Rules in the gate
  section of `docs/alur-bersama.md`; the `CLAUDE.md` DoD text, the handover template and the merge
  request checklist follow.
- **QA pairing marker:** `Tests: <ID>` (written by the Sprint Planner) is accepted everywhere
  `Menguji: <ID>` is, in `/sprint` and `qa-test-engineer`.
- **Dispatch without the plugin installed for the CLI:** `/sprint` notes that `claude -p --agent
  scrum-kit:<agent>` answers "not found" then, and gives the retry with `--plugin-dir
  "${CLAUDE_PLUGIN_ROOT}"` and `env -u CLAUDE_CODE_SIMPLE`; if that still fails, the host's own agent
  tool is used and noted in the summary.
- **Expected red, one exception:** an old test that fails only because the item deliberately replaces
  the behaviour it tested may be red on the code item's branch, provided the QA item that rewrites it
  merges in the same sprint and the integration branch is green; the item merges through its QA
  branch. `module-dev` leaves such a test alone and names it in its report.
- **Contract step 6.1** runs only when `kontrak` is configured, like step 2.
- **Local mode:** every sprint or hotfix merge writes a merge record,
  `<dokumen.laporan>/merge-<source branch>.md` (gate output and the ticked DoD checklist), included in
  the merge commit (`git merge --no-ff --no-commit`, then `git commit --no-edit`). The integration
  branch is kept until the product owner has approved and merged, then deleted; the final merge commit
  also updates the handover, so no "waiting for approval" line stays behind.
- **Step 1:** an item labelled "foundation" that belongs to `module-dev` is not a step-1 item; step 1
  is for `shared-module-owner` and `platform-tooling` only.

No hook or script changes; hook self-test stays at 48 tests.

Projects that already installed the kit: copy the changed text by hand from the plugin's `templates/`:
the paragraph after the DoD list and point 5 of section 6 in `CLAUDE.md`, the intro of "Butir DoD tidak
berlaku" in the handover, and the last DoD line of the merge request template. `kit-init --perbarui`
only inserts sections that are missing, so it does not rewrite these existing paragraphs.

## v1.4.0 — 2026-11-07

A readiness gate in front of the sprint, local mode for every command, and prompt caching.

- **Sprint, backlog readiness gate:** a new step 0.3 reads `docs/sprints/backlog-check-<nn>.md`, the
  report the free Lanewright Planning skill Backlog Check writes. No report: the orchestrator says so
  once and asks whether to go on without it; the report is never required. A different SHA-256 for
  the backlog means the report is stale: it says so and asks once whether to continue or re-run the
  check. A NOT READY / BELUM SIAP verdict or an empty sign-off stops the sprint until the product owner
  decides; going on is recorded as "Gerbang laporan: dilanjutkan tanpa persetujuan, alasan ..." in the
  handover. A fresh, approved READY or READY WITH WARNINGS report passes and is noted there too. The
  orchestrator never fills the sign-off. Old steps 0.3–0.5 are now 0.4–0.6; step 0.4 also commits the
  report and the handover line. Reading rules in `docs/alur-bersama.md`, a "Gerbang laporan" line in
  the handover template, one paragraph in both READMEs.
- **`scripts/backlog-sidik.py`:** prints the SHA-256 of a file with CRLF read as LF, computed exactly
  like the `sha256` line of Backlog Check, so a report written on Windows matches on Linux and back.
  Standard library, Python 3.8+, run through the launcher from `hooks/cari-python.sh --peluncur`;
  has `--self-test`.
- **Local mode for `/hotfix`, `/rilis` and `kit-init`:** with no remote (`git remote` empty), `/hotfix`
  and `/rilis` skip the forge checks with an explicit message, merge locally with a merge commit after
  the product owner approves, tag locally, and push nothing. `/rilis` freezes the release on a local
  `claude/rilis-<version>` branch and uses the release notes as the merge commit message. The last
  step of `kit-init` no longer pushes or offers a merge request; it gives the local merge command
  instead. Also in `docs/alur-bersama.md`, rule 5 of the `CLAUDE.md` template, and both READMEs.
- **`panggil_llm.py`, prompt caching:** the Anthropic system prompt is sent as a block with
  `cache_control`, so repeated calls with the same system prompt read it from cache (5 minutes, or 1
  hour with `SCRUM_KIT_CACHE_TTL=1h`); `permintaan_batch` builds one Message Batches request with a
  cached system block (1-hour TTL by default); `SCRUM_KIT_TANPA_CACHE=1` (or `--tanpa-cache`,
  `cache=False`) turns caching off for tests that must measure uncached input. Token usage, cache
  writes and reads included, goes to stderr.
- Hook self-test: 44 → 48 tests.

Projects that already installed the kit: copy the changed text by hand from the plugin's `templates/`:
the "Gerbang laporan" line in the handover and the new local-mode wording in rule 5 of `CLAUDE.md`.
`kit-init --perbarui` only inserts sections that are missing, so it does not rewrite these existing
lines.

## v1.3.0 — 2026-11-07

Six fixes from an end-to-end test, at the points where an agent had to guess or stop.

- **Python launcher in the gate:** `kit-init` picks a launcher that actually runs through
  `hooks/cari-python.sh --peluncur` (`python3`, `python`, then `py -3`; usable only when `--version`
  prints a Python 3 version). On Windows `python` is often the Microsoft Store stub, which exits with
  code 49. The `ci`/`test`/`build` gates are written with that launcher and the choice is explained;
  the project's own CI file is left alone, so the local gate differs only in the launcher.
- **Sprint, documents committed:** a new step 0.3 makes sure the sprint backlog, `docs/requirements/`
  and the weekly plan are committed on the base branch before the first worktree is created. If not,
  the orchestrator lists them and, once confirmed, commits only those files. The integration branch is
  created from that local base; the base is not pushed.
- **Sprint and QA, item shapes:** a separate QA item (`Menguji: <ID>`) gets its own branch and merge
  request on top of the tested item's branch; an implementation item without a QA item gets its merge
  request from its own branch with a "tanpa item QA" note; a QA item without an implementation item
  (for example fixtures) branches from integration. Branches and reports use the item's own ID. The
  old model (QA works on the implementer's item) still applies.
- **`worktree-new.sh`:** `--modul` is optional. With a `kit.json` whose `modul` is empty, `--modul` is
  refused with the message "proyek ini tidak punya modul; hilangkan --modul", and `/sprint` and
  `/hotfix` say to leave it out.
- **Definition of Done:** an item may be marked "tidak berlaku" only with a reason in the sprint's
  handover document and the product owner's approval, never silently (new section in the handover
  template, new line in the merge request checklist). Public API documentation is written by the module
  implementer as docstrings; a README change is a separate item owned by `platform-tooling`
  (`README.md` is now in the example `tooling` region).
- **Local mode:** with no remote (`git remote` empty), `/sprint` skips the forge checks with an explicit
  message, creates the integration branch locally from the base, merges item branches locally with a
  merge commit, and merges integration into the base locally after the product owner approves; nothing
  is pushed. Also described in `docs/alur-bersama.md` and both READMEs. `worktree-new.sh` no longer
  warns "fetch failed" when there is no remote.
- Hook self-test: 37 → 44 tests.

Projects that already installed the kit: copy `scripts/kit/worktree-new.sh` again, add `README.md` to
the `tooling` region of `.claude/kit.json`, and copy the new DoD text and the "Butir DoD tidak berlaku"
section by hand from the plugin's `templates/` into `CLAUDE.md` and the handover. `kit-init --perbarui`
only inserts sections that are missing and leaves existing handover and merge request files alone, so it
does not bring these texts in.

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
