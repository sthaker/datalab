# Architecture

The whole app is `index.html`: one `<style>` block, a four-element HTML shell, and one `<script>`. Vanilla JS, no framework, no build step, no dependencies except two Google Fonts. Every screen is built by `el()` calls and swapped into `<main id="app">` by `render()`.

Sections are marked in the file with `/* ===== NAME ===== */` banners. Search for the banner; line numbers move.

## Code map

| Section banner | Main names | Owns |
|---|---|---|
| `<style>` | `:root` tokens, component classes | All styling. See "CSS conventions". |
| `CONTENT` | `CODAP_MAMMALS`, `CODAP_NEW`, `MONTH_DOT`, `MONTH_DAYS`, `CONTINENTS`, `KIDS`, `TRACKS` | Every word of curriculum. Schema in `AUTHORING.md`. `KIDS[kid]` has `dflt` (label when no name is set), `tone` (`s` or `m`, picks the accent color), `age` (under 10 switches on one-step-at-a-time, read-aloud buttons and the card button), `weekly` (goal, 3), `needs` (default "you need" sentence). |
| `HELPERS` | `el`, `dstr`, `today`, `addDays`, `weekStart`, `shuffle`, `withTimeout`, `esc` | `el(tag, attrs, ...kids)` is the only DOM builder. It skips `null` and `false` children. Attribute `svg` sets `innerHTML` (used for generated figures only); `on*` adds a listener. Dates are local `YYYY-MM-DD` strings; weeks start on Monday. |
| `content lookups` | `unitsOf`, `findSession`, `findGate`, `autoItems`, `itemByKey` | Reading `TRACKS`. `autoItems(unit)` is the pool of `mc`/`num` items with keys `sid.itemId` and `gateId.itemId`. Also defines `KIDS[k].name` and `.named` as getters over the parent doc, `TOUCH`/`TAP`, and `inClaude()`. |
| `GITHUB SYNC` | `GH.cfg`, `GH.setCfg`, `GH.db`, `GH.test`, `GH.fail` | The GitHub contents API backend. Exposes the same `db.doc(path).get()/set()` shape as the Claude artifact db. |
| `STORE` | `Store.blank`, `get`, `save`, `pull`, `push`, `merge`, `adopt`, `reset`, `connect` | All persistent state: memory, `localStorage`, remote. |
| `UNFINISHED SESSION` | `WIP`, `activeMin`, `isReal`, `wipSave`, `wipLine` | The device-only note of where a kid stopped. |
| (after it) | `AI.connect`, `AI.speak`, `AI.grade`, `AI.coach` | Claude-only pieces plus browser speech. |
| `FIGURES` | `FW`, `niceTop`, `barFig`, `dotRows`, `stripFig`, `median`, `figure` | SVG strings for the four figure kinds. |
| `PROGRESS LOGIC` | `gateState`, `position`, `counts`, `winsOf`, `logReview`, `BOX_DAYS`, `schedule` | Everything derived from state: where the kid is, what is passed, streaks, review scheduling. Pure functions over `Store.get(kid)` except `schedule` and `logReview`, which mutate it. |
| `ITEM WIDGETS` | `renderItem(kid, sid, item, done, opts)` | One function, one branch per item type. Calls `done({first, value?, interests?})` exactly once when resolved. `opts`: `oneShot` (warm-ups and gates), `noShuffle`, `practice`, `tryout`. |
| `VIEWS` | `VIEW`, `go`, `render`, `renderNav`, `renderSync`, `viewHome`, `viewKid`, `viewPath` | Routing and the simple screens. |
| `session` | `startSession`, `restartSession`, `sessionRow`, `tryBar`, `showBlock`, `viewSession`, `selfReport`, `finishSession`, `coachBox` | The session flow and its four stages. `finishSession` is the only writer of `done[sid]`. |
| `gate` | `makeQuiz`, `viewGate` | Gate quiz, score, product panel. The only writer of `gates[gid].quiz`. |
| `try the lessons` | `viewTryout` | The grown-up tryout list. |
| `parent` | `parentOpen`, `viewParent`, `syncCard`, `viewCards` | Parent code, names, per-kid numbers, sign-off (the only writer of `gates[gid].sign`), erase, copy, sync connect and disconnect, mission cards. |
| `BOOT` | `boot` IIFE | Initial route from the hash, `Store.connect` then pull all three docs, `AI.connect`, timers and event listeners. |

## State

Three documents, each a plain JSON object: `k7`, `k4`, `parent`. All start from `Store.blank()`.

### Kid doc (`k7`, `k4`)

| Field | Shape | Written by | Meaning |
|---|---|---|---|
| `v` | `1` | `blank` | Schema version. Nothing reads it yet. |
| `epoch` | number | `Store.reset` | Bumped by Erase. See merge. |
| `ts` | ms timestamp | `Store.save` | Last local save. |
| `done` | `{ [sid]: {t, first, auto, mins, card?, solo?, feel?} }` | `finishSession`, `selfReport` | `t` finish time; `auto` number of `mc`/`num` items; `first` how many of those were right first try; `mins` minutes actually worked (all sittings, capped at 3 × the session's `mins`; the session's `mins` for a card run); `card:1` if started from "I did it from my card"; `solo` index into `SOLO`; `feel` index into `FEEL`. |
| `ans` | `{ [sid]: { [itemId]: value } }` | check callback in `viewSession`, `finishSession` | Stored answers: `txt` `{a, ok, fb}`, `tally` `{cats, vals, guess}`, `react` `{right, left, predict, mr, ml}`. Read by `show`, Parent view, and to refill a text box. |
| `rev` | `{ [key]: {box, due, u} }` | `schedule` | Spaced review. `key` is `sid.itemId`; `box` 0–4 indexes `BOX_DAYS`; `due` is a date string; `u` update time. |
| `gates` | `{ [gid]: {quiz?, sign?, ext?} }` | `viewGate`, `viewParent` | `quiz`: `{best, last, n, t, d, tries, missed}`. `sign`: `{t}`. `ext` is merged but nothing writes it (reserved for outside checks). |
| `log` | `[{d, sid}]` | `finishSession`, `logReview` | One entry per first completion, plus at most one `{sid:"review"}` per day. Drives week counts and streaks. |
| `interests` | `[string]` | `pick` items | Unused by current content. |
| `stats` | `{fn, fok, rn, rok}` | `finishSession`, warm-up callback | First-try attempts and hits on check items; review attempts and hits. |

### Parent doc (`parent`)

Same blank shape (the kid fields stay empty) plus:

| Field | Meaning |
|---|---|
| `code` | The parent code, plain text, at least 4 characters. A speed bump, not security: anyone with the progress repo or the device's storage can read it. |
| `names` | `{k7?: string, k4?: string}`. Display names typed in Parent view. The only place names exist. |

### Where state lives

| Key in `localStorage` | Content | Synced |
|---|---|---|
| `datalab:k7`, `datalab:k4`, `datalab:parent` | The three docs | Yes, to `state/<key>.json` |
| `datalab:gh` | `{repo, token}` for this device | Never |
| `datalab:wip:k7`, `datalab:wip:k4` | Unfinished-session note | Never |
| `datalab:probe` | Write test at boot when no backend | Never |

`Store.data[k]` is the in-memory copy. `Store.adopt(k, next)` replaces its contents in place so views holding a reference stay valid.

## Merge semantics and epochs

`Store.merge(a, b)` is symmetric and runs on every pull and before every push.

1. If the epochs differ, the higher epoch wins whole. Nothing from the lower epoch survives. This is how Erase reaches other devices and why erased progress cannot merge back.
2. Same epoch, per field:

| Field | Rule |
|---|---|
| `done[sid]` | The entry with the later `t`. `ans[sid]` follows the winning side, then falls back to the other. |
| `ans` (sessions not in `done`) | Either side, first found. |
| `rev[key]` | The entry with the later `u`. |
| `gates[gid].quiz` | The attempt with the later `t`, but `best` and `tries` are the max of both. |
| `gates[gid].sign`, `ext[*]` | Later `t`. |
| `log` | Union, deduplicated on `d|sid`, sorted by date. |
| `interests` | Union. |
| `stats.*` | Max of both. Known flaw: two devices that each add attempts undercount. |
| `code`, `names` | From the side with the later `ts`. |
| `ts` | Max. |

`Store.reset(k)` builds a blank doc with `epoch + 1` and saves it. `adopt` clears that kid's WIP note whenever the epoch changes.

A consequence: there is no "un-erase", and there is no way to remove a single session by editing one device. Edit the JSON in the progress repo and bump `epoch` if a manual correction is ever needed (see `OPERATIONS.md`).

## Sync backends

`Store.connect()` picks one backend at boot:

| Condition | `Store.kind` | Backend |
|---|---|---|
| `window.claude.use` exists (the hosted Claude artifact) | `claude` | `await window.claude.use("db")`, documents `state/k7`, `state/k4`, `state/parent` in the artifact's database |
| Otherwise, `datalab:gh` holds a repo and token | `github` | `GH.db(cfg)`: files `state/<key>.json` in that repo through `https://api.github.com/repos/<owner>/<repo>/contents/…` |
| Otherwise | `""` | None. Device storage only. |

Both expose `db.doc(path)` with `get()` returning `{exists, data()}` and `set(obj)`.

GitHub details: `get` is a `GET` with a cache-busting query and `cache:"no-store"`; it remembers the file's blob `sha`. `set` is a `PUT` with base64 content and that `sha`. A stale `sha` returns 409 or 422, which `GH.fail` marks as `conflict`. Each write is one commit in the progress repo with the message "Data Lab progress: state/<key>".

Flow:

- `Store.save(k)`: stamp `ts`, write `localStorage`, call `push(k)`, update the status line. Local write comes first, always.
- `Store.push(k)`: one write per doc at a time (`writing`, `queued`). Read remote, merge, write local, write remote. On a `conflict` it retries the whole read-merge-write once. Any other failure sets `fail[k]`, `err` (HTTP status or `"net"`) and mode `device`.
- `Store.pull(k)`: read remote (10 s timeout), merge into memory, write local, and push back if the merged result differs from what the remote had. Returns whether local data changed, so the caller can re-render.
- Retries: `retryFailed` pushes every doc in `Store.fail` on the `online` event and every 60 s. It does nothing while `err === 401`, because a dead token will not start working. When the page becomes visible again, all three docs are pulled, which also pushes anything the remote lacks.
- Pulls happen at boot, when the tab becomes visible, on Connect, and for one kid when their card is tapped on Home.

`Store.mode` drives the status line (`renderSync`): `cloud` (all docs synced), `device` (saved locally; amber if a backend exists and is failing), `none` (even `localStorage` failed; the page tells the kid to use the notebook).

`GH.test(cfg)` runs on Connect before anything is stored: repo readable, repo private (a public repo is refused), then a real write to `state/device-check.json`. Each failure has its own message. After a successful Connect the page pulls all three docs and adopts the remote parent `code` and `names` over any local ones, then relocks Parent view.

## Unfinished sessions (WIP)

`WIP` stores `{sid, stage, stepIdx, card, startedAt, minutesSoFar, t}` under `datalab:wip:<kid>`.

- Written by `wipSave(v)` for real sessions only (`isReal`: not practice, not tryout, has a session id) in the `task` and `check` stages: on every render of those stages, on `go()` away, on "Stop for now", and when the page is hidden.
- Read by `WIP.get(kid)`, which discards the note unless it is under 14 days old and the kid's current position is still that session.
- Today then shows where the kid stopped, "Keep going" (resume: no warm-up, same stage and step, clock continues from `minutesSoFar`) and "Start this session over".
- Each session screen has "Stop for now" and "Start over" (with a confirmation). `restartSession` goes back to step 1, drops this run's answers and zeroes the clock.
- Resuming at the check re-asks the items. Typed answers are still in the boxes because `txt`, `tally` and `react` values are saved to `ans` as soon as each resolves.
- Cleared on finish, on start over, on Erase (epoch change), and when stale.
- Time away does not count: `park` on `visibilitychange`/`pagehide` folds elapsed time into `v.base` and stops the clock; it restarts on return.
- Never synced. A session stopped on the phone cannot be resumed on the iPad; it starts from the top there.

## Routing and views

`VIEW` is one object; `go(v)` replaces it and renders. There is no router library and no history stack. The URL hash is set only for `#k7`, `#k4` and `#parent`, so those three can be bookmarked or put on a home screen.

| `VIEW.name` | Function | Reached from | Notes |
|---|---|---|---|
| `home` | `viewHome` | "Switch person", boot | Two kid cards and the tryout entry. |
| `kid` | `viewKid` | A kid card, "Today" | The one loud card is the next session, the gate, or "finished everything written". Also quick review, time-log reminder (`k7`), wins, progress bar. |
| `path` | `viewPath` | "My path" | All phases. Done sessions can be reopened as practice. Outlined units show their topic list. |
| `session` | `viewSession` | `startSession` | `stage`: `warm` → `task` → `check` → `done`. Flags: `practice`, `tryout`, `card`, `resumed`. `sid:null` is a quick review (warm-up only). |
| `gate` | `viewGate` | Today, My path, tryout | Quiz in progress (`v.quiz`), score (`v.justScored`), or the summary with the product panel. |
| `tryout` | `viewTryout` | "Grown-ups: try the lessons" on Home | Every written session and gate of both tracks, nothing locked, no parent code. Sessions run with `practice:true, tryout:true`; gates with `tryout:true`. Nothing is written to `Store`, nothing is counted, nothing syncs, no WIP note. A banner says so on every screen. `k4` sessions get a "Show all steps" toggle. |
| `parent` | `viewParent` | "Parent" | Locked by `parentOpen`, which resets whenever `go()` leaves `parent` or `cards`. |
| `cards` | `viewCards` | Parent view → Print | One printable card per written session of that track. |

Practice vs tryout vs real:

| | Real | Practice (reopen a done session from My path, or from a failed gate) | Tryout |
|---|---|---|---|
| Warm-up | If items are due | No | No |
| Writes `done`, `log`, `stats`, `rev` | Yes | No | No |
| Writes `ans` | Yes | No | No |
| AI grading of `txt` (hosted) | Yes | No | No |
| WIP note | Yes | No | No |
| Nav shows Today / My path | Yes | Yes | No |

## The AI pieces (hosted Claude artifact only)

`AI.connect()` asks for the artifact capabilities `sample` and `tts`. Outside Claude both are `null`.

| Piece | Needs | Behavior | Outside Claude |
|---|---|---|---|
| Coach (`coachBox`, `AI.coach`) | `sample` | A "Stuck? Ask the coach for a hint" panel on the task screen. The prompt carries the lesson steps and the check questions it must not answer. Six questions per session. Replies capped at 500 characters. | Not rendered. |
| Written-answer grading (`AI.grade`) | `sample` | Returns `{ok, fb}` against the item's `rubric`. One resubmission, then the answer is saved either way with the verdict. | Returns `null`; the answer is saved as "A parent will read this one". |
| Read-aloud (`AI.speak`) | `tts`, or the browser's `speechSynthesis` | "Read it to me" on steps and questions for a kid under 10. | Works wherever the browser has speech synthesis. Not verified on a real device. |

Both prompts include the kid's display name and age. That text goes only to the Claude sampling capability in the owner's account, never to the public page's network.

## CSS conventions

- **Tokens.** Every color is a custom property on `:root`: `--bg`, `--grid`, `--card`, `--ink`, `--muted`, `--line`, `--good`, `--warn`, `--bad` (each with a `-bg`), `--on-accent`. Dark values are defined twice: under `prefers-color-scheme: dark` and under `:root[data-theme="dark"]`. Change both. Never hard-code a color in a component or in an SVG; figures use the classes `ttl`, `mark`, `axis`, `gl`.
- **Per-track tint.** `--accent`/`--tint` default to the `k7` pair (`--accent-s`, `--tint-s`). `body.kid-k4` swaps in the `k4` pair (`--accent-m`, `--tint-m`). `renderNav` toggles the class from `VIEW.kid`.
- **Type.** Body is Lexend, 16.5 px; display is Bricolage Grotesque. Both load from Google Fonts with system fallbacks. Inputs inherit the body size, which keeps iOS from zooming on focus (it zooms under 16 px).
- **Layout.** One 720 px column (`.wrap`). `.stack` is a vertical flex with 14 px gaps; `.row` is a wrapping horizontal flex. `.card` is the container; `.card.next` is the single loud element on a screen.
- **Buttons.** `.primary` (one per screen; tests click `button.primary` to advance), `.second`, `.ghost`, `.quiet`. Tap targets are at least 44 px high for navigation and 40 px elsewhere.
- **Phone rules.** One breakpoint, `max-width:520px`: smaller nav buttons, brand subtitle hidden, kid cards in one column, and the status line hidden during a session or gate unless it is a warning. Figures use their own breakpoint in JS (`FW()`, 560 px). Nothing may scroll sideways at 390 px; `.fig` and tables scroll inside their own box.
- **Print rules.** `@media print` forces black on white, hides the header, the status line and anything with `.noprint`, and removes shadows. `.mcard` avoids page breaks inside a mission card.
- **Motion.** One transition (the progress bar), only under `prefers-reduced-motion: no-preference`.
- **Text nodes.** Always build text through `el()`. `Node.append(null)` prints the word "null"; `el()` drops `null` and `false`. Never call `.append()` or `.replaceChildren()` with a value that can be `null`.

## Test hooks in the app

- `window.__FAST = true` shortens the reaction-time waits to 30 ms.
- Globals the tests read or call: `VIEW`, `go`, `position`, `counts`, `gateState`, `unitsOf`, `findSession`, `Store`, `today`. Renaming any of them breaks the tests.
- Selectors the tests rely on: `#app .item`, `.opts button`, `button.primary`, `button.second`, `.tally-grid input`, `.reactpad.go`, `.chips button`, `#pcode`, `#ghrepo`, `#ghtok`, `#sync`, `.mcard`, `input[id^='rb-g-…']`, and several button labels ("Draw my graph", "Check", "Ready", "Sign off", "Set code", "Open", "Connect", "Save names", "Disconnect this device", "I did it from my card").
