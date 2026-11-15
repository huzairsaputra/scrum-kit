# Research participation: disclaimer, consent form and report (draft)

Status: **draft for the product owner's review** (15 Nov 2026). Applies to every scrum-kit user: individuals, teams,
government agencies and private companies. Indonesian version: [persetujuan-riset.id.md](persetujuan-riset.id.md).
Placeholders in `[brackets]` are filled in before publication. This is not legal advice; the final text is checked
against the university's ethics requirements and Indonesia's Personal Data Protection Law (UU 27/2022).

## A. Disclaimer for the README

> **Research (optional).** scrum-kit sends nothing anywhere: no telemetry, no automatic reports. It is also part of a
> doctoral study on structured, specification-first workflows for AI coding agents. If you want to help, you can run
> `scripts/laporan-riset.py` after a sprint. It writes a short local summary with numbers only (see below), never your
> code, repository names, backlog text, people's names or secrets. You read it, edit it, and submit it yourself through
> [the form] only after accepting the consent statement. Taking part or not changes nothing about the kit or support.

## B. Consent statement (shown in the submission form, ticked before sending)

**Study:** [study title], doctoral research by Huzair Saputra, [university, programme]. Ethics approval: [number].

**What is collected:** only the numbers in the report (section C), and the answers you choose to give in the form
(role, team size, sector: government / private / education / individual). No source code, repository or project
names, backlog or ticket text, names, email addresses, forge accounts, secrets, or any personal data of your users,
customers or citizens.

**How it is used:** to compare how teams work with AI coding agents under a structured workflow. Results are published
only as **aggregates** (for example averages per sector or team size), never per team or per person.

**Voluntary:** taking part is your free choice. If you submit data from a team, every team member whose work is counted
has agreed, and the data is **not used to assess anyone's performance**. A team lead collecting data from staff must
make sure saying no has no consequence.

**Authorisation:** if you submit on behalf of an organisation (government agency or company), you confirm that you are
allowed to share these metrics, and that they contain no classified or confidential information.

**Storage and withdrawal:** submissions are stored in [location] for [period] and then deleted. Each report carries a
random submission ID. Send that ID to [contact] to have your submission removed at any time before publication of the
aggregate it belongs to.

**Conflict of interest:** the researcher is the author of scrum-kit and of a separate paid workflow pack. The paid pack
collects no data and is not part of this data collection.

☐ I have read this statement and agree that the attached report may be used as described.

## C. What `scripts/laporan-riset.py` writes (proposal)

One JSON file per sprint, created locally, never sent by the script:

| Field | Example | Source |
|---|---|---|
| `id_kiriman` | random UUID | generated on each run |
| `versi_kit` | `1.6.0` | plugin version |
| `agen_platform` | `claude-code`, `codex`, `other` | asked once |
| `mode_jalan` | `claude-code`, `portable` | sprint summary |
| `ukuran_tim`, `jumlah_posisi` | `6`, `6` | `pemilik` count, no names |
| `jumlah_item`, `item_selesai` | `4`, `3` | backlog and merges |
| `dod_terpenuhi` | `5/7` per item | sprint report |
| `putaran_review`, `mr_ditolak` | counts | forge, no texts |
| `durasi_sprint_jam`, `durasi_mr_median_jam` | numbers | git and forge timestamps |
| `ci_gagal_sebelum_hijau` | count | forge |
| `persetujuan_pemilik_tercatat` | `true/false` per item, counted | forge |

Excluded by design: paths, branch names, commit messages, usernames, emails, timestamps finer than a day, anything the
user did not see in the file before submitting.
