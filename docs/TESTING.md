# Testing

All tests are in `tests/`. They are plain Python scripts using Playwright (sync API), not a test framework. Each prints its result; read the output. Runtimes were measured on 10 November 2026 in a Linux container.

## Setup

```sh
pip install playwright
python3 -m playwright install webkit      # Safari engine, used by three scripts
# Chromium: the scripts launch system Chrome at /usr/bin/google-chrome.
export CHROME=/path/to/chrome              # only if Chrome is elsewhere
```

The scripts open `index.html` from disk (`file://`), so no server is needed except for the simulator harness. Run them from `tests/` or from a scratch folder: `walk.py`, `walk_webkit.py` and `test_gh.py` write screenshots to the current directory (`tests/*.png` is git-ignored).

## Run everything

```sh
cd tests
python3 walk.py && python3 walk_webkit.py && python3 test_gh.py && python3 test_modes.py && python3 phone_audit.py
```

About six and a half minutes in total. All five must be clean before a push. "Clean" is defined per script below; only assertion failures give a non-zero exit code, so a zero exit is not enough.

## The scripts

| Script | Engine and profile | Runtime | Covers | Clean means |
|---|---|---|---|---|
| `walk.py` | Chromium, 820×1100 | 20 s | Both tracks end to end: every session, every warm-up (review items are aged after each session so warm-ups always appear), all gates, project sign-off through Parent view, reload persistence, test-out of a unit on a fresh profile, `Store.merge` field rules, epoch and Erase, a dark-mode screenshot. Asserts no stray `null`/`undefined`/`NaN`/`[object` text on task and check screens. Deliberately answers wrong first in `m02` and `s04`. | No traceback; `ERRORS: []`; both tracks reach `END`; `merge: [2, 2, 3, 3, 9, 2, 12]`; `epoch/reset: [0, 1, 0, 1, 0, 1, 1]`; `after reload totals` equal to the number of written sessions per track (now `[12, 12, 12, 12, 'device']`; meaning below the table); `test-out: ok ['session', 's07', 0, 6]`. |
| `walk_webkit.py` | WebKit, iPad (gen 7) emulation | 40 s | The same walk in the Safari engine. Takes the page URL as an optional first argument. It does not run the stray-text assertions. | Same lines as `walk.py`. |
| `test_gh.py` | Chromium, several browser contexts as separate devices, GitHub API mocked by the `Mock` class | 35 s | Sync: short token, bad token, wrong repo, public repo refused, read-only token, nothing stored after a failed connect, connect and write test, parent code and names reach the repo, second device receives them, a device with its own code adopts the family's, concurrent write (409) retried and merged, Erase reaches another device, offline warning and catch-up, revoked token message, disconnect. Mission cards: count, reveal kept off the card, PDF written to `tests/out/`. Card path: `m08` shows the drawn graph in the check; no card button for the older kid. Nav tap targets at least 44 px. | Every line starts `PASS`; `page errors: []`; `FAILED: []`. |
| `test_modes.py` | Chromium at 390×844 with the same mock, then WebKit iPhone 13 with real taps | 45 s | Tryout mode: entry on Home without the parent code, all 24 sessions and 4 gates listed and unlocked, banner on every screen, the step toggle for the younger track, finish returns to the list, and proof that nothing is saved: `Store` docs and `localStorage` byte-identical before and after, zero API requests, `Store.save` never called. Stop, keep going, start over: the note is written and cleared at the right times, resume lands on the same stage and step, counts do not move until the session is finished, nothing about the note reaches the mock repo. Audits each screen for stray text, sideways overflow and small buttons. Screenshots in `tests/out/modes_*.png`. | Every line `PASS` (142 checks at the time of writing); `page errors: []`; `N passed, 0 failed`; `FAILED: []`. Read the screenshots. |
| `phone_audit.py` | WebKit, iPhone 13 (390 px), two passes | 4 min 15 s | Dark pass with real timing and real taps on every control; light pass with fast timing and display names set. On every screen: stray text (including in input values and labels), elements past the viewport edge, tap targets, inputs under 16 px (iOS zoom), figure text size, clipped text, contrast, whether the primary button is below the fold, console errors, failed requests, taps that did not advance. Writes `tests/phone_audit_report.json` and `tests/phone_shots/*.png`. Optional argument `dark` or `light` runs one pass. It only reports; it never fails. | `CRASH: none`; `ERRORS: none`; `TAPS THAT DID NOT ADVANCE: none`; no findings outside the accepted list below the table; and the screenshots look right. |
| `harness.js`, `server.py`, `run.py` | A real iOS Simulator, or WebKit iPad emulation | minutes, manual | The same walkthrough run from inside the page, for an environment Playwright cannot drive. See below. | The green-on-black bar reads `HARNESS DONE … errors=0`; the report has no `fail`. |

`after reload totals: [a, b, c, d, mode]` (`walk.py`, `walk_webkit.py`): `a` sessions done on `k7`, `b` sessions done on `k4`, `c` sessions written for `k7`, `d` sessions written for `k4` (`counts(kid).total` and `.authored`), then `Store.mode`, which is `'device'` because the walk has no sync backend. Clean is `a == c` and `b == d`. The script asserts none of this; this line is the only expectation, so update it when sessions are added.

Accepted `phone_audit.py` findings. The report file is git-ignored, so a fresh clone has no earlier run to compare with. These are the only findings accepted today; anything else, in either pass, is a defect:

| Category in the output | Accepted instance |
|---|---|
| `3 small tap target` | Only the 22×22 parent sign-off checkboxes in Parent view (`input[checkbox]`, labels `rb-g-s1b-0…4` and `rb-g-m1b-0…4`). |
| `5 figure text shrinks below 11px` | Figures shown in a task step, at 9.7 px (`AUTHORING.md`, "Rendered text size"). |
| `x text under 13px` | Only the 12.5 px pills: `span.pill`, `.pill.now`, `.pill.good`, `.pill.warn`. |
| "primary button below the fold" list at the end of each pass | Long task, check and gate-quiz screens where the kid scrolls to the button. A list, not a finding category. |

A new unit adds instances of the same kinds (five more checkboxes for a new product, more step figures); a new category or a new kind of element does not pass.

`DATALAB_FORBID`: set it to a regular expression of names that must never appear in the page, and `test_gh.py` fails if `index.html` matches. The owner keeps the real pattern out of the repo; ask the owner for it, or have the owner run the script. If the variable is unset or empty the check did **not** run: the line `PASS source has no forbidden names` still prints, vacuously.

### The simulator harness

`harness.js` clears storage, walks both tracks with the same solver, audits tap targets and overflow on chosen screens, and POSTs a JSON report. `server.py` serves the site folder on `127.0.0.1:8766` and saves the report to `/tmp/datalab-report.json` (`REPORT` and `SITE` override the paths).

1. Make `test.html`: a copy of `index.html` with `<script src="tests/harness.js"></script>` added before `</body>`. `test.html` is git-ignored. Never commit it and never deploy it.
2. `python3 tests/server.py &`
3. Open `http://127.0.0.1:8766/test.html` in the target: `xcrun simctl openurl booted http://127.0.0.1:8766/test.html` on a Mac with Xcode, or `python3 tests/run.py` for WebKit iPad emulation. Append `?stop=m05` to stop after one session and inspect the screen.
4. Read the bar at the bottom of the page and the report file.

## What the tests cannot catch

| Gap | Why | Covered by |
|---|---|---|
| Whether a step makes sense to a child | The solver reads the answer key and clicks. It never reads the steps. | Read-aloud pass; the second reviewer. |
| A step that points to something that is not on the screen | Text is not checked against the UI. | Human read at phone size. |
| Wrong answer keys | The solver uses the key, so a wrong key passes. | The answer-key helper in `AUTHORING.md`; the second reviewer. |
| Items that do not stand alone | Warm-ups are solved by key, not read. | Shuffled read of all items. |
| Real fingers: double taps, fat-finger misses, the on-screen keyboard covering a field, rotation | Emulation sends synthetic events and has no keyboard. | Real-finger phone pass. |
| Real GitHub: rate limits, token expiry, CORS changes, slow networks | The API is mocked. | One real connect per release, by the owner. |
| The hosted copy: artifact database, coach, grader, Claude voice | `window.claude` does not exist in the tests. | Manual, in the owner's account. |
| Speech | No audio in headless browsers. | Manual. |
| CODAP itself: link still loads, menus still named as the steps say, drag and drop, save and reopen | Outside the page. | Manual CODAP pass. |
| Printing on a real printer | Only a PDF is generated. | Print the cards once. |
| Visual judgment | Numbers do not see an ugly or confusing screen. | Read the screenshots. |

## Manual checks still needed

Do these before a new unit ships and after any change to layout, session flow or sync.

1. **Real-finger phone pass.** On a real phone, with a thumb: one full session per track including the reaction-time test and a tally, a gate quiz, stop and resume, Parent view, connect. Watch for double-tap zoom, the keyboard hiding the field or the button, and anything needing two hands.
2. **Read-aloud.** Read every new `k4` step and question aloud at a child's pace. Any sentence that needs a breath in the middle is too long. Then, on a device with sound, tap "Read it to me" on one step and one question.
3. **CODAP save and reopen.** On a computer: open each CODAP link, follow the steps exactly as written, and for `s11` → `s12` confirm a table typed into a blank document survives closing the tab (or that the screenshot instruction is enough). Check the menu names against the step text.
4. **Print one set of mission cards** from Parent view and check that no card splits across pages and that mystery graphs do not reveal their answer.
5. **One real sync round trip**: do a session on one real device, see it on a second.

Record what was and was not done in `CLAUDE.md` under "Verified / not verified". Do not move an item to "verified" on the strength of an emulator.

## The rule for new units

A new unit does not ship until all three have happened, in this order:

1. All scripts above are clean, with the tests' hard-coded expectations updated for the new content (see the checklist in `AUTHORING.md`).
2. A **second reviewer** has read every new session, question and answer key cold, with only `PEDAGOGY.md` and `AUTHORING.md` as context. A different model or a person, not the author. Ask it to compute every numeric key, to answer every item in shuffled order without the steps, and to say whether it would run the unit with its own kids.
3. A **phone audit** has been run and its screenshots read by the author, in both color schemes.

On the first day each of the last two found real defects the other missed, and the first real user found two more in minutes that neither had caught. That is why the manual pass is not optional either.

## Adding a test

- Reuse `SOLVE` from `walk.py` so every script answers items the same way. `test_gh.py` and `test_modes.py` read it out of `walk.py` by regex. `walk_webkit.py`, `phone_audit.py` and `harness.js` carry their own copies. When adding an item type, extend all four copies.
- Use the `Mock` class in `test_gh.py` for anything that touches sync. Never point a test at a real repo.
- Assert on visible text for anything a kid reads. The two first-day bugs were both visible-text bugs.
- Prefer state assertions through page globals (`VIEW`, `Store.get`, `counts`, `position`) over timing.
