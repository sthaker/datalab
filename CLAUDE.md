# Data Lab: working notes for future development

Read this before changing anything. It is the handoff for an ongoing project.

## What this is
A single-file web app (`index.html`, vanilla JS, no build step) that gives two kids short, self-paced data lessons with a check at the end of each one. It is the delivery vehicle for a home data-science curriculum. A four-week trial (12 sessions per kid, two units each) is written; later units are planned only.

- Track `k7`: a 7th grader. Sessions `s01`–`s12`. Mostly CODAP on a computer; `s01` (reaction-time experiment) works on any device.
- Track `k4`: a 4th grader. Sessions `m01`–`m12`. Paper and real objects first; the screen is a short check at the end. Each session is also a printable mission card (Parent view → Print).
- **No names in this repo.** The page is public. Kids' names are typed in Parent view and stored with the progress. Never hardcode a name, school or other identifying detail in `index.html`, tests, commits or docs here.

## Where things live
| Thing | Where |
|---|---|
| The page | this repo, `main`, served by GitHub Pages at `https://sthaker.github.io/datalab/` |
| Progress and names | private repo `sthaker/datalab-progress`, files `state/k7.json`, `state/k4.json`, `state/parent.json`, `state/device-check.json`, written by the page through the GitHub contents API |
| Hosted copy with AI coach and written-answer grading | a private Claude artifact titled "Data Lab Mission Control" in the owner's account (same `index.html`; uses the artifact `db`, `sample`, `tts` capabilities) |
| Parent guide: rationale, decision table, curriculum arc, testing record | a Claude doc titled "Data Science at Home: Curriculum for …" in the owner's account |

## How the app is put together
- `KIDS`, `TRACKS`: all content. Track → phases → units → sessions (`steps`, `check` items) and a unit `gate` (`extra` unseen items, optional `product` rubric).
- Item types: `mc`, `num`, `txt`, `tally` (optional `predict`), `react` (in-page reaction-time experiment). Figures: `bar`, `dot`, `dots2`, `strip2`. `FW()` narrows figures on phones.
- Flow per session: optional warm-up (spaced review, Leitner boxes 1/3/7/14/30 days) → task steps → check → done. The 4th grader can skip the task with "I did it from my card".
- Unit gate: 10 questions, 9 to pass, includes unseen items; second unit adds a parent-signed project. Passing a gate early counts as a test-out, not as sessions.
- `Store`: per-kid state in `localStorage` (`datalab:<key>`), merged with a remote doc. `merge()` is per-field; a higher `epoch` wins whole (that is how Erase works). `push()` reads, merges, then writes; on a sha conflict it retries once. Failed docs are tracked in `Store.fail` and retried on `online`, every 60 s, and when the page returns to the front.
- `GH`: the GitHub backend. Repo and token live only in this device's `localStorage` (`datalab:gh`). First Connect does a real write test.
- Inside Claude (`window.claude` present) the store is the artifact db instead, and `AI` adds a hints-only coach, lenient grading of written answers, and read-aloud.
- Parent view sits behind a code (a speed bump, not security) and relocks when you leave it.

## Changing and shipping
1. Edit `index.html`.
2. Run the tests (below). All must pass.
3. Commit and push to `main`. Pages rebuilds in about a minute. Confirm the live file's hash matches.
4. Republish the Claude artifact from the same file so the two copies stay identical.

## Tests (`tests/`, Python Playwright; Chromium and WebKit)
Set `CHROME` if Chrome is not at `/usr/bin/google-chrome`.
- `walk.py`: both tracks, all 24 sessions, warm-ups, 4 gates, sign-off, reload, test-out, merge and erase logic. Fails on stray `null`/`undefined`/`NaN` text.
- `walk_webkit.py`: the same walk in the Safari engine with iPad emulation.
- `test_gh.py`: GitHub sync against a mock API (bad token, wrong repo, public repo, read-only token, two devices, concurrent write, late-connecting device, erase, offline, revoked token, disconnect), mission cards, card path. Set `DATALAB_FORBID` to a regex of names that must never appear in the page.
- `phone_audit.py`: iPhone 13 profile, real taps, dark and light. Reports stray text, sideways overflow, small tap targets, input zoom risk, figure text size, contrast. Read its screenshots, do not trust the numbers alone.
- `harness.js` + `server.py` + `run.py`: an in-page walkthrough that can run inside a real iOS Simulator (serve the folder, inject `harness.js`, open the URL with `xcrun simctl openurl`).

## What has and has not been verified
- Verified: all of the above tests; the page in Apple's iPad simulator (scripted clicks); the live page's bytes; real GitHub sync from a real phone (connect, parent code and names written).
- Not verified: finger taps on a real iPad; read-aloud audio; CODAP save and reopen (needed between `s11` and `s12`); dragging in CODAP; the AI grader after its prompt was tightened.

## Lessons from the first day (keep doing these)
- The first real user found two bugs in minutes that 24-session walkthroughs missed: `Node.append(null)` renders the word "null", and a step told the kid to "go to the exit check" to start an experiment. Tests now check visible text; copy still needs a human-eyes pass at phone size.
- Test on the device class the kids use. Desktop passes said nothing about a 390 px screen.
- Any check item can reappear in a warm-up or gate without its session. Every item must make sense alone and carry its own `fig`.
- An outside reviewer (Codex) and a phone audit each found real defects the other missed. Use both before shipping a new unit.

## Backlog
- Write Unit 1C for each track (outlines are in `TRACKS` as `planned`).
- Test-out skips the data-collection sessions that `s11` depends on; let skipped sessions be opened from My path.
- Review stats merge with `Math.max`, so two devices can undercount attempts.
- On a phone, sessions that need CODAP only warn; they do not block.
