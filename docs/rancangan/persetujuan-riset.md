# Research participation: disclaimer, consent statement and report (draft)

Status: **draft for the product owner's review** (15 Nov 2026). Applies to every scrum-kit user: individuals, teams,
government agencies and private companies. Indonesian version: [persetujuan-riset.id.md](persetujuan-riset.id.md).
Placeholders in `[brackets]` are filled in after ethics approval; **nothing here is published before that**. This is
not legal advice; the final text is checked against the university's ethics requirements and Indonesia's Personal Data
Protection Law (UU 27/2022).

Decisions (15 Nov 2026): submissions go through a **GitHub issue form** in this repository; raw submissions are kept
**5 years**; private matters go through GitHub's private reporting channel, withdrawals through the issue itself.

## A. Disclaimer for the README

> **Research (optional).** scrum-kit sends nothing anywhere: no telemetry, no automatic reports. It is also part of a
> doctoral study on structured, specification-first workflows for AI coding agents. If you want to help, run
> `scripts/laporan-riset.py` after a sprint. It writes a short local file with numbers only, never your code,
> repository names, backlog text, people's names or secrets. Read it, edit it, and post it yourself through the
> **Research report** issue form. Issues are public. Taking part or not changes nothing about the kit or its support.

## B. Consent statement (in the issue form; every box must be ticked)

**Study:** [study title], doctoral research by Huzair Saputra, [university, programme]. Ethics approval: [number].

**What you share:** only the numbers in the attached report (section C) and the form answers you choose to give (role,
team size, sector: government / private / education / individual). Never source code, repository or project names,
backlog or ticket text, names, email addresses, forge accounts, secrets, or personal data of your users, customers or
citizens.

**Public by design:** a GitHub issue is public. Your report and the GitHub account you post from are visible to anyone.
Post from an account you are comfortable showing. The research dataset stores the report without your account name.

**How it is used:** to study how teams work with AI coding agents under a structured workflow. Research publications
report **aggregates** (for example averages per sector or team size), never one team or one person.

**Voluntary:** taking part is your free choice. If the report covers a team, every member whose work is counted has
agreed, and the data is **never used to assess anyone's performance**. A team lead collecting data from staff makes
sure that saying no has no consequence.

**Authorisation:** if you post on behalf of an organisation (government agency or company), you are allowed to share
these metrics, and they contain no classified or confidential information.

**Keeping and withdrawing:** raw submissions are kept for **5 years** and then deleted; published aggregates remain. To
withdraw, comment `withdraw` on your issue (or edit the report out): the issue is deleted and the report is removed from
every dataset not yet published. For anything you do not want to say in public, use the repository's private reporting
channel on GitHub.

**Conflict of interest:** the researcher is the author of scrum-kit and of a separate paid workflow pack. The paid pack
collects no data and is not part of this study.

- [ ] I have read this statement and agree that the attached report may be used as described.
- [ ] The report contains no code, names, accounts, secrets or personal data.
- [ ] If it covers a team or an organisation, I have the team's agreement and the organisation's permission.

## C. What `scripts/laporan-riset.py` writes (proposal)

One JSON file per sprint, created locally, never sent by the script:

| Field | Example | Source |
|---|---|---|
| `id_kiriman` | random UUID | generated on each run |
| `versi_kit` | `1.7.0` | plugin version |
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
user did not see in the file before posting.

## D. Issue form

Draft at [`laporan-riset.issue-form.yml`](laporan-riset.issue-form.yml), bilingual: sector, role, team size, the pasted JSON, and the
three required boxes of section B. It moves to `.github/ISSUE_TEMPLATE/` only after ethics approval, so nothing goes live by accident.
