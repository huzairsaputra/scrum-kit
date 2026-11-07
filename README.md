<h1 align="center">scrum-kit</h1>

<p align="center">
  <strong>Scrum sprints for Claude Code agent teams.</strong><br>
  One agent, one turf. A hook enforces it, your CI decides when it's done.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="CHANGELOG.md"><img alt="Version" src="https://img.shields.io/badge/version-1.4.0-green.svg"></a>
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-orange.svg">
</p>

<p align="center"><strong>English</strong> · <a href="README.id.md">Bahasa Indonesia</a></p>

---

Parallel coding agents are fast until two of them edit the same migration. scrum-kit runs a sprint the
way a small Scrum team would: an orchestrator splits the backlog, each agent owns one area of the repo
on its own branch, tests are written by someone other than the implementer, and nothing merges until
an independent reviewer and your own CI agree.

It works with any stack (Go, Laravel, Node, Python, …). Nothing project-specific is hard-coded: every
project describes itself in one file, `.claude/kit.json`.

> The agent prompts, commands, and templates are written in **Bahasa Indonesia**. Claude reads them
> fine in any language; your team's docs and commit messages follow whatever you set in `CLAUDE.md`.

> **Want it in English, and on agents other than Claude Code?** [Lanewright](https://www.agensi.io/r/HUZAIRSAPUTRA?to=/skills/lanewright-sprint-workflow-for-ai-coding-agent-teams) is the paid,
> English rebuild of scrum-kit: one skill with five modes, an ownership check that also runs in Codex
> CLI and other agents, and a [public benchmark](https://github.com/huzairsaputra/lanewright). (Referral link; scrum-kit stays free
> and MIT.)

## What you get

- **Per-branch file ownership.** A `PreToolUse` hook reads the branch name (`sprint-03/admin/BE-1`) and
  `kit.json`, then blocks any Write/Edit outside that agent's area.
- **Eight agent roles:** `module-dev`, `shared-module-owner`, `api-contract-keeper`, `qa-test-engineer`,
  `code-reviewer`, `platform-tooling`, `security-auditor`, `spec-change-adapter`.
- **Definition of Done gate** that runs your project's own fmt/lint/build/test commands, the same ones
  CI runs. No second source of truth.
- **Headless dispatch.** The orchestrator runs heavy work as background `claude -p --agent …` processes
  in per-item git worktrees, not as subagents eating its own context.
- **GitLab or GitHub**, optional OpenAPI contract-first flow, optional Google Drive spec sync.

## Install

Requires Claude Code, git, Python 3 (`python3`, `python`, or `py`), and bash (Git Bash on Windows).

```
/plugin marketplace add huzairsaputra/scrum-kit
/plugin install scrum-kit@scrum-kit
```

Then, inside your project:

```
/scrum-kit:kit-init
```

It inspects the repo, asks a few questions (modules, base branch, gate commands), and writes
`.claude/kit.json`, `CLAUDE.md`, a worktree script, an MR/PR template, and sprint doc skeletons on a new
branch. The project's `.claude/settings.json` registers this marketplace, so teammates get the same
plugin just by trusting the folder.

## Commands

| Command | What it does |
|---|---|
| `/scrum-kit:kit-init` | Install the kit in a project (interview, then config + templates). `--perbarui` to revisit. |
| `/scrum-kit:sprint <n>` | Run one sprint: spec sync → foundation → contract → parallel implementation → QA → review → one integration MR/PR. |
| `/scrum-kit:hotfix <id> <description>` | Out-of-sprint work with the same gates. Normal path: a small change approved by the product owner, to the base branch. Emergency path: an urgent production fix with no downtime, merged to the release branch on the product owner's approval, then merged back into base. |
| `/scrum-kit:rilis [version] [schedule]` | Scheduled release from the base branch to production: readiness checks, downtime assessment, release notes, one MR/PR merged on the product owner's approval, then a tag. |

## How it works

```
kit.json ──► hook (who may write where) ──► worktree per item ──► agent on sprint-nn/<area>/<id>
                                                                          │
backlog ──► orchestrator ──► claude -p --agent scrum-kit:<role> ──────────┘
                    │
                    └──► gate (your CI commands) ──► code-reviewer ──► one MR/PR to base
```

**Local mode.** With no git remote (`git remote` is empty), `/scrum-kit:sprint` says so and skips the
forge checks, creates the integration branch locally from the base branch, merges each item branch
into it with a merge commit, and merges the integration branch into the base branch locally only after
the product owner approves. Nothing is pushed; a green local `gate.ci` stands in for forge CI. Each
sprint merge commit carries a merge record (`merge-<branch>.md` in the sprint reports folder: the gate
output and the ticked DoD checklist). The integration branch is kept until the product owner has
approved and it is merged into the base branch, then deleted; the handover is updated in that merge
commit.
`/scrum-kit:hotfix` and `/scrum-kit:rilis` work the same way (local merge commits after the product
owner approves, local tags), and `/scrum-kit:kit-init` commits its branch without pushing or offering
a merge request.

**Backlog readiness gate.** Before committing the sprint documents, `/scrum-kit:sprint` looks for
`docs/sprints/backlog-check-<nn>.md`, the readiness report written by the free
[Lanewright Planning](https://github.com/huzairsaputra/lanewright-planning) skill Backlog Check. No report: it says so once and asks whether to go on without one; the report is
never required. If the report's SHA-256 for the backlog differs from the current file, the report is
stale and the orchestrator asks once. A NOT READY verdict or an empty sign-off stops the sprint until
the product owner decides, and that decision goes into the handover document. The orchestrator never
fills the sign-off itself.

A minimal `kit.json` for a single-module Laravel app:

```json
{
  "proyek": "my-app",
  "stack": "laravel-12",
  "branch": { "basis": "main", "integrasi": "integrasi-{n}", "wilayah": "sprint-{nn}/{wilayah}/{id}" },
  "wilayah": {
    "app":    { "agen": "module-dev",          "tulis": ["app/**", "routes/**", "resources/**"], "kecuali": ["app/Models/**"] },
    "shared": { "agen": "shared-module-owner", "tulis": ["database/**", "app/Models/**"] },
    "tests":  { "agen": "qa-test-engineer",    "tulis": ["tests/**"] }
  },
  "gate": { "ci": "make ci", "test": "make test" },
  "dokumen": {
    "backlog": "docs/sprints/sprint-{nn}-backlog.md",
    "laporan": "docs/sprints/reports/sprint-{nn}/",
    "serah_terima": "docs/sprints/serah-terima.md",
    "code_debt": "docs/sprints/code-debt-backlog.md"
  },
  "forge": { "jenis": "github", "proyek": "you/my-app" }
}
```

Full contract: [`docs/kit-json.md`](docs/kit-json.md).

## Upgrading to 1.2.0

- The hook only reads a `branch.wilayah` that is a string with `{wilayah}` as one whole segment between
  `/` (e.g. `sprint-{nn}/{wilayah}/{id}`). A list or a pattern like `sprint-{nn}-{wilayah}-{id}` now
  turns ownership checks off with a warning (it never worked: every write was blocked). Run
  `/scrum-kit:kit-init --perbarui` to validate and migrate it.
- Agent reports are now `<dokumen.laporan>/<agent>-<item-id>.md` (was `<agent>.md`), so parallel
  instances no longer collide.
- Agents are dispatched with `env -u ANTHROPIC_API_KEY claude -p ...`, so the CLI uses your
  subscription instead of billing an API key found in the environment.

## Repository layout

| Path | Contents |
|---|---|
| `.claude-plugin/` | Plugin manifest; this repo is also its own marketplace. |
| `agents/` | The eight roles (`scrum-kit:<role>`). |
| `commands/` | `kit-init`, `sprint`, `hotfix`, `rilis`. |
| `hooks/` | `path_ownership.py` with its self-test, and a wrapper that finds a working Python. |
| `scripts/` | `worktree-new.sh` (worktree + branch, optional sparse checkout), `panggil_llm.py` (one LLM entry point for project scripts), `backlog-sidik.py` (backlog SHA-256 for the readiness gate). |
| `templates/` | `CLAUDE.md`, MR/PR template, backlog, handover, code-debt log. |
| `docs/` | `kit-json.md` (the `.claude/kit.json` contract) and `alur-bersama.md` (how commands dispatch agents and merge, shared by `sprint`, `hotfix`, `rilis`). |

## Test

```bash
py -I hooks/test_path_ownership.py
py -I scripts/panggil_llm.py --uji
py -I scripts/backlog-sidik.py --self-test
claude plugin validate .
```

For local development, run `claude --plugin-dir .` in a test project and `/reload-plugins` after edits.

## FAQ

**Is the hook a security boundary?** No. It fails open (no `kit.json`, a branch outside the pattern, or
a hook error all allow the write). Real enforcement is code review and branch protection; the hook
keeps honest agents in their lane.

**Does it create a Makefile or CI for me?** No. It uses the commands you already have, or records the
ones `platform-tooling` must create in the first sprint.

**Why per-agent permissions in `settings.json`?** Claude Code ignores `permissionMode` and per-agent
hooks for plugin agents, so permissions live in the project's `.claude/settings.json`.

## License

[MIT](LICENSE) © 2026 Huzair Saputra
