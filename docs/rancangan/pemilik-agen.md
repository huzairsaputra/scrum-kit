# Design: agent owners (`pemilik`) in scrum-kit 1.6.0

Status: **draft for the product owner's decision** (15 Nov 2026). No code yet. Written fresh for scrum-kit (MIT); no
text or code is copied from any other product. Indonesian version: [pemilik-agen.id.md](pemilik-agen.id.md).

## 1. Goal

Every agent region (`wilayah.<name>`) gets **one human owner** with a forge account. The owner reviews and approves the
merge requests in that region, receives the escalations of that region's agent, and is named in the backlog. The input
is the **Agent Owner Form** (one row per position: position, name, forge account, regions held, who approves).

Deliberate limits:

- It applies **per repository**. A project of four repositories has four `kit.json` files; one person may appear in
  several. Approvals across repositories (for example an API contract change touching backend and frontend) are out of
  scope, and the docs say so.
- Ownership changes through a **handover** (one block that is updated, with the event recorded in the handover
  document), not through blocks per period.
- The orchestrator stays **one person**; the final merge is done by the orchestrator or the product owner.

## 2. Shape in `kit.json`

```json
"pemilik": {
  "backend-admin":  { "nama": "Name A", "akun_forge": "user-a", "wilayah": ["admin"] },
  "backend-mobile": { "nama": "Name B", "akun_forge": "user-b", "wilayah": ["mobile", "bersama"] },
  "devops":         { "nama": "Name C", "akun_forge": "user-c", "wilayah": ["tooling", "skema"] }
},
"persetujuan_pemilik": "peringatan"
```

scrum-kit keeps its Indonesian key names.

| Key | Required | Meaning |
|---|---|---|
| `pemilik.<position>` | no | One team position. The position name is free text (not a person's name) and is used in the backlog: `module-dev (backend-admin)`. |
| `.nama` | yes | Display name in merge requests and reports. |
| `.akun_forge` | yes | GitLab or GitHub username; used as the merge request reviewer and in CODEOWNERS. |
| `.wilayah` | yes | List of region names from `wilayah.*` (or module names for a `per_modul` region). |
| `persetujuan_pemilik` | no | `peringatan` (warning, the default) or `wajib` (required). See section 4. |

Without `pemilik`, scrum-kit behaves exactly as 1.5.0.

**Validation** (`/kit-init` and `worktree-new.sh`):

- one region held by two positions → **rejected**, except during a recorded handover (section 5);
- a region that does not exist in `wilayah.*` → rejected;
- a region with no owner → **warning**, never a block;
- an empty `akun_forge`, or the same account for two positions → warning (a small team may give one person two
  positions, but that person never approves a merge request they wrote).

## 3. Sprint flow

1. **Backlog:** the owner column reads `agent (position)` before the backlog is signed (the backlog fingerprint stays
   intact). Assignments made after signing go into the handover document, not the backlog.
2. **Sprint start:** when the project has none, `/sprint` **proposes** a CODEOWNERS block from `pemilik` (one path
   pattern per line, from the region's `tulis` globs). A human approves and commits it; agents never edit CODEOWNERS
   on their own.
3. **Item merge request:** the region's owner is set as the reviewer, and the description names the position.
4. **Merge:** see section 4. The author of a merge request never counts as an approver; when the owner wrote it, another
   owner or the product owner approves.

## 4. Approval

The same on every forge (GitLab, GitHub). Before a merge, the orchestrator reads the merge request's approvals through
the forge (GitLab MCP or `gh`) and checks that the region's owner, not the author, has approved.

- `peringatan` (default): when the owner's approval is missing, the merge may go ahead, and the warning is recorded in
  the merge request and the sprint report.
- `wajib`: the orchestrator **holds** the merge until the owner approves; when the owner is unavailable, the product
  owner approves and the reason is recorded.

When the project's forge also enforces code owner rules (CODEOWNERS with required approval), that rule applies next to
scrum-kit's check; scrum-kit does not depend on it.

## 5. Handover

When an owner changes (moves to another project, long leave):

- the `pemilik` block is updated, and the event (date, position, from whom to whom, regions) is recorded in
  `serah-terima.md`;
- during the transition, two positions may hold the same region **only** when that handover is recorded;
- open items of the previous owner **go back to the backlog** until the region is taken over in writing.

## 6. Files

`docs/kit-json.md`, `commands/kit-init.md`, `commands/sprint.md`, `commands/hotfix.md` (owner approval for hotfixes),
`templates/backlog.md`, `templates/serah-terima.md`, `templates/merge_request.md`, `scripts/worktree-new.sh`
(validation), `CHANGELOG.md`, `README.md`/`README.id.md`. Tests: a sample kit with and without `pemilik`, a doubly held
region, an unknown region, a region with no owner.

## 7. Product owner decisions

1. Key names `pemilik` and `persetujuan_pemilik`, default `peringatan`?
2. Ship in scrum-kit 1.6.0 (freeze 15 Dec, release 22 Dec) together with the run-mode fix and the merge option?
3. Pilot: one repository, one sprint, before all four.
