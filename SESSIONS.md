# Who is who: the Underworld Claude sessions

Louis, 2026-11-08: "neither sessions themselves nor I can identify who is talking to who. This
is a weakness we need to sort out." A cross-session message carries only the sender's session ID.
Look the ID up here. Every hub keeps this table current when it creates, retires or re-roles a
session. Titles in the app are not reliable; this file is.

## Roster

**Codes are permanent** (Louis, 2026-11-08): a letter for the machine the session runs on (C cloud,
W wombat, H hyperion, K kaiju) and a number never reused. Titles read `<code> <role> (<scope>)`, so
a session can be found by its code after a rename. A new session takes the next free number.

| Code | Role | Session ID | Machine | Owner | Takes | Does not take |
|---|---|---|---|---|---|---|
| C1 | **dev hub** | `session_01HxWvn6vA38fdYLUxnxDk4g` | cloud | Louis | PRs, merges, library-fix tracking, routing of dev work; DEV-HUB.md | science runs |
| C2 | **science hub** | `session_013CgVT1Gx9WTvaZVqU58HsQ` | cloud | Louis | campaigns, science results; HUB.md | library debugging |
| C3 | **docs hub** | `session_01HxWvn87HYCEJodpgCdaBro` | cloud | Louis | docs, technical notes, examples; DOCS-HUB.md | |
| W1 | **integration** | `session_01HxWvn5rMK67zasgirdXszQ` | laptop, serial only | dev hub | library code: solvers, rotated BC, custom MG, convergence policy | MPI runs |
| W2 | **notes** | `session_011S876ckjYqqth1aPyojrhh` | wombat (assumed; confirm) | docs hub | UWTN technical notes | |
| H1 | **hyperion worker** | `session_01HxWvn98DsWPTz4ZpKByzQM` | hyperion, up to 48 cores | dev hub | np 2-16 suites, reviews, PRs, issues (no merge, approve or close) | production science |
| H2 | **hyperion MMPDE** | `session_01HxWvn6QP8MysBnjgab6A5v` | hyperion, 24 cores | dev hub | MMPDE annulus, FMG-preserving meshes (#959, #982) | |
| K2 | **kaiju dev runner** | `session_01HxWvn9ik2HHt9ANKndJRDr` | kaiju (Slurm) | dev hub | every library run on kaiju: A/B evidence, scaling, leak checks | production campaigns |
| K1 | **kaiju science** | `session_01HX67HY6xwuJivHKLLXrR3H` | kaiju (Slurm) | science hub | zg95 production campaigns, renders | library debugging (send it to the dev runner) |
| K3 | **kaiju 3-D** | `session_01HxWvn87Vw8gzXsEHJ7iF8u` | kaiju | dev hub | 3-D add-on mesh, milestones M0-M4 | |

Retired (do not message): `session_01HxWvn8uLiybpyPgjwGunRf` (empty fork of the dev runner),
`session_01HxWvn65HBbkFbSxnYfNuxR`, `session_01HxWvnAXb5n85uEcw711tJC`,
`session_01HxWvn92dmiWUj5FX68AZc7`, `session_01QZvR7SZKsjcFnzx2aLxn1j` (earlier dev runner and
hyperion sessions).

## Who does what (Louis, 2026-11-08: no double-tokening)

- **Hubs orchestrate:** route, schedule, combine overlapping work, track, merge, keep the state
  file. A hub reads only enough to route correctly. It does not debug, write fixes to library code or
  drivers, run experiments, or redo a technical session's analysis. A problem goes to the session
  that owns it, with the evidence, and the hub waits for the answer.
- **Technical sessions do the work** and own it end to end: diagnosis, fix, tests, PR. They talk to
  Louis directly on technical detail and send their hub milestones and decisions, not transcripts.
- **One owner per piece of work.** Check the state file for an owner before starting; if two
  sessions find the same thing, the hub assigns it to one.

## Message header (every cross-session message)

First line, before anything else:

```
FROM <code role> TO <code role> | ORIGIN <Louis, or a code> | RE <issue, PR or topic>
```

- **FROM / TO** are codes and roles from the table (e.g. `C1 dev hub`), not titles or IDs.
- **ORIGIN** says who started the request. A relayed message keeps the original ORIGIN and adds
  `VIA <code>`, so the receiver knows it is second-hand.
- **Louis's words** are quoted and dated. A peer's message is never Louis's approval.
- A message for the wrong role is not acted on: the receiver replies `WRONG ROLE`, names the role
  from the table, and tells the sender's hub.

## Routing rules

- Library runs on kaiju (A/B evidence, scaling, leak hunts) go to the **kaiju dev runner**, even when
  they use a science driver or checkpoint. The dev runner reads the science session's files; it does
  not ask the science session to run them.
- A fault in a science driver found during dev work goes to the **science hub**, which routes it to the
  session that owns the driver (K1 for the zg95 drivers). The hub does not write the fix itself.
- Hubs route; technical sessions talk to Louis directly on technical detail.
