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
- Prompt agen memuat ID item dan aturan bagian "Keluaran gate" di bawah; agen menulis laporannya ke `<dokumen.laporan>/<agen>-<id-item>.md`.
- Hasil agen dibaca dari keluaran perintah itu (kamu diberi tahu saat prosesnya selesai; jangan
  polling). Laporan yang melanggar bagian "Keluaran gate" diperlakukan sama seperti agen yang belum
  selesai: kembalikan.
- CLI terkena batas pemakaian (*usage/session limit*) atau gagal → Anthropic API. Tool Agent/subagen
  hanya dipakai bila CLI dan Anthropic API sama-sama habis atau gagal, atau bila pengguna memintanya
  di sesi ini. Bila sudah terlanjur memakai subagen, laporkan ke pengguna dan pindah ke CLI.
- `claude -p` tidak bisa memberi persetujuan tulis `.claude/**`. Agen (terutama `platform-tooling`)
  yang perlu mengubah berkas di `.claude/` menulis berkas lain dulu, lalu melaporkan isi utuh berkas
  `.claude/` itu; kamu yang menulisnya di sesi interaktif (dengan persetujuan) dan meng-commit-nya.

## Keluaran gate

Berlaku untuk setiap peran yang menjalankan gate:

- Jalankan hanya gate yang terdefinisi di `gate.*`, persis seperti tertulis, masing-masing sendiri
  tanpa tambahan apa pun di belakangnya, dan tempel keluaran aslinya di laporan.
- Gate yang memuat sintaks shell (`$(...)`, `&&`, pipe) dijalankan sebagai `bash -c '<gate>'`.
- Gate yang tidak dikonfigurasi dilaporkan "tidak dikonfigurasi": bukan kegagalan, dan N/A di
  checklist DoD.
- Laporan yang berisi ringkasan, bukan keluaran asli, dikembalikan.

## Cara merge

Selalu merge commit, tanpa squash, rebase, atau fast-forward, agar `/scrum-kit:rilis` bisa melacak
hotfix yang belum di-back-merge.

- Merge butuh run CI proyek yang sukses pada SHA HEAD MR persis. "Tanpa check" tidak pernah hijau:
  GitHub melaporkan `mergeStateStatus` = `CLEAN` pada repo tanpa check wajib walau tidak ada pipeline
  yang berjalan. GitHub: `gh run list --commit <sha>` menampilkan run yang sukses; GitLab: head
  pipeline MR punya `sha` = SHA HEAD dan status `success`.
- Tunggu run dengan satu perintah yang memblokir (`gh run watch <id> --exit-status`, atau satu loop
  polling dalam satu panggilan shell), bukan giliran model berulang. Dalam beberapa menit tidak muncul
  run untuk SHA HEAD → berhenti dan tanya manusia. Hanya manusia yang boleh mengizinkan CI dipicu
  manual (`gh workflow run <file> --ref <branch>`, GitLab "Run pipeline"), dan hanya run sukses pada
  SHA HEAD itu yang dihitung.
- GitLab: `detailed_merge_status` = `mergeable`, merge dengan `sha` = HEAD MR yang sudah diperiksa dan
  `squash` = false.
- GitHub: `gh pr view <n> --json mergeStateStatus` = `CLEAN` (tidak cukup tanpa run CI di atas), lalu
  `gh pr merge <n> --merge --match-head-commit <sha>`.
- Sebelum merge, pastikan pengaturan forge tidak mengalahkan aturan ini: GitLab `merge_method` proyek =
  `merge` dan `squash_option` ≠ `always`; selain itu berhenti dan laporkan.
- Status `not_approved` (GitLab), atau `BLOCKED` dengan `gh pr view <n> --json reviewDecision` =
  `REVIEW_REQUIRED` (GitHub), berarti forge mewajibkan approval: minta manusia memberi approval di
  forge. `BLOCKED` karena hal lain (check wajib pending/gagal, percakapan belum diselesaikan) →
  laporkan penghambatnya.
- Jangan pernah memakai `--admin` atau melewati proteksi branch.
- Sesudah merge: `git fetch origin`; untuk tiap branch lokal item yang di-merge, hanya bila
  `git merge-base --is-ancestor <branch> origin/<tujuan MR>` sukses: `git worktree remove <worktree>`,
  `git branch -D <branch>`, dan `git push origin --delete <branch>`. Selain itu simpan branch dan
  worktree-nya, lalu laporkan.

### Mode lokal (tanpa remote)

Bila `git remote` kosong, tidak ada forge. Nyatakan "Mode lokal: tidak ada remote; pemeriksaan forge
dilewati" di laporan, lalu:

- Syarat CI pada SHA HEAD diganti `gate.ci` lokal yang hijau pada HEAD yang akan di-merge; keluarannya
  ditempel di laporan. Pemeriksaan forge (status merge, approval, pengaturan merge) dilewati.
- Merge tetap merge commit, secara lokal: `git switch <tujuan>` lalu `git merge --no-ff <branch>`.
  Aturan persetujuan sama dengan merge lewat MR (mis. branch integrasi sprint ke `branch.basis` hanya
  atas persetujuan PO).
- Sesudah merge, hanya bila `git merge-base --is-ancestor <branch> <tujuan>` sukses:
  `git worktree remove <worktree>` dan `git branch -D <branch>`. Tidak ada `git push`, termasuk
  `git push origin --delete`. Selain itu simpan branch dan worktree-nya, lalu laporkan.
