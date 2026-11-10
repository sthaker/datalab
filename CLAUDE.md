# Data Lab: start here

Entry point for any agent or person picking this project up with no prior context. Read this file, then the docs listed in the map for the job at hand.

## What this is

A single-file web app (`index.html`, vanilla JS, no build step) that gives two kids short, self-paced data lessons with a check at the end of each one. It is the delivery vehicle for a home data-science curriculum that runs on top of school.

- Track `k7`: a 7th grader. Sessions `s01`–`s12`. Mostly CODAP on a computer; `s01` (a reaction-time experiment) works on any device.
- Track `k4`: a 4th grader. Sessions `m01`–`m12`. Paper and real objects first; the screen is a short check at the end. Each session is also a printable mission card (Parent view → Print).
- The parents set up, spot-check for about 10 minutes a week, and sign off projects.

## Current state (10 November 2026)

- A four-week trial is written: two units of six sessions per track, a gate after each unit. Unit 1C is outlined for each track. Everything later is a plan.
- No child has completed the trial; the content is unpiloted and the trial is the pilot. The first measure of success is whether the kids come back (decision rule in `docs/PURPOSE.md`).
- Live at <https://sthaker.github.io/datalab/>. Progress syncs to a private GitHub repo. A hosted copy inside Claude adds a hints-only coach and grading of written answers.
- Added 10 November: "Grown-ups: try the lessons" (run any session or gate, nothing saved) and stop / keep going / start over for a session in progress (remembered on the device only).

## Rules that are not negotiable

1. **Privacy.** This repo and the page are public. No names of the kids, parents, pets, school, teachers or city, and no other identifying detail, in `index.html`, tests, docs, commit messages or screenshots. Names are typed in Parent view and live only with the progress. Say "the 7th grader (track k7)", "the 4th grader (track k4)", "the parents", "their school". Before every commit run a case-insensitive grep for the family's names and places over the working tree, and run `tests/test_gh.py` with `DATALAB_FORBID` set to the same pattern. The pattern is not in this repo: ask the owner for it, or have the owner run both. An unset `DATALAB_FORBID` means the check did NOT run; the test prints a SKIP line. Commands in `docs/OPERATIONS.md`, "Privacy operations". The GitHub account name in the URL is the one accepted exception.
2. **No "null" on screen.** `Node.append(null)` prints the word "null". Build all DOM through `el()`, which drops `null` and `false`. Tests fail on stray `null`, `undefined`, `NaN` or `[object` text.
3. **Phone first.** Every screen must work at 390 px wide with a thumb: no sideways scroll, tap targets 44 px, inputs at 16 px or more, figures laid out at 340 px (`FW()`).
4. **Test before ship.** All scripts in `docs/TESTING.md` clean. A new unit also needs a second reviewer and a phone audit.
5. **Both copies stay identical.** The GitHub Pages file and the Claude artifact are the same bytes. Never edit one alone.
6. **Stored ids are permanent.** Session ids, item ids and gate ids key the kids' saved progress. Never rename or reuse one that has shipped.
7. **Every check item stands alone.** It reappears in warm-ups and gates without its session.

## Map of the docs

| File | Read it when you need |
|---|---|
| `docs/PURPOSE.md` | Why this exists, what success means, who the users are, the constraints |
| `docs/PEDAGOGY.md` | The design principles and where the code enforces them, the weekly system, how progress is counted, failure modes, the outside review |
| `docs/CURRICULUM.md` | Both tracks by phase, every written session in tables, the outlines for unit 1C, gates and outside checks |
| `docs/AUTHORING.md` | To write a session or unit: the full data schema, every item and figure type, content rules, checklist, a worked example |
| `docs/ARCHITECTURE.md` | To change code: code map, state shape, merge rules, sync backends, WIP, views, AI pieces, CSS conventions |
| `docs/OPERATIONS.md` | Deploy, the progress repo, connecting devices, sync warnings, erase and reset, debugging sync, what to hand the owner when blocked |
| `docs/TESTING.md` | Each test script, what it cannot catch, the manual checks, the rule for new units |
| `docs/DECISIONS.md` | Why things are the way they are, dated |

Three common jobs: add a session → `CURRICULUM.md`, then `AUTHORING.md`, then `TESTING.md`. Fix a sync bug → `ARCHITECTURE.md` (merge and backends), `OPERATIONS.md` (debugging sync), `tests/test_gh.py`. Ship → "Deploy the page" in `OPERATIONS.md`.

## Where things live

| Thing | Where |
|---|---|
| The page | this repo, `main`, served by GitHub Pages at `https://sthaker.github.io/datalab/` |
| Progress and names | private repo `sthaker/datalab-progress`: `state/k7.json`, `state/k4.json`, `state/parent.json`, `state/device-check.json`, written by the page through the GitHub contents API |
| Hosted copy with coach and written-answer grading | a private Claude artifact titled "Data Lab Mission Control" in the owner's account (same `index.html`; uses the artifact `db`, `sample`, `tts` capabilities) |
| Parent guide (rationale, private details) | a private Claude doc in the owner's account. The docs here carry everything from it that is safe to publish. Where the two disagree, this repo wins. |

## Ship procedure

The full procedure, the only copy, is "Deploy the page" in `docs/OPERATIONS.md`. In short:

1. Edit, update the docs in the same commit, run all tests and the privacy check.
2. Push to `main` only when the owner has asked, then confirm the live page's SHA-256 equals the committed file's.
3. Republish the Claude artifact from the same file, verify it, and update "Verified / not verified" below.

## Verified / not verified

- Verified: all test scripts (Chromium, WebKit iPad and iPhone emulation); the page in Apple's iPad simulator with scripted clicks; the live page's bytes after the 9 November push; real GitHub sync from a real phone (connect, parent code and names written); every numeric answer key in the 9 November draft, checked by hand by a second reviewer (keys added or changed since are covered only by the walkthroughs).
- Verified 10 November, after the outside review of `c23ac9a`: `tests/test_review_fixes.py` (42 checks) passes on the fixed page and fails 28 of its checks on `c23ac9a`; all other scripts clean.
- Shipped 10 November (merge `8d325ec`, PR #1): the live page's SHA-256 equals the committed `index.html` (`e709814d…`), and the Claude artifact was republished from the same file and lists the same SHA-256, with its `db`, `sample`, `tts` and `user` capabilities kept.
- Second-reviewer read (Codex, cold, `PEDAGOGY.md` and `AUTHORING.md` only) of the `s11`/`s12` rewrite on 10 November: "ship with listed edits"; the edits were applied (table layout per route, median defined, units in the question, the saved prediction shown, `s11.b` made route-neutral, range defined in `s12`).
- Not verified: the hosted grader against both `s11` routes; a computer walkthrough of `s11` from an empty profile after a Unit 1A test-out; finger taps on a real iPad; a full session by a child; read-aloud audio; CODAP save and reopen (needed between `s11` and `s12`); dragging in CODAP; CODAP menu names against the live tool; the AI grader after its prompt was tightened; the hosted copy's database sync; mission cards on a real printer; tryout and stop/resume on a real device.

## Lessons from the first day (keep doing these)

- The first real user found two bugs in minutes that 24-session walkthroughs missed: `Node.append(null)` renders the word "null", and a step told the kid to "go to the exit check" to start an experiment. Tests now check visible text; copy still needs a human-eyes pass at phone size.
- Test on the device class the kids use. Desktop passes said nothing about a 390 px screen.
- Any check item can reappear in a warm-up or gate without its session. Every item must make sense alone and carry its own `fig`.
- An outside reviewer (Codex) and a phone audit each found real defects the other missed. Use both before shipping a new unit.
- A passing walkthrough proves the flow, not the content. The solver reads the answer key; it never reads the steps.
- Adults need a way to look without leaving marks. The first advice was to do real sessions and then Erase; tryout mode replaced it.
- The docs were tested by a new developer with no context writing two sessions from them; 17 gaps were found and fixed. Repeat that test after any large change to the docs.

## Backlog, in priority order

1. Run the manual checks in `docs/TESTING.md` on real devices (phone, iPad, CODAP on a computer, one printed card set).
2. Write Unit 1C for each track when a kid is within three sessions of the end (outlines in `TRACKS` and `docs/CURRICULUM.md`). `k7` 1C needs a scatter-plot figure kind.
3. Skipped sessions (passed by test-out) cannot be opened from My path. `s11` now collects the reaction times it needs in place (`collect`), so this is no longer blocking.
4. Review stats (`stats.*`) merge with `Math.max`, so two devices can undercount attempts.
5. On a phone, sessions that need CODAP only warn; they do not block.
6. `walk_webkit.py` lacks the stray-text assertions that `walk.py` has; `SOLVE` is duplicated in four files.
7. Unused code: the `pick` item type, `interests`, `gates[*].ext`, the `NYT_GRAPH` constant. Use or remove.
8. Phase gates (Khan Academy unit tests) are planned and not represented in the page.
