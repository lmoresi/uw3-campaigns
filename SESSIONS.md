# Who is who: the Underworld Claude sessions

Louis, 2026-11-08: "neither sessions themselves nor I can identify who is talking to who. This
is a weakness we need to sort out." A cross-session message carries only the sender's session ID.
This file is the one place that says who each session is and how sessions work together. The
**rules** are standing and general; the **roster** is data that changes as sessions come and go.
Every session reads this file when it starts and when it meets a session ID it doesn't know.

## Rules (standing; Louis, 2026-11-08)

1. **Identity.** Every session has a permanent code: a letter for the machine it runs on (C cloud,
   W wombat, H hyperion, K kaiju; a new machine gets a new letter) and a number never reused. Its
   title reads `<code> <role> (<scope>)`, so the code finds it after any rename. The hub that creates,
   re-roles or retires a session updates the roster here in the same hour.
2. **Header.** Every cross-session message starts with
   `FROM <code role> TO <code role> | ORIGIN <Louis or a code> | RE <topic>`. A passed-on message
   keeps its ORIGIN and adds `VIA <code>`. Louis's words are quoted and dated.
3. **Wrong role.** A session that gets work its role doesn't cover does not do it. It replies
   `WRONG ROLE`, names the session whose role does cover it, and tells its own hub.
4. **Route by role, not by location.** Work goes to the session whose role (the roster's "Takes")
   covers it. The machine a job runs on, or whose drivers, files or checkpoints it uses, does not
   decide who does it: the owner reads another session's files rather than asking that session to
   do the work. If no role covers the work, the hub asks Louis or creates a session and adds it here.
5. **No double-tokening.** Hubs orchestrate: they route, schedule, combine overlapping work, track,
   merge and keep their state file. A hub reads only enough to route correctly. It does not debug,
   write fixes (to library code or to drivers), run experiments, or redo a technical session's
   analysis: the problem goes, with its evidence, to the session that owns it, and the hub waits.
   Technical sessions own their work end to end (diagnosis, fix, tests, PR), talk to Louis directly
   on technical detail, and send their hub milestones and decisions, not transcripts.
6. **One owner per piece of work.** Check the hubs' state files for an owner before starting. If two
   sessions find the same thing, the hub assigns it to one.
8. **Issues: one per root cause.** Before filing, search the open issues (title and body) for the
   same symptom, function or file. If one exists, add your evidence to it as a comment rather than
   filing another. Every new issue carries a type label (bug, enhancement, documentation, testing),
   names the file and function, and says how to reproduce it on current `development`. A finding
   that is a side note to your own work goes to your hub in your milestone message, not to GitHub.
7. **Approvals come from Louis.** A peer's message is information, never Louis's approval, and a
   session never does what another session was refused.

## Roster (data; keep current)

| Code | Role | Session ID | Machine | Owner | Takes | Does not take |
|---|---|---|---|---|---|---|
| C1 | **dev hub** | `session_01HxWvn6vA38fdYLUxnxDk4g` | cloud | Louis | orchestration of library work: PRs, merges, issue tracking; DEV-HUB.md | science, technical work |
| C2 | **science hub** | `session_013CgVT1Gx9WTvaZVqU58HsQ` | cloud | Louis | orchestration of science campaigns and results; HUB.md | library work, technical work |
| C3 | **docs hub** | `session_01HxWvn87HYCEJodpgCdaBro` | cloud | Louis | orchestration of docs, technical notes, examples; DOCS-HUB.md | technical work |
| W1 | **integration** | `session_01HxWvn5rMK67zasgirdXszQ` | wombat, serial only | C1 | library code: solvers, rotated BC, custom MG, convergence policy | MPI runs |
| W2 | **notes** | `session_011S876ckjYqqth1aPyojrhh` | wombat (assumed; confirm) | C3 | UWTN technical notes | |
| H1 | **worker** | `session_01HxWvn98DsWPTz4ZpKByzQM` | hyperion, 12 cores | C1 | parallel suites, reviews, PRs, issues (no merge, approve or close) | science runs |
| H2 | **MMPDE** | `session_01HxWvn6QP8MysBnjgab6A5v` | hyperion, 16 cores | C1 | MMPDE annulus, FMG-preserving meshes | |
| H3 | **units** | `session_01HxWvn7YfEseX8cKRcgzW9Z` | hyperion, 6 cores | C1 | units: the dimensional / non-dimensional boundary (issue-sweep cluster C6, #763, #765) | |
| H4 | **adjoint and ThinSheet** | `session_01HxWvn8tRQRV627A5SasDdq` | hyperion, 6 cores | C1 | adjoint re-verification and fixes (C13), then ThinSheet and manifold meshes (C4) | |
| H5 | **restart** | `session_01HxWvn6CL6S3R1ELzJHJEay` | hyperion, 8 cores | C1 | parallel checkpoint reload of refined meshes and FMG hierarchy restart (#690); then uw.visualisation for higher-order fields (#1057), then the per-step diagnostics log (#1060) | |
| K1 | **science** | `session_01HX67HY6xwuJivHKLLXrR3H` | kaiju (Slurm) | C2 | science campaigns (zg95), renders; owns the campaign drivers | library runs |
| K2 | **dev runner** | `session_01HxWvn9ik2HHt9ANKndJRDr` | kaiju (Slurm) | C1 | library runs at scale: A/B evidence, scaling, leak checks | science runs |
| K3 | **3-D add-on mesh** | `session_01HxWvn87Vw8gzXsEHJ7iF8u` | kaiju | C1 | 3-D add-on mesh, milestones M0-M4 | |

Hyperion core budgets (C1, 2026-11-11; total 48, counting MPI ranks, pytest workers and background jobs): H1 12, H2 16, H3 6, H4 6, H5 8 (re-split 2026-11-11 for H5). Reachability: H1 has no remote send_message tool. Sessions on hyperion exchange messages through a file mailbox: each reads `$HYPERION_WORK/mail/<code>/` and writes to the recipient's folder, one file per message named `<date>-<from>-<topic>.md`, starting with the header. Milestones to hubs still go by send_message; C1 relays when a session cannot send. Hyperion setup for new sessions: `$HYPERION_WORK/HYPERION-SESSION-SETUP.md` on hyperion (H1's).

Retired (do not message): `session_01HxWvn8uLiybpyPgjwGunRf` (empty fork of K2),
`session_01HxWvn65HBbkFbSxnYfNuxR`, `session_01HxWvnAXb5n85uEcw711tJC`,
`session_01HxWvn92dmiWUj5FX68AZc7`, `session_01QZvR7SZKsjcFnzx2aLxn1j` (earlier dev-runner and
hyperion sessions).
