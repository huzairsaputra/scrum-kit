# Changelog

All notable changes to scrum-kit. Versions follow [Semantic Versioning](https://semver.org/):
a breaking change to `.claude/kit.json`, a command name, or an agent name bumps the major version.

## v1.1.0 — 2026-11-05

- `/scrum-kit:hotfix` now has two paths, picked up front. The **normal** path is unchanged: a small
  change approved by the product owner, to `branch.basis`. The **emergency** path is a real hotfix for
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
