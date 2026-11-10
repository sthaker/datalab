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

1. **Privacy.** This repo and the page are public. No names of the kids, parents, pets, school, teachers or city, and no other identifying detail, in `index.html`, tests, docs, commit messages or screenshots. Names are typed in Parent view and live only with the progress. Say "the 7th grader (track k7)", "the 4th grader (track k4)", "the parents", "their school". Before every commit run a case-insensitive grep for the family's names and places over the working tree (the owner has the pattern; `DATALAB_FORBID` feeds it to `tests/test_gh.py`). The GitHub account name in the URL is the one accepted exception.
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

Three common jobs: add a session → `CURRICULUM.md`, then `AUTHORING.md`, then `TESTING.md`. Fix a sync bug → `ARCHITECTURE.md` (merge and backends), `OPERATIONS.md` (debugging sync), `tests/test_gh.py`. Ship → the procedure below.

## Where things live

| Thing | Where |
|---|---|
| The page | this repo, `main`, served by GitHub Pages at `https://sthaker.github.io/datalab/` |
| Progress and names | private repo `sthaker/datalab-progress`: `state/k7.json`, `state/k4.json`, `state/parent.json`, `state/device-check.json`, written by the page through the GitHub contents API |
| Hosted copy with coach and written-answer grading | a private Claude artifact titled "Data Lab Mission Control" in the owner's account (same `index.html`; uses the artifact `db`, `sample`, `tts` capabilities) |
| Parent guide (rationale, private details) | a private Claude doc in the owner's account. The docs here carry everything from it that is safe to publish. Where the two disagree, this repo wins. |

## Ship procedure

1. Edit `index.html`. Update the docs the change touches in the same commit.
2. From `tests/`: `python3 walk.py && python3 walk_webkit.py && python3 test_gh.py && python3 test_modes.py && python3 phone_audit.py`. Read the output against "Clean means" in `docs/TESTING.md`; exit codes alone are not enough. Read the screenshots.
3. Run the privacy grep.
4. Commit and push to `main` only when the owner has asked for that. Pages rebuilds in about a minute.
5. Confirm the live bytes: `sha256sum index.html` must equal `curl -s "https://sthaker.github.io/datalab/index.html?v=$(date +%s)" | sha256sum`.
6. Republish the Claude artifact from the same file.
7. Update "Verified / not verified" below.

If you cannot push, cannot reach the artifact, or cannot run a browser, do not work around it. `docs/OPERATIONS.md` lists what to hand the owner.

## Verified / not verified

- Verified: all test scripts (Chromium, WebKit iPad and iPhone emulation); the page in Apple's iPad simulator with scripted clicks; the live page's bytes after the 9 November push; real GitHub sync from a real phone (connect, parent code and names written); every numeric answer key in the 9 November draft, checked by hand by a second reviewer (keys added or changed since are covered only by the walkthroughs).
- Not verified: finger taps on a real iPad; a full session by a child; read-aloud audio; CODAP save and reopen (needed between `s11` and `s12`); dragging in CODAP; CODAP menu names against the live tool; the AI grader after its prompt was tightened; the hosted copy's database sync; mission cards on a real printer; tryout and stop/resume on a real device.

## Lessons from the first day (keep doing these)

- The first real user found two bugs in minutes that 24-session walkthroughs missed: `Node.append(null)` renders the word "null", and a step told the kid to "go to the exit check" to start an experiment. Tests now check visible text; copy still needs a human-eyes pass at phone size.
- Test on the device class the kids use. Desktop passes said nothing about a 390 px screen.
- Any check item can reappear in a warm-up or gate without its session. Every item must make sense alone and carry its own `fig`.
- An outside reviewer (Codex) and a phone audit each found real defects the other missed. Use both before shipping a new unit.
- A passing walkthrough proves the flow, not the content. The solver reads the answer key; it never reads the steps.
- Adults need a way to look without leaving marks. The first advice was to do real sessions and then Erase; tryout mode replaced it.

## Backlog, in priority order

1. Run the manual checks in `docs/TESTING.md` on real devices (phone, iPad, CODAP on a computer, one printed card set).
3. Write Unit 1C for each track when a kid is within three sessions of the end (outlines in `TRACKS` and `docs/CURRICULUM.md`). `k7` 1C needs a scatter-plot figure kind.
4. Test-out skips the data-collection sessions that `s11` depends on; let skipped sessions be opened from My path.
5. Review stats (`stats.*`) merge with `Math.max`, so two devices can undercount attempts.
6. On a phone, sessions that need CODAP only warn; they do not block.
7. `walk_webkit.py` lacks the stray-text assertions that `walk.py` has; `SOLVE` is duplicated in four files.
8. Unused code: the `pick` item type, `interests`, `gates[*].ext`, the `NYT_GRAPH` constant. Use or remove.
9. Phase gates (Khan Academy unit tests) are planned and not represented in the page.
