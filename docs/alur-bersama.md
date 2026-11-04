# Alur bersama perintah orkestrasi

Dirujuk oleh `/scrum-kit:sprint`, `/scrum-kit:hotfix`, dan `/scrum-kit:rilis`. Aturan yang khusus
satu perintah tetap ditulis di perintah itu.

## Mendispatch agen

Setiap kali perintah menyebut agen `scrum-kit:<agen>`, jalankan agen itu sebagai proses Claude Code
CLI terpisah, **bukan** lewat tool Agent/subagen:

- Lewat Bash dengan `run_in_background`, dari dalam worktree item:
  `cd <worktree> && env -u ANTHROPIC_API_KEY claude -p --agent scrum-kit:<agen> --permission-mode auto "<prompt>"`.
  Prompt panjang atau berisi tanda kutip: tulis ke berkas di scratchpad, lalu
  `cd <worktree> && env -u ANTHROPIC_API_KEY claude -p --agent scrum-kit:<agen> --permission-mode auto < <berkas-prompt>`.
  `env -u` membuang key API dari lingkungan proses itu; bila key ada, `claude -p` menagih Anthropic
  API, bukan langganan CLI.
- Prompt agen memuat ID item; agen menulis laporannya ke `<dokumen.laporan>/<agen>-<id-item>.md`.
- Hasil agen dibaca dari keluaran perintah itu (kamu diberi tahu saat prosesnya selesai; jangan
  polling). Laporan tanpa keluaran gate diperlakukan sama seperti agen yang belum selesai: kembalikan.
- CLI terkena batas pemakaian (*usage/session limit*) atau gagal → Anthropic API. Tool Agent/subagen
  hanya dipakai bila CLI dan Anthropic API sama-sama habis atau gagal, atau bila pengguna memintanya
  di sesi ini. Bila sudah terlanjur memakai subagen, laporkan ke pengguna dan pindah ke CLI.
- `claude -p` tidak bisa memberi persetujuan tulis `.claude/**`. Agen (terutama `platform-tooling`)
  yang perlu mengubah berkas di `.claude/` menulis berkas lain dulu, lalu melaporkan isi utuh berkas
  `.claude/` itu; kamu yang menulisnya di sesi interaktif (dengan persetujuan) dan meng-commit-nya.

## Cara merge

Selalu merge commit, tanpa squash, rebase, atau fast-forward, agar `/scrum-kit:rilis` bisa melacak
hotfix yang belum di-back-merge.

- GitLab: `detailed_merge_status` = `mergeable`, merge dengan `sha` = HEAD MR yang sudah diperiksa dan
  `squash` = false.
- GitHub: `gh pr view <n> --json mergeStateStatus` = `CLEAN`, lalu
  `gh pr merge <n> --merge --match-head-commit <sha>`.
- Sebelum merge, pastikan pengaturan forge tidak mengalahkan aturan ini: GitLab `merge_method` proyek =
  `merge` dan `squash_option` ≠ `always`; selain itu berhenti dan laporkan.
- Status `not_approved` (GitLab), atau `BLOCKED` dengan `gh pr view <n> --json reviewDecision` =
  `REVIEW_REQUIRED` (GitHub), berarti forge mewajibkan approval: minta manusia memberi approval di
  forge. `BLOCKED` karena hal lain (check wajib pending/gagal, percakapan belum diselesaikan) →
  laporkan penghambatnya.
- Jangan pernah memakai `--admin` atau melewati proteksi branch.
