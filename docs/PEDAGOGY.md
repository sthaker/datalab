# Pedagogy

Why the sessions are shaped the way they are, and where each rule is enforced in `index.html`. If a rule here is not enforced by the page, it says so.

## Design principles

| Principle | Why | How it is built in |
|---|---|---|
| Predict, then test, in the first session | A kid who makes a graph of their own data inside ten minutes has a reason to come back. An early draft opened with reading and writing; the reviewer said it would not hold a kid. A prediction also makes the result a surprise or a confirmation instead of a fact. | `s01` is a reaction-time experiment (`react` item). `m01` is guess, sort, count (`tally` with `predict:true`). Both end with a graph the page draws from the kid's numbers. |
| Their own data | Motivation is the binding constraint. Questions about your own week or your own shelf are harder to click through, and no chatbot knows the answers. | `k7` logs sleep, screens and moving from `s03` and analyses them in `s11`/`s12`. `k4` counts things at home (`m01`, `m03`, `m07`) and tells that story in `m12`. |
| Short, fixed-length sessions | The work sits on top of school. A fixed small size removes the "how long will this take" objection. | Each session has `mins` (8–20). The task screen shows a countdown; at zero it shows "Time" and nothing is blocked. |
| Every session ends in a check | Practice testing is one of the two study techniques with the best evidence (Dunlosky et al., 2013). The check also decides whether the session counts. | `finishSession` only runs when every check item is resolved. `done[sid]` is written there and nowhere else. |
| Spaced review, widening intervals | Distributed practice is the other technique with the best evidence. | Every auto-graded check item (`mc`, `num`) enters a Leitner schedule, `BOX_DAYS = [1,3,7,14,30]`. A miss returns to 1 day. Up to 3 due items open the next session as a warm-up; up to 5 form a "Quick review". |
| Mastery gates with unseen items | Moving on at 90% keeps gaps from compounding. Reusing lesson questions would test memory of the questions. | Each unit has a `gate`: 10 questions, one try each, 9 to pass (`Math.ceil(n*0.9)`). All `extra` items (5 or 6, never shown in a session) are included; the rest are drawn from the unit's `mc`/`num` items. Retakes are unlimited. A failed quiz lists the sessions behind the missed questions. |
| A product, signed off | A quiz shows recall and some transfer. The project is the better evidence, and the page cannot see a notebook. | The second unit's gate has a `product` with a five-line rubric. A parent ticks every line in Parent view; that writes `gates[gid].sign`. |
| Test-out | A kid who already knows a unit should not sit through it. | "Know this unit already? Take the gate quiz" is on the Today card. Passing skips the unit's remaining sessions. Skipped sessions show as "skipped", never as done. |
| Paper first for the younger kid | Starting on a screen is a barrier for the 4th grader, and the sessions are about real objects. | Every `k4` session is also a printable mission card (Parent view → Print). "I did it from my card" jumps to the check and records `done[sid].card = 1`. On screen, `k4` steps appear one at a time. |
| Weekly streak over daily | The plan is three a week. A daily streak would punish the plan. | Pips show sessions this week against `KIDS[kid].weekly`. "Weeks on target" is the main streak. "Days in a row" appears only when it is 2 or more and never shows as broken. |
| Self-report chips | Independence and enjoyment drive the week-4 decision as much as the count. Asking is cheap. | After a session: "Did you do it by yourself?" (`solo`) and "How was it?" (`feel`), stored on `done[sid]`. Optional; the kid can skip them. |
| A coach that does not hand over answers | A tutor that gives answers trains kids to ask for answers. | Hosted copy only. The coach prompt forbids answering check questions and allows one hint at a time, six questions per session. The public page has no AI. |
| No ceiling, no guilt | A kid who is into it should be able to go fast; a missed week should cost nothing. | "Keep going" after every session. No make-up work. No points, leaderboard between the kids, cartoon rewards or guilt messages. |

Borrowed and not borrowed: the mastery and short-session mechanics come from Alpha School's published description; its results are its own claims and are not relied on. Paying per session was left out on purpose. Rewards at gates, chosen by the kid, are a parent decision and are not in the page.

## What the parent does and avoids

Setup, once (about an hour): connect each device (see `OPERATIONS.md`), set the parent code, type the names, print the `k4` mission cards, try a session of each track in "Grown-ups: try the lessons", buy two notebooks, agree a slot with each kid, and say the deal out loud: four weeks, then the kids get a vote.

Weekly, 10 minutes (the same list is printed at the bottom of Parent view):

1. Check sessions this week. Under 3 means the time slot needs fixing, not the kid.
2. Read one written answer per kid. On the public page nothing grades written answers.
3. Sign off any waiting project with the kid next to you.
4. If "exit checks right first try" is under 70% two weeks running, the pace is too fast. Slow the next unit.

Avoid: reminding mid-week, sitting in on sessions, and correcting the conclusions in projects. Ask "how do you know?" instead.

## The weekly system

Every session has the same parts, so a kid never has to decide what to do.

| Part | Length | What happens |
|---|---|---|
| Warm-up | about 2 min | Up to 3 due review questions, one try each. Skipped when nothing is due. |
| Task | 8–20 min | Numbered steps, one optional link, a countdown. |
| Check | about 2 min | 1–3 items on what was just done. Finishing it marks the session done. |
| Done | seconds | Self-report chips, any new "you can now" line, "Keep going" or "Done for today". |

Three rules keep it from collapsing: a fixed slot tied to a household trigger (the page cannot send reminders); three a week is the floor, not the cap; no make-up work.

Planned time ramp (not built into the page; `mins` is set per session by the author):

| Stage | k7 | k4 |
|---|---|---|
| Weeks 1–4 | 3 × 15 min | 3 × 10 min |
| Months 2–5 | 3 × 20 min | 3 × 15 min |
| Month 6 on | 2 × 30 min plus one 45–60 min project block | 2 × 20 min plus one 30 min project block |

Session length moves up a stage only after four weeks at three sessions a week.

## How progress and testing work

| Layer | When | What | Graded by |
|---|---|---|---|
| Exit check | End of every session | 1–3 items. Wrong answers can be retried; "first try" is recorded. | The page. Written (`txt`) answers are saved for a parent; the hosted copy also checks them against the item's `rubric`. |
| Warm-up / quick review | Start of a session, or alone | Due items, one try. Right moves the item up a box; wrong sends it to tomorrow. | The page |
| Unit gate | End of each six-session unit, or early as a test-out | 10 questions, 9 to pass, 5–6 unseen. Second unit adds the signed-off project. | The page; a parent for the project |
| Phase gate | End of each phase | Khan Academy unit tests at 90%. Planned. Not in the page. | Khan Academy |
| Outside checks | About twice a year | School standardized test now; competitions and the AP exam later. | Other people |

What counts as progress, precisely:

- A session is done when its check is finished outside practice mode. Re-doing a done session from My path is practice and changes nothing.
- "This week" counts sessions whose first completion fell in the current Monday–Sunday week. A quick review counts toward days in a row but not toward the weekly goal.
- A unit is passed when the quiz best score reaches the bar and, if it has a product, the product is signed.
- The Today screen shows the first unpassed unit's first undone session, or its gate, or "You finished everything that is written so far".
- Tryout mode ("Grown-ups: try the lessons") never changes any of this.

Parent view shows per kid: sessions this week, sessions in the last 4 weeks, weeks in a row on target, share of exit-check items right on the first try, review accuracy, sessions done (and skipped by test-out), sessions the kid says they did alone, how each felt, gate status, and the latest written answers.

Limits to be honest about: the page cannot see paper or a CODAP window, so the sign-off is the real check on projects. A gate is a ten-question quiz. Passing shows recall and some transfer, not mastery.

## Failure modes and counters

| Failure mode | Signal | Counter |
|---|---|---|
| Novelty decay in week 2 or 3 (the likeliest) | Fewer than 3 sessions in a week | Short sessions, weekly streak, own data, quick reviews on busy days. Apply the week-4 rule; do not nag. |
| No trigger | Sessions only happen when prompted | A repeating reminder on the kid's device tied to a fixed slot. The page cannot remind. |
| Content runway | A kid is within three sessions of the end | Write unit 1C. At a session a day the written content lasts about two weeks. |
| Clicking through | Sessions finished in two minutes (`done[sid].mins`); thin written answers | Read one written answer a week; projects need a sign-off; gates include unseen items. |
| Unpiloted content | A kid says a step makes no sense | Fix it the same day and add the case to the content rules in `AUTHORING.md`. CODAP steps were written from memory of the tool. |
| Screen as a barrier (younger kid) | Avoids starting | Mission cards; "I did it from my card". |
| Interrupted session | Kid has to stop halfway | "Stop for now" keeps the place on that device; Today offers "Keep going" and "Start this session over". |
| Lost or split progress | The status line under the header turns amber | Local copy keeps working and retries. See `OPERATIONS.md`. The notebook is the backup record; Parent view has "Copy all progress as text". |
| Generous grading of written answers | Hosted coach passes a weak answer | A parent reads them. Gates count only items the page grades itself. |
| Math outruns school (k4) | The mean arrives before division | Hold the phase that needs it; add projects to the one before. |
| Overreach on the long arc (k7) | First-try rate falls; gates take many tries | Move the date, keep the standard. |
| Parent-driven, not kid-driven | Dread, negotiating to skip | Kids pick what to count and ask; they vote at week 4; stopping is allowed. |
| One maintainer | Two weekly checks missed | It pauses at the end of the written sessions. Nothing breaks. |
| Account exposure | A kid's device signed in to a parent's Claude account | Kids use the public page. The hosted copy is for a supervised computer only. |

## Independent review of the first draft (9 November 2026)

A second AI system (OpenAI's Codex) read every session, question, answer key and the save logic cold, and said it would not run the draft with its own kids. It checked every numeric answer key by hand and found none wrong.

| Finding | Resolution |
|---|---|
| First sessions asked for reading and writing before the kid made anything | Changed. Session 1 of each track is predict, test, see a graph of your own data. |
| Time understated (k7 sessions summed to 210 minutes against 180 advertised) | Changed. Sessions now sum to 179 (`k7`) and 118 (`k4`) minutes; weekly figures include warm-ups and gates. |
| Gates reused lesson questions, so 90% proved little | Changed. Each gate has 5–6 unseen `extra` items. Still a quiz; the signed project is the better evidence. |
| A limit of two gate tries a day could lock a kid out | Removed. Retakes are unlimited. |
| A daily streak punishes a three-a-week plan | Partly changed. Weeks on target is the main streak; days in a row shows only when it exists. |
| k7's own data started at session 6, and the analysis session could stall on an unfinished log | Changed. Own data is `s01`. The log starts at `s03` with three numbers a day. Reaction times are the fallback dataset in `s11` (`show`). |
| k4's range lesson used category counts; the last session made the kid redraw and retype | Changed. `m11` measures five objects. `m12` reuses the graph and allows dictation to a parent. |
| Topic picks were collected and never used | Removed from content. The `pick` item type and `interests` field remain in code, unused. |
| Some checks accepted claims that might not match the graph | Partly changed. Wording is tighter. The page still cannot see a notebook or CODAP. |
| Save and merge bugs: lost counts, one device overwriting another, stalled saves, a false "saved" status | Fixed. `push()` reads and merges before writing; merge and erase are tested in `walk.py` and `test_gh.py`. |
| Cut the coach, AI grading and long roadmap from the pitch | Partly. The public page has no AI. The roadmap is kept, marked as aspiration (`PURPOSE.md`, `CURRICULUM.md`). |
| Send k7 to a curated graph, not the newest newspaper one | That session is out of the trial. The `NYT_GRAPH` constant is left in the code, unused. |
