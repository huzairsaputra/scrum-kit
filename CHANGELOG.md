# Changelog

All notable changes to scrum-kit. Versions follow [Semantic Versioning](https://semver.org/):
a breaking change to `.claude/kit.json`, a command name, or an agent name bumps the major version.

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
