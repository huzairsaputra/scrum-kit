# Alur bersama perintah orkestrasi

Dirujuk oleh `/scrum-kit:sprint`, `/scrum-kit:hotfix`, dan `/scrum-kit:rilis`. Aturan yang khusus
satu perintah tetap ditulis di perintah itu; cara membaca laporan gerbang kesiapan backlog
(`/scrum-kit:sprint`) dirinci di sini.

## Mendispatch agen

Setiap kali perintah menyebut agen `scrum-kit:<agen>`, jalankan agen itu sebagai proses Claude Code
CLI terpisah, **bukan** lewat tool Agent/subagen:

- Lewat Bash dengan `run_in_background`, dari dalam worktree item:
  `cd <worktree> && env -u ANTHROPIC_API_KEY claude -p --agent scrum-kit:<agen> --permission-mode auto "<prompt>"`.
  Prompt panjang atau berisi tanda kutip: tulis ke berkas di scratchpad, lalu
  `cd <worktree> && env -u ANTHROPIC_API_KEY claude -p --agent scrum-kit:<agen> --permission-mode auto < <berkas-prompt>`.
  `env -u` membuang key API dari lingkungan proses itu; bila key ada, `claude -p` menagih Anthropic
  API, bukan langganan CLI.
- Prompt agen memuat ID item dan aturan bagian "Keluaran gate" dan butir **Agen** di "Batas pemakaian" di bawah; agen menulis laporannya ke `<dokumen.laporan>/<agen>-<id-item>.md`.
- Hasil agen dibaca dari keluaran perintah itu (kamu diberi tahu saat prosesnya selesai; jangan
  polling). Laporan yang melanggar bagian "Keluaran gate" diperlakukan sama seperti agen yang belum
  selesai: kembalikan.
- CLI terkena batas pemakaian (*usage/session limit*) atau gagal → Anthropic API. Tool Agent/subagen
  hanya dipakai bila CLI dan Anthropic API sama-sama habis atau gagal, atau bila pengguna memintanya
  di sesi ini. Bila sudah terlanjur memakai subagen, laporkan ke pengguna dan pindah ke CLI.
  Yang dikerjakan sebelum dan sesudah pindah ada di "Batas pemakaian" di bawah.
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

Bila `git remote` kosong, tidak ada forge. Berlaku untuk `/scrum-kit:sprint`, `/scrum-kit:hotfix`,
dan `/scrum-kit:rilis` (rinciannya di bagian "Mode lokal" tiap perintah); `/scrum-kit:kit-init` pada
mode ini tidak push dan tidak menawarkan MR. Nyatakan "Mode lokal: tidak ada remote; pemeriksaan
forge dilewati" di laporan, lalu:

- Syarat CI pada SHA HEAD diganti `gate.ci` lokal yang hijau pada HEAD yang akan di-merge; keluarannya
  ditempel di laporan. Pemeriksaan forge (status merge, approval, pengaturan merge) dilewati.
- Merge tetap merge commit, secara lokal: `git switch <tujuan>` lalu `git merge --no-ff <branch>`.
  Aturan persetujuan sama dengan merge lewat MR (mis. branch integrasi sprint ke `branch.basis` hanya
  atas persetujuan PO; branch integrasi disimpan sampai merge itu, lalu dihapus).
- **Catatan merge** (pengganti deskripsi MR, untuk merge `/scrum-kit:sprint` dan `/scrum-kit:hotfix`):
  satu berkas per merge di folder laporan sprint, `<dokumen.laporan>/merge-<branch sumber>.md` (`/`
  di nama branch diganti `-`), berisi branch sumber dan tujuan, SHA HEAD yang diuji, keluaran asli `gate.ci` pada HEAD
  itu, dan checklist DoD templat MR proyek yang sudah dicentang. Berkas itu ikut di merge commit:
  `git merge --no-ff --no-commit <branch>`, tulis berkasnya, `git add -- <berkas>`, lalu
  `git commit --no-edit` (pesan bawaan `Merge branch '<branch>'` tetap, dibaca `/scrum-kit:rilis`).
- Sesudah merge, hanya bila `git merge-base --is-ancestor <branch> <tujuan>` sukses:
  `git worktree remove <worktree>` dan `git branch -D <branch>`. Tidak ada `git push`, termasuk
  `git push origin --delete`. Selain itu simpan branch dan worktree-nya, lalu laporkan.
- Tag rilis atau hotfix dibuat lokal dan tidak di-push.

## Gerbang kesiapan backlog

Dipakai `/scrum-kit:sprint` langkah 0.3, sebelum dokumen sprint di-commit. Laporan kesiapan
`docs/sprints/backlog-check-<nn>.md` ditulis skill gratis "Backlog Check" dari Lanewright Planning,
bukan oleh scrum-kit. Laporan itu tidak pernah wajib: tanpa laporan, sprint lanjut bila pengguna
memintanya.

Cara membaca laporan (bahasa Inggris atau Indonesia):

- **Baris backlog**: di tabel "Checked files" / "Berkas yang diperiksa", baris yang berkasnya =
  `dokumen.backlog` dengan `{nn}` terisi (abaikan backtick dan `./` di depan; `\` = `/`). Baris
  `.proposed.md` tidak dipakai: persetujuan hanya mencakup berkas resmi.
- **Sidik jari**: SHA-256 isi berkas dengan CRLF dibaca sebagai LF, dihitung
  `scripts/backlog-sidik.py` persis seperti `backlog_check.py` Backlog Check. Tidak ada baris untuk
  backlog itu, selnya "not computed" / "tidak dihitung", atau tidak ada peluncur Python → kesegaran
  laporan tidak bisa dipastikan: perlakukan seperti sidik jari berbeda (usang).
- **Putusan**: baris backlog yang sama di tabel "Verdict" / "Putusan", dibandingkan utuh (`BELUM
  SIAP` memuat kata `SIAP`): `READY` = `SIAP`; `READY WITH WARNINGS` = `SIAP DENGAN PERINGATAN` atau
  `SIAP DENGAN CATATAN`; `NOT READY` = `BELUM SIAP`. Nilai lain diperlakukan seperti `NOT READY`.
- **Persetujuan terisi** hanya bila "Approved by" / "Disetujui oleh", "Role" / "Peran", dan "Date" /
  "Tanggal" berisi nilai (bukan kosong atau `____`) dan baris Status = "approved" / "disetujui".
  Selain itu blok persetujuan dianggap kosong. Isi "Overrides" / "Pengecualian" disebutkan saat
  bertanya ke product owner.
- **Butir DoD tidak berlaku yang disetujui**: kolom `Butir DoD tidak berlaku (disetujui):` /
  `DoD not applicable (approved):` di blok persetujuan, sesudah "Overrides" / "Pengecualian": nama
  butir DoD dipisah titik koma. Cocokkan lebih dulu dengan daftar usulan di laporan itu sendiri: butir
  usulan yang nama lengkapnya muncul di kolom dihitung satu butir walau namanya memuat titik koma;
  hanya sisanya yang dipecah di titik koma. Himpunan yang disetujui = butir yang disebut di sana, hanya bila
  persetujuan terisi (butir di atas) dan sidik jari cocok; selain itu kosong. Kosong juga bila
  isinya `____`, `tidak ada` / `none`, atau kolomnya tidak ada (laporan dengan blok persetujuan versi
  lama). Daftar usulan Sprint Planner di atas blok persetujuan ("butir DoD yang diusulkan tidak
  berlaku") hanya usulan, tidak pernah masuk himpunan.

Aturan:

- Orkestrator tidak pernah mengisi blok persetujuan, mengubah Status, atau menyunting laporan; bila
  backlog harus diperiksa ulang, manusia menjalankan ulang Backlog Check.
- Tiap keadaan ditanyakan sekali, tidak berulang. Laporan usang sekaligus belum disetujui atau
  `NOT READY` → satu pertanyaan untuk keduanya.
- Lanjut tanpa persetujuan hanya atas keputusan eksplisit product owner, dengan alasan.
- Hasil gerbang dicatat satu baris di `dokumen.serah_terima` (bagian "Status saat ini"), diakhiri
  `(sprint <nn>, <tanggal>)`, dan ikut di-commit bersama dokumen sprint (langkah 0.4):
  - lulus: `Gerbang laporan: lulus, putusan <putusan>, disetujui <nama> (<peran>) <tanggal persetujuan>`;
  - tanpa laporan: `Gerbang laporan: tanpa laporan kesiapan, dilanjutkan atas keputusan pengguna`;
  - hanya usang: `Gerbang laporan: laporan usang (sidik jari berbeda), dilanjutkan atas keputusan pengguna`;
  - blok persetujuan kosong (belum disetujui; usang atau tidak): `Gerbang laporan: dilanjutkan tanpa
    persetujuan, alasan <alasan product owner>`, ditambah "laporan usang" bila berlaku;
  - `NOT READY` dengan blok persetujuan terisi: `Gerbang laporan: dilanjutkan walau putusan NOT READY,
    disetujui <nama> (<peran>) <tanggal persetujuan>, butir DoD tidak berlaku yang disetujui:
    <himpunan, atau tidak ada>, alasan <alasan product owner>`, ditambah "laporan usang" bila berlaku.
- Berhenti di gerbang (pengguna tidak melanjutkan) → tidak ada worktree yang dibuat; laporkan apa yang
  perlu dilakukan (membuat laporan, menjalankan ulang Backlog Check, atau persetujuan).

### Butir DoD tidak berlaku selama sprint

Berlaku setiap kali peran atau peninjau menandai sebuah butir Definition of Done "tidak berlaku" untuk
sebuah item. Aturan lama tetap: alasannya tertulis di `dokumen.serah_terima` bagian "Butir DoD tidak
berlaku" dan product owner menyetujuinya; tidak pernah diam-diam. Yang ditambahkan di sini: dari mana
persetujuan itu boleh datang, dan apa yang terjadi selama persetujuan belum ada.

- Butir ada di himpunan yang disetujui (gerbang di atas; dicocokkan dengan nama butir di Definition of
  Done `CLAUDE.md`, ragu → anggap tidak ada) → terima, dan isi kolom persetujuan di serah terima dengan
  `disetujui di laporan kesiapan <nama berkas laporan> (<tanggal persetujuan>)`.
- Butir tidak ada di himpunan → tanya product owner sekali, di chat. Disetujui → `disetujui PO di chat
  (<tanggal>)`. Ditolak → butir itu tetap wajib; kembalikan item ke agen pemiliknya.
- Tidak ada yang bisa menjawab (sesi non-interaktif) → tandai baris DoD itu `menunggu persetujuan
  product owner`, di checklist DoD item dan di kolom persetujuan serah terima. Butir itu tidak
  dihitung terpenuhi. Branch item tetap di-merge ke branch integrasi hanya bila semua butir DoD
  lainnya terpenuhi, tetapi branch integrasi **tidak** di-merge ke `branch.basis`: berhenti sesudah
  ringkasan sprint, cantumkan setiap persetujuan yang tertunda, dan laporkan bahwa merge akhir
  menunggu product owner.

Tidak pernah merge ke `branch.basis` selama ada persetujuan yang tertunda.

## Batas pemakaian

Berlaku untuk `/scrum-kit:sprint`, `/scrum-kit:hotfix`, dan `/scrum-kit:rilis`. Plugin ini tidak
membaca angka kuota dan tidak memasang ambang: bertindaklah atas yang ditampilkan Claude Code.
Tandanya: peringatan bahwa batas pemakaian, sesi, laju, atau kredit sudah dekat, galat bahwa batas
tercapai, atau proses agen yang berakhir dengan galat semacam itu.

**Batas sudah dekat (masih bisa bekerja):**

1. Jangan memulai agen atau item baru. Agen yang sedang berjalan menyelesaikan langkahnya.
2. Agen yang punya pekerjaan belum di-commit meng-commit-nya di branch-nya sendiri dengan pesan
   `wip: <id-item>, berhenti karena batas pemakaian`. Commit itu tidak mengklaim gate apa pun.
3. Perbarui `dokumen.serah_terima` (baris "Sedang berjalan"): untuk tiap item terbuka, agen, branch,
   worktree, SHA commit terakhir, yang sudah selesai, yang tersisa, gate yang sudah dijalankan, dan
   jam batas pulih bila ditampilkan. Commit dan push seperti biasa.
4. Berhenti dan laporkan: yang sudah merge, yang masih terbuka, dan kapan bisa dilanjutkan.

Tidak ada gate, review, atau persetujuan yang dilewati demi selesai sebelum batas. Item yang belum
merge tetap belum merge.

**Batas tercapai (proses agen berakhir, atau panggilanmu sendiri ditolak):** laporkan galatnya
sekali dan jangan mengulang dalam loop. Pindah jalur hanya menurut urutan di "Mendispatch agen"
(CLI → Anthropic API → tool Agent), dan catat perpindahan itu di serah terima dan ringkasan. Semua
jalur habis → berhenti. Berkas agen yang belum di-commit dibiarkan di worktree-nya: orkestrator
tidak meng-commit, mengembalikan, atau menghapusnya. Bila kamu masih bisa menulis, kerjakan butir 3
dan 4 dan tambahkan `git status --short` tiap worktree itu ke serah terima. Bila sesimu sendiri
terputus, tidak ada lagi yang tertulis; karena itu serah terima diperbarui setiap pekerjaan dimulai
dan selesai.

**Agen** (aturan ini ikut di prompt agen): bila Claude Code memperingatkan batas pemakaian sudah
dekat, berhenti di titik berkas-berkasnya konsisten, commit sebagai
`wip: <id-item>, berhenti karena batas pemakaian`, dan tulis di laporan yang sudah selesai, yang
tersisa, dan gate yang belum dijalankan. Jangan mengklaim gate untuk commit itu.

**Melanjutkan.** Bila manusia meminta sprint, hotfix, atau rilis dilanjutkan, kerjakan ini sebelum
langkah lain:

1. Baca `dokumen.serah_terima`. Jalankan `git worktree list`; untuk tiap branch item jalankan
   `git status --short` di worktree-nya dan `git log --oneline <tujuan MR>..<branch>`.
2. Pilah tiap item yang belum selesai:
   - branch-nya sudah merge (`git merge-base --is-ancestor <branch> origin/<tujuan MR>` sukses
     sesudah `git fetch origin`; mode lokal: `<tujuan MR>`) → selesai; bersihkan seperti "Cara
     merge";
   - MR-nya terbuka → periksa buktinya (SHA HEAD, run CI, vonis review) dan lanjut dari situ;
   - worktree punya commit atau berkas belum di-commit → agen yang sama melanjutkan di worktree dan
     branch itu. Jangan membuatnya lagi (`worktree-new.sh` menolak path atau branch yang sudah ada)
     dan jangan membuang pekerjaannya. Beri tahu agen apa yang ada di sana; sesudah commit `wip:`
     semua gate dijalankan ulang;
   - belum ada worktree dan branch → mulai item seperti biasa.
3. Bila git atau forge berbeda dengan serah terima, git dan forge yang benar: betulkan serah terima.
4. Lanjutkan perintah dari langkah pertama yang belum selesai, dan tulis di ringkasan (hotfix atau
   rilis: di laporan) bahwa pekerjaan terhenti karena batas pemakaian dan kapan.
