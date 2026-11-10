# Authoring sessions and units

Everything needed to write new content with no other context. All content is plain JavaScript object literals in the `CONTENT` section at the top of the `<script>` in `index.html`: `KIDS` and `TRACKS`. There is no build step and no separate content file.

Read `PEDAGOGY.md` for why, `CURRICULUM.md` for what comes next.

## Structure

```
TRACKS = {
  k7: { wins:[...], phases:[ { n, title, when, blurb, units:[ UNIT, ... ] }, ... ] },
  k4: { ... }
}
```

### Track and phase

| Field | Type | Meaning |
|---|---|---|
| `wins` | array of `{after, label}` | "What you can do now" list. `after` is a session id. `label` starts with a capital verb and must read correctly after "New: you can now …" (the page lowercases the first letter). A win is earned when that session is done or its unit's gate is passed. |
| `phases[].n` | number | Phase number, shown on My path. |
| `phases[].title`, `when`, `blurb` | string | Shown on My path. `when` is free text ("About 18 sessions", "Next", "Later"). |
| `phases[].units` | array | Written and outlined units in order. `[]` shows "Written closer to the time". |

### Unit (written)

```js
{ id:"m1c", title:"Unit 1C: Fair or not?", sessions:[ SESSION, ... ], gate: GATE }
```

- `id`: unique in the track. Existing pattern: `s1a`, `m1b` (track letter, phase, unit letter).
- `sessions`: in the order the kid meets them. Six per unit so far.
- `gate`: **required** for a written unit. `autoItems()`, `gateState()` and `position()` read `unit.gate` without checking. A written unit with no gate crashes the page.

### Unit (outlined)

```js
{ id:"m1c", title:"Unit 1C: Fair or not?", planned:true, list:["topic", ...], note:"one sentence" }
```

`position()` stops at the first unit that is `planned` or has no `sessions`. To turn an outline into a written unit, delete `planned`, `list` and `note`, add `sessions` and `gate`, and keep the `id` and `title`. Add an outline for the following unit after it so My path still shows what is coming.

### Session

| Field | Required | Type | Meaning |
|---|---|---|---|
| `id` | yes | string | Unique in the track. Pattern: `s13`, `m13`. Progress is stored under this id. **Never rename or reuse the id of a shipped session.** |
| `title` | yes | string | Shown on Today, My path, the session screens and the mission card. Keep under about 30 characters so it fits beside the timer on a phone. |
| `mins` | yes | number | Time budget for the task. Drives the countdown and all "minutes" labels. |
| `steps` | yes | array | Each step is a string, or `{t:"text", fig:FIGURE}` to show a figure under the text. `k4` (age under 10) sees one step at a time with "Next step"; `k7` sees all steps at once. |
| `check` | yes | array of ITEM | 1–3 items. The session is done when all are resolved. At least one `mc` or `num` item per session is strongly preferred: only those feed warm-ups, gates and the first-try rate. |
| `needs` | no | string | One sentence, overrides `KIDS[kid].needs` on the Today card and the mission card ("You need: …"). Use it when the session needs something unusual (a coin, a ruler, "Any phone, tablet or computer."). |
| `link` | no | `{t, u}` | One outside link, shown as a button above the steps (`t` label, `u` URL, opens in a new tab). **A `link` means "this session needs CODAP on a computer" to the page**: on touch devices Today warns "Do this one on a computer. It uses CODAP…", and the mission card says "This mission uses CODAP on a computer." Do not use `link` for anything else without changing those two strings. Constants: `CODAP_MAMMALS`, `CODAP_NEW`. |
| `show` | no | `{from:"<sid>.<itemId>", kind:"tally"\|"react"}` | Shows an answer saved in an earlier session, under the steps (and at the top of the check when the kid came by "I did it from my card"). `tally` redraws the bar graph from the saved counts. `react` lists the saved reaction times. Shows nothing if that answer does not exist, so the steps must still make sense without it. |

How the first check item changes the screens:

- The button that ends the task reads "Start the experiment" if `check[0].t` is `react`, "Next: type my counts" if `tally`, otherwise "I did it. Go to the quick check". Put a `react` or `tally` item first, never later.
- If `check[0]` is `react`, the other items stay hidden until it is finished.

### Check items

Common fields: `id` (unique in the session; pattern `a`, `b`, `c`; gate extras `x1`…), `t` (type), `q` (the question, shown bold), `fig` (optional FIGURE under the question), `why` (optional; one short sentence shown after a correct answer in `mc` and `num`).

Stored keys are `"<sessionId>.<itemId>"` and `"<gateId>.<itemId>"`. Do not change an item's id after it ships. If a shipped item is wrong, fix its text or answer in place.

| Type | Extra fields | Auto-graded | Feeds warm-ups and gates | Stores an answer |
|---|---|---|---|---|
| `mc` | `opts` (array of strings), `a` (index of the right option, from 0) | yes | yes | no |
| `num` | `a` (number), `tol` (optional, default 0.001) | yes | yes | no |
| `txt` | `rubric` (string), `min` (optional minimum characters, default 15) | only in the hosted copy | no | `{a, ok, fb}` |
| `tally` | `predict` (optional boolean) | yes (internal consistency) | no | `{cats, vals, guess}` |
| `react` | none | yes (internal consistency) | no | `{right, left, predict, mr, ml}` |
| `pick` | `opts` | no | no | writes `interests`. Implemented, not used by any session. |

**`mc`**: options are shuffled each time. In a session a wrong pick is struck out and the kid picks again; first-try is recorded. In warm-ups and gates there is one try.

```js
{id:"b", t:"mc", q:"On a bar graph of things you counted, what does the tallest bar show?",
 opts:["The kind there is the most of","The kind you like best","The biggest thing that was counted"], a:0,
 why:"A taller bar means more things."}
```

Never write "all of the above", "both A and B" or anything that depends on option order.

**`num`**: a number input. Correct when `|answer − a| ≤ tol`. In a one-try setting a wrong answer shows "The answer is `a`".

```js
{id:"b", t:"num", q:"The ordered data are 2, 4, 5, 7, 8, 10, 11, 15. What is Q1?", a:4.5,
 why:"The lower half is 2, 4, 5, 7. Its median is halfway between 4 and 5."}
```

Set `tol` when rounding is reasonable (for a mean of 10.43, `a:10.4, tol:0.05`). Ask for an answer with one obvious form: no units, no fractions, no percent signs.

**`txt`**: a text box, 900 characters at most. Under `min` characters the page asks for more. On the public page the answer is saved and marked "A parent will read this one". In the hosted copy the AI grader compares it with `rubric`, allows one resubmission, and never blocks the session. `rubric` is a sentence for the grader and the parent; the kid never sees it.

```js
{id:"c", t:"txt", min:12, q:"Type one question you could answer by counting or asking.",
 rubric:"Any question that needs counting several things or asking several people. Be generous. One sentence is enough."}
```

The walkthrough tests type a fixed answer of about 200 characters, so `min` above 200 makes the tests fail.

**`tally`**: six rows of "kind" and "count". "Draw my graph" needs at least 2 kinds, whole-number counts from 0 to 500, and at least one count above 0. The page draws a bar graph, then asks which kind had the most and how many in all; both must match the kid's own numbers. With `predict:true` a "My guess for the most" box comes first and is required.

```js
{id:"a", t:"tally", predict:true, q:"Type your guess. Then type each color and how many."}
```

**`react`**: the whole reaction-time experiment (prediction, 8 tries per hand, a `strip2` plot, medians, "which hand was faster"). It takes no fields beyond `id`, `t`, `q`. It is specific to `s01`; reuse it only for a session about that experiment.

```js
{id:"a", t:"react", q:"Which hand is faster? Predict, then test it."}
```

### Figures

A FIGURE is an object with `k` (kind). `figure(f)` returns an SVG in a `div.fig`. Use the same object for the same graph everywhere; share it through a constant (`MONTH_DAYS`, `MONTH_DOT`, `CONTINENTS`) and vary it with `Object.assign({}, CONST, {hideTitle:true})`.

| Kind | Fields | Draws |
|---|---|---|
| `bar` | `cats` (array of strings), `vals` (array of numbers ≥ 0, same length), `title` (optional), `hideTitle`, `hideCats`, `hideVals` (optional booleans) | Vertical bars from 0 with gridlines. `hideTitle` drops the title. `hideCats` prints "?" under every bar. `hideVals` drops the numbers on the side axis. Hide flags build "mystery graph" and "what is missing" items. |
| `dot` | `vals` (array of whole numbers), `title` (optional), `label` (optional axis label) | One row of stacked dots on a number line from the smallest to the largest value. |
| `dots2` | `la`, `lb` (row names), `a`, `b` (arrays of whole numbers) | Two rows of stacked dots on one shared number line. No title or axis label. |
| `strip2` | `la`, `lb`, `a`, `b` (milliseconds) | Two rows binned to 20 ms with a fixed axis label about reaction time. Used by `react` only. |

Minimal examples:

```js
{k:"bar", title:"Favorite pet (made-up class)", cats:["Cat","Dog","Fish","Bird"], vals:[4,7,2,3]}
{k:"bar", cats:["Red","Blue","Green"], vals:[5,3,6], hideTitle:true}
{k:"dot", title:"Books read by 9 kids (made-up)", label:"Number of books", vals:[1,2,2,3,3,3,4,4,6]}
{k:"dots2", la:"Group A", lb:"Group B", a:[4,5,5,6,6,6,7,7,8], b:[3,7,8,8,9,9,9,10,10,11]}
```

**The phone width rule.** `FW()` returns 340 when the window is narrower than 560 px and 520 otherwise. Every figure is laid out at that width when it is rendered. Design every figure for 340:

- `bar`: the plot area is 288 px, so each bar slot is `288 / n` wide. Text is about 6.6 px per character. Names wider than one slot are staggered onto two rows; names wider than two slots collide. So a name may have at most `floor(2 × 288 / n / 6.6)` characters: 14 for 6 bars, 12 for 7, 7 for 12. Abbreviate ("N. America"). 12 bars is the practical maximum.
- `bar` axis steps come from `niceTop()`: by 2 up to 12, by 5 up to 40, by 10 up to 100, by 25 up to 250, then by 50. Choose values so that a kid can read every bar exactly. With a top of 12 and steps of 2, an odd value sits between gridlines; that is acceptable for `k7` and avoidable for `k4`.
- `dot` and `dots2`: a tick is drawn at every whole number from min to max (every second one when the span is over 16). Dots are 12 px wide. Keep the span (max − min) at 20 or less, and no more than about 8 dots on one value.
- Titles: under about 40 characters, or they run off the right edge at 340.
- A figure that needs to be compared with another (two bar graphs side by side) does not fit. Use `dots2` or two items.

**Adding a figure kind** (unit 1C of `k7` needs a scatter plot): write a function that returns an SVG string using the classes `ttl`, `mark`, `axis`, `gl` and width `FW()`, add a branch in `figure()`, add an `aria-label`, and check it in `phone_audit.py` screenshots in both color schemes. Text inside figures is 12 px; the audit flags smaller.

### Gate

```js
gate:{ id:"g-m1c", title:"Gate 1C", n:10,
       product:{label:"Poster about your own question", rubric:["line 1","line 2","line 3","line 4","line 5"]},
       extra:[ ITEM, ... ] }
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Must be `"g-" + unit id`. `walk.py` finds the sign-off checkboxes by that pattern. |
| `title` | yes | "Gate 1C". |
| `n` | yes | Number of questions, 10. The page uses `min(n, pool)` and requires `ceil(0.9 × that)`. |
| `extra` | yes (may be `[]`) | Unseen items, `mc` or `num` only, ids `x1`…. All of them appear in every attempt; the rest of the quiz is a random draw from the unit's `mc`/`num` session items. Write 5 or 6. `why` is optional here; in a one-try quiz it only shows after a right answer. |
| `product` | no | A parent-signed piece of work. `label` names it; `rubric` is an array of short checkable lines (five so far). The kid sees the list on the gate screen; the parent ticks every line in Parent view. |

The pool (auto-graded session items plus extras) must be at least `n`, or the quiz silently shrinks. Six sessions with two auto-graded items each plus five extras gives 17.

## Previewing while you write

- Open `index.html` straight from disk in a browser (`file://…/index.html`). No server is needed. Reload after each edit; a syntax error in `TRACKS` leaves a blank page, so keep the browser console open.
- From Home, "Grown-ups: try the lessons" opens any written session or gate directly, without doing the ones before it and without saving anything. Use it to read a new session end to end.
- Narrow the window to 390 px (or use the browser's device toolbar) and reload: figures pick their width when they are drawn, not when the window is resized.
- To see a session as the kid will, including warm-ups and the Today card, use a private browser window so no real progress is on the device.

## Shipping a unit whole

Ship a unit only when all its sessions and its gate are written. `position()` sends a kid to the gate as soon as every written session in the unit is done, so a unit with one session and a thin gate would be passed in a day and its test-out would mean nothing. Adding sessions to a unit a kid has already passed does not reopen it for that kid; the new sessions show as skipped. Adding a new unit after the last passed one works with no migration: the kid's Today card moves to its first session.

## Content rules learned the hard way

1. **Every check item stands alone.** Any `mc` or `num` item reappears in a warm-up days later and in the gate, without its session, its steps or the item before it. It must carry its own numbers and its own `fig`. Bad: "How many did you count?" Bad: "In the graph above…". Acceptable only with its own figure attached: "In that graph, how many more Green than Blue?" (`m05.b`). Better: name the thing ("How many more Green than Blue?").
2. **Auto-graded items cannot depend on the kid's own data.** The page does not know the kid's notebook. Own-data questions are `txt`, `tally` or the product.
3. **Never send a kid somewhere that is not on the screen.** A step once said "go to the exit check" to start an experiment; there was no such button. Name only buttons, links and words the kid can see, with the exact label. If a step needs an earlier result, show it with `show` or restate it.
4. **Each step is one action.** State what to do, then what should happen ("Click Graph in the toolbar. A new graph of scattered dots appears."). Say what to do if it does not ("stop and tell a parent").
5. **Reading level.**

   | | k4 | k7 |
   |---|---|---|
   | Sentence length | 12 words or fewer, mostly | 20 words or fewer, mostly |
   | Sentences per step | 1–3 | 1–4 |
   | Vocabulary | Words a 9-year-old says. Introduce a term after the idea ("That is the middle: 5. Its fancy name is the median."). | Define each term once, in the step that first uses it. |
   | Steps per session | 3–5 | 4–5 |
   | Math | Counting, adding, subtracting, comparing. No division, fractions (beyond "half a star"), percent or decimals. | Arithmetic and algebra are fine. |

6. **No names, places or identifying details.** No kids' names, family, school, city or street-level detail in steps, questions, options or data. Use "a kid", "a made-up class", "your pet". Label invented data "(made-up)" in the figure title. Check the existing content against this rule too when you touch it.
7. **Time budgets.** `k4`: 8–12 minutes, and the unit's six sessions should sum to about 60. `k7`: 10–20 minutes, about 90 per unit. Count honestly: collecting 12 things and tallying them is 6 minutes, not 2. Trial totals are 118 and 179 minutes; a reviewer caught an earlier overrun.
8. **Answer keys are computed, never trusted.** For every `num` item compute `a` with code. For every `mc` item check that exactly one option is right, including under the figure's actual data. For every figure question read the answer off the data array, not off the picture in your head. The script in the checklist below does part of this.
9. **Medians and quartiles.** Use an odd count for `k4` medians (the "take one from each end" method). For `k7` state the quartile rule in the step (median of each half, middle value left out when the count is odd) and note that software may differ.
10. **Feedback teaches.** `why` is one sentence that gives the reason, not "Correct!". Wrong options should each be a real misconception ("The single highest dot in each group").
11. **Mystery graphs keep the reveal off paper.** On a mission card, once a figure with a hide flag has appeared in a session, later full figures in that session are replaced by "The whole graph is in Data Lab. Guess first, then look." Order steps so the hidden version comes first.
12. **A session must work from the card alone (`k4`).** The card prints the title, `needs`, steps and figures. It does not print the check. Do not put instructions only in a check question.
13. **Do not let a session depend on one earlier session without a fallback.** `s11` accepts either the 7-day log or the `s01` reaction times. `m07` offers a ready-made question.

### What makes a good unseen gate item

- Tests the unit's idea in a context the sessions did not use (pizza toppings, dog breeds, test scores), with new numbers.
- Stands alone and carries its own figure.
- One reading, one right answer, answerable in under a minute without a calculator.
- At least one item per unit where the tempting wrong answer is the unit's main misconception (`g-s1a.x4`: Group A has the single highest dot but Group B sits higher).
- Covers the unit: one extra per main idea, not three on the same idea.
- Not a reworded copy of a session item with the same numbers.

## Pre-ship checklist for content

- [ ] Ids are new and unique; no shipped id was renamed. Gate id is `g-` + unit id.
- [ ] Every written unit has a `gate` with `n`, `extra`, and a pool of at least `n`.
- [ ] Each `mc`/`num` item reads correctly with nothing but its own `q`, `opts` and `fig` in front of you. Read them in shuffled order to check.
- [ ] Every answer key computed (script below) and every `mc` checked for exactly one right option.
- [ ] Every step names only things on the screen, on the card or in the notebook.
- [ ] Reading level and time budget per the table. Read every `k4` step aloud.
- [ ] No names or identifying details: `grep` per `CLAUDE.md`.
- [ ] `wins` updated if the unit earns a new "you can now" line.
- [ ] Figures checked at 340 px in light and dark (`phone_audit.py` screenshots).
- [ ] Tests updated where they hard-code content: `test_gh.py` asserts 12 `k4` mission cards and exactly 2 "The whole graph is in Data Lab" notes; `walk.py` prints expected totals; `harness.js` and `phone_audit.py` name specific session ids for screenshots.
- [ ] All tests pass (`TESTING.md`), then a second reviewer and a phone audit, before the unit ships.
- [ ] `CURRICULUM.md` tables updated.

Answer-key helper. It loads the content section in Node and prints every auto-graded item so the keys can be checked by eye and by code. Adjust the line range if the content section has moved (it runs from the `CODAP_MAMMALS` constant to the `};` that closes `TRACKS`).

```sh
awk '/^const CODAP_MAMMALS/,/^\/\* =+ HELPERS/' index.html | sed '$d' > /tmp/content.js
cat >> /tmp/content.js <<'EOF'
const med = a => { const b=[...a].sort((x,y)=>x-y), n=b.length; return n%2 ? b[(n-1)/2] : (b[n/2-1]+b[n/2])/2; };
for (const k of Object.keys(TRACKS)) for (const p of TRACKS[k].phases) for (const u of p.units) {
  if (!u.sessions) continue;
  const items = [...u.sessions.flatMap(s => s.check.map(i => [s.id, i])), ...u.gate.extra.map(i => [u.gate.id, i])];
  for (const [sid, i] of items) {
    if (i.t === "mc") { if (!(i.a >= 0 && i.a < i.opts.length)) console.log("BAD INDEX", sid, i.id); console.log(sid+"."+i.id, "|", i.q, "=>", i.opts[i.a]); }
    if (i.t === "num") console.log(sid+"."+i.id, "|", i.q, "=>", i.a);
    if (i.fig && i.fig.vals) console.log("   fig", i.fig.k, JSON.stringify(i.fig.cats || ""), JSON.stringify(i.fig.vals), "median", med(i.fig.vals));
  }
  const pool = items.filter(([, i]) => i.t === "mc" || i.t === "num").length;
  console.log("UNIT", u.id, "pool", pool, "n", u.gate.n, pool < u.gate.n ? "POOL TOO SMALL" : "ok", "minutes", u.sessions.reduce((a, s) => a + s.mins, 0));
}
EOF
node /tmp/content.js
```

## Worked example: a complete new session for track k4

Topic 1 of unit 1C, "Coin flips: predict, then flip 20 times". This object is valid as written. It was pasted into a copy of `index.html` inside a written `m1c` unit and passed `walk.py`.

```js
{ id:"m13", title:"Heads or tails?", mins:10, needs:"A coin, your data notebook and a pencil.",
  steps:["Get one coin. You will flip it 20 times.",
         "Before you flip, guess. Will you get more heads or more tails? Say your guess out loud.",
         "In your notebook, write Heads on one line and Tails on the next line.",
         "Flip the coin 20 times. Make one tally mark after each flip.",
         "Count the marks on each line. Then type your guess and your counts."],
  check:[
   {id:"a", t:"tally", predict:true, q:"Type your guess. Then type Heads and Tails and how many of each."},
   {id:"b", t:"num", q:"A coin was flipped 20 times. It landed on heads 12 times. How many times did it land on tails?", a:8, why:"20 − 12 = 8."},
   {id:"c", t:"mc", q:"Two kids each flip a coin 20 times. One gets 9 heads. The other gets 13 heads. What does that show?",
    opts:["Flipping a coin does not come out the same every time","One kid counted wrong","One coin is broken"], a:0,
    why:"Chance makes the counts come out a little different each time."}
  ]}
```

Why it is shaped this way:

- Predict first, then real objects, then the page draws the graph (`tally` with `predict:true` is first in `check`, so the task ends with "Next: type my counts").
- `b` and `c` carry their own numbers. They make sense in a warm-up next week.
- Every sentence is short. No division or fractions. 20 − 12 is within school math.
- `needs` names the coin, so the Today card and the mission card say so.
- A 10/10 tie is fine: the page accepts either kind as "the most".

Where it goes. Replace the outlined unit with a written one (the gate is required; five or six extras when the unit is complete):

```js
{ id:"m1c", title:"Unit 1C: Fair or not?", sessions:[
   /* the m13 object above, then m14 … m18 */
  ], gate:{ id:"g-m1c", title:"Gate 1C", n:10, extra:[
   {id:"x1", t:"num", q:"A coin was flipped 30 times. It landed on tails 14 times. How many times did it land on heads?", a:16}
   /* x2 … x5 */
  ]}}
```

Then add `{after:"m13", label:"Test a guess with a coin"}` to `TRACKS.k4.wins` if the unit should announce it, update the tests listed in the checklist (13 mission cards), and run everything in `TESTING.md`.
