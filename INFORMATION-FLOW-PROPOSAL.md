# How information should flow across Underworld: a proposal

**Status**: proposal from the docs hub, 2026-10-27. Nothing below is adopted until the
team rules on it; the decisions it needs are listed at the end.

## The problem, as observed

Seven channels carry Underworld's knowledge today: `docs/` in underworld3, docstrings,
planning files (first `underworld.md`, then Project 10, now `HUB.md` and `DOCS-HUB.md`),
the technical notes, the wiki, issues and pull requests. Each was added for a reason and
each still does something. What is missing is any rule for how a piece of knowledge moves
between them, so the same finding is copied by hand from a transcript to a hub log to a
wiki page to a design doc to a subsystem page to a note, with no pointer back, and
"where is the current truth about X" has no single answer.

Evidence from one day's reading:

- `docs/` holds four genres that are not documentation of the code at a version:
  review records (`docs/reviews/`, 788 KB, duplicating what is posted on the PRs),
  planning snapshots (`docs/planning/`, `docs/plans/`, `docs/developer/planning/`),
  AI session notes (`docs/developer/ai-notes/`), and 58 design documents of which 7 say
  nothing about whether they shipped. 137 of 270 pages are reachable from no toctree.
- Two changelogs: root `CHANGES.md` (stopped in May, referenced by nothing) and
  `docs/developer/CHANGELOG.md` (the one the release process names, no October entries).
- The wiki says a page "graduates to `docs/` when it stops moving". No page has, in
  three weeks of heavy use, because nothing checks. Pages are rewritten in place, so the
  record of what was tried on 18 October is gone once the page says what we think on
  27 October. They are neither permanent nor ephemeral, as Louis put it.
- Project 10 was meant as the agents' shared surface and has not been used; `HUB.md`
  has been updated several times a day. The agents chose files because files are what
  they can write: from a cloud session the board (GraphQL) and the wiki (not an
  attachable repository) are both read-only.
- The notes repository has the strongest machinery of all (validation, house-style
  check, preview, deposit, DOI tests) and the clearest definition of what it publishes.
  It is the one channel that gels, and it is the one with a stated lifecycle.

The diagnosis: the channels are defined by their *container* (a wiki, a docs tree, a
board) rather than by the *state* of the knowledge they hold, and no step moves
knowledge from one state to the next.

## The principle

Knowledge about Underworld passes through four states, and the work that produces it
is a fifth thing:

| State | Example | Lifetime | Who writes it, from where |
|---|---|---|---|
| **Now** | which machine runs what, who holds the pen on a note, what waits for team input | hours to days | agents, from anywhere |
| **Learning** | "warm start after a rebuild wastes 20 Picard iterations because the switch is relative to the solve's own residual"; what did not work and why | weeks to months, then permanent as a record | agents and people, from anywhere |
| **Reference** | how `add_rotated_freeslip_bc` works at v3.2 | until the code changes; versioned with it | people and agents, through PRs |
| **Record** | a technical note with a DOI; a paper | permanent, citable | people, with agents' help |
| **Work** | a bug, a branch, a review | until merged or closed | everyone |

Each state gets exactly one home. A home must be writable by whoever produces that kind
of knowledge, from wherever they produce it, which for the first two states means an
ordinary git repository and nothing else. Knowledge moves forward by a defined step
that leaves a pointer behind, so the back-trail from a reference page to the finding
that justified it is never lost.

## The five homes

| State | Home | What stays there | What moves out, and when |
|---|---|---|---|
| Now | `HUB.md`, `DOCS-HUB.md` (hub files) | state tables, the waiting-for-team-input list, a log no older than two weeks | a log entry that records something learned becomes a journal entry the day it is written; older log lines are deleted, not archived |
| Learning | **the journal** (new; see below) | dated, immutable entries; topic pages that index them and state the current conclusion | a topic whose conclusion has not changed for a quarter, and that the code relies on, becomes a reference page by PR; a cluster of entries becomes a technical note via `WRITING-PLAN.md` |
| Reference | `underworld3/docs/` and docstrings | how the code works at a version, one governing page per topic, the authority map as router; capability guides as the bridge from the object to its page | nothing moves out; superseded pages are deleted in the PR that supersedes them |
| Record | technical notes, papers | what the world may cite | nothing; a correction is a new version of the same deposit |
| Work | issues and PRs | the work and its review | a review finding we decide not to fix becomes an issue; a finding worth keeping becomes a journal entry linked from the PR |

Seven channels become five, each with one job, one writer set, and one direction of
flow.

## The journal

This is the only new piece, and it replaces the wiki, the board, Discussions as a
record, and the dated genres now sheltering in `docs/`.

**Shape.** A git repository (`underworldcode/journal`, or whatever name the team prefers)
built with MyST into a site in the same theme as underworldcode.org, linked from its
header:

```
entries/2026-10-24-warm-start-switch-relative-residual.md
entries/2026-10-26-rebuild-spacing-rungs-8-vs-4.md
topics/fault-multigrid.md
topics/solvers-and-multigrid.md
digests/2026-W44.md
```

**An entry** is written once and never edited (a correction is a new entry that links
the old one). Front matter: date, author (a person, or a session id and the machine it
ran on), kind (`finding`, `dead-end`, `measurement`, `decision`, `digest`), topics, and
links: the PR or branch and commit, the run directory, the transcript, the figure
script. Body: what was tried, what happened, what we now think, in that order. A dead
end is a first-class kind, with the same weight as a finding, because it is the thing a
polished document deletes and a transcript buries. This is what the wiki's History lines
and "What did not work" sections were reaching for; the difference is that an entry is
permanent and a wiki paragraph is not.

**A topic page** has two parts: a short, hand-written "current understanding" (this is
the part a wiki page is today, and it is still rewritten in place) and a generated list
of every entry tagged with the topic, newest first. The script that generates the list
is the whole machinery: no database, no custom tooling beyond the one index script and
the MyST build the notes site already runs.

**The digest** is one entry a week, written by the docs hub from the week's entries,
merged PRs and hub-file changes: what was learned, what shipped, what is stuck. This is
the page a collaborator reads to see what others are doing. It is also the page that
makes the hub files unnecessary reading for a human.

**Why not the wiki.** A wiki is not a repository a cloud session can attach, so half the
sessions that learn things cannot write it; it has no build step, so nothing can check
front matter, links or math; and rewriting in place is the wrong default for a record.
The nineteen existing pages migrate as topic pages, with their History lines turned into
dated entries. The wiki keeps a Home page pointing at the journal.

**Why not inside `underworld3/docs/`.** `docs/` is versioned with the code and goes
through code review. Dated findings are not versioned with anything; keeping them there
is exactly what produced `reviews/`, `planning/` and `ai-notes/`.

**Why not the notes repository.** It is the obvious host: same theme, same checks, and
it already has a `development-note` type. But every type it has is `archival: true` or
a front-page post, its CI builds a PDF per article and runs the DOI tests, and its
standing rests on nothing being there that is not finished. A hundred raw entries a
quarter would slow its build and blur the line it draws well. A separate repository with
the same theme and a cross-link costs one more repo and keeps the series clean. If the
team would rather have one site, the alternative is a `journal-entry` type with
`archival: false`, its own stream, and a banner that says "working note, not reviewed",
and the build excluded from the PDF and DOI steps.

## What retires or shrinks

- **Wiki**: frozen with a pointer after migration.
- **Project 10**: retired, or left as a view fed automatically from labelled issues
  (built-in workflow, no code) for anyone who likes a board. Agents never touch it.
- **Discussions**: not used as a record; a decision is a journal entry of kind
  `decision`, and the argument happens where it happens.
- **`docs/reviews/`**: stops growing. Review findings are posted on the PR, which is
  where they are read; a finding worth keeping is a journal entry. The existing archive
  stays, excluded from the toctree, or moves to the journal as dated entries.
- **`docs/planning/`, `docs/plans/`, `docs/developer/planning/`,
  `docs/developer/ai-notes/`**: moved to a `docs/archive/` excluded from the build, or
  to journal entries dated when they were written. Nothing is deleted.
- **`docs/developer/design/`**: every document gets a status line. Shipped designs fold
  into the subsystem page they describe and the design doc is deleted in that PR;
  proposals and parked ideas move to the journal as `decision` or `dead-end` entries.
  Fifty-eight documents become perhaps fifteen.
- **`CHANGES.md`**: retired with a pointer to `docs/developer/CHANGELOG.md`, which is
  regenerated from `git log --first-parent` at each release as the release process
  already asks.
- **`~/.claude/plans/`**: a session's scratch, never a record. A plan worth keeping is a
  journal entry.

## The flow rules

These are the glue that was missing. They go into `CLAUDE.md` (two paragraphs), the
hub files, and the notes `CONTRIBUTING.md`.

1. **A session that learned something ends by writing an entry.** Not a hub log line,
   not a wiki edit. The hub log says what changed hands; the entry says what was found.
2. **An entry links its evidence**: the commit, the run, the transcript, the figure
   script. An entry with no link is an opinion and says so.
3. **A topic page's "current understanding" is rewritten only with a new entry
   underneath it** saying why.
4. **Graduation is checked, not hoped for.** The docs hub reviews topic pages monthly:
   a conclusion unchanged for a quarter that the code relies on goes to `docs/` by PR,
   with the topic page left pointing at the reference page. A cluster of entries that
   explains one idea is proposed as a note in `WRITING-PLAN.md`.
5. **One router.** `docs/developer/index.md` carries the authority map for reference;
   the journal's topic index carries the map for learning; `CLAUDE.md` points at both.
   Any document that claims authority over a topic and is not in a map is wrong, and the
   map wins.
6. **No pull documents.** Anything that rots when nobody regenerates it (the docstring
   queue, the changelog, the feature manifest, the toctree) is regenerated in CI or at
   release, or deleted. The toctree check becomes a build error with an explicit exclude
   list.
7. **PRs carry their own review.** The adversarial review is posted on the PR and
   nowhere else, with one journal entry only for a finding that outlives the PR.

## Migration

**Phase 0, the team decides** (the list at the end).

**Phase 1, the journal exists (docs hub, one week).** Create the repository, the entry
template, the index script, the MyST build and deploy. Migrate the nineteen wiki pages:
each becomes a topic page, each History line becomes an entry dated as it was. Freeze
the wiki. Write the first digest. Put the two-paragraph rule into `CLAUDE.md` and
`CONTRIBUTING.md` by PR.

**Phase 2, `docs/` is only reference (docs hub, two to three weeks of small PRs).**
Status lines on the 58 design docs and the fold-or-move decision for each; the archive
move; one changelog; the toctree check in CI; the authority map extended to every
subsystem page. Each PR is small and reviewable on its own.

**Phase 3, the habit (ongoing).** The weekly digest; the monthly graduation review;
the quarterly changelog and docstring sweep tied to the release. The docs hub owns all
three and reports in `DOCS-HUB.md`.

Nothing in the plan requires a new tool beyond one index script, and nothing requires
anyone to change where they do their work: machines still push to underworld3,
notes are still written on branches, reviews still happen on PRs. What changes is that
a session ends by writing one dated page, and that one page is where the next person
looks.

## Risks, and what I am not sure of

- **Public rough notes.** Entries written by agents at the end of a session will be
  uneven. The wiki is public today and that has been acceptable; the banner and the
  `kind` field make the standing of an entry unmistakable. If that is still
  uncomfortable, the journal can be a private repository for the team with the digest
  alone published to the notes site.
- **A sixth repository.** The plan retires more than it adds, but a reader counting
  repositories will see one more. The alternative, the journal as a stream on the notes
  site, is above.
- **Who reads the digest.** If nobody does, the journal is a well-kept diary. The test
  is whether Thyagarajulu and Juan read it instead of asking; if after a month they do
  not, the digest should go wherever they do look.
- **Discussions.** I could not check from here whether the Discussions tab is in use; if
  it is, the `decision` entry replaces it as the record and the thread links the entry.

## Decisions needed from the team

1. Journal as its own repository, or as a non-archival stream on the notes site?
2. Public, or private with a published digest?
3. Retire the wiki after migration, or keep it mirrored from the journal for people who
   prefer the wiki UI?
4. Retire Project 10, or keep it as an auto-fed view of issues?
5. `docs/reviews/` and the other dated trees: `docs/archive/` in underworld3 (keeps git
   history, excluded from the build) or journal entries (readable, loses blame)?
6. Go-ahead for Phase 1.
