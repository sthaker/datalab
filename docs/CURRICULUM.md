# Curriculum

Two independent tracks. Each is five phases. Only Phase 1, units 1A and 1B, is written (12 sessions per track). Unit 1C is outlined. Everything after that is a plan.

Status words used here:

- **Written**: session objects exist in `TRACKS` in `index.html` and are walked by the tests.
- **Outlined**: a `planned:true` unit in `TRACKS` with a `list` of six session topics. Shown on My path as "Coming up".
- **Planned**: a phase with `units:[]`. Shown on My path as "Written closer to the time".
- **Aspiration**: a target date or outside result. Not a commitment. Marked (A).

The concept map is UCLA's Introduction to Data Science (IDS). Its labs are not used because they are in R. Each phase leans on an existing free course so that later units do not have to be invented.

## Track k7 (7th grader)

| Phase | Status | What is learned | Main material | Gate | Pointed at (A) |
|---|---|---|---|---|---|
| 1. See | 1A, 1B written; 1C outlined | Reading graphs, kinds of data, statistical questions, comparing groups, shape, center, spread, outliers, scatter plots, a week of own data | CODAP (Mammals example), in-page figures | Page gates at 9 of 10; a one-page data story; Khan Academy grade 6 and 7 statistics unit tests at 90% | Nov 2026 – Jan 2027 |
| 2. Code | Planned | Python, tables, plotting. Rebuild the Phase 1 project in code. | Kaggle Learn: Intro to Programming, Python, Pandas, Data Visualization | Every exercise complete; the rebuilt project runs top to bottom | Feb – Jun 2027 |
| 3. Infer | Planned | Randomness, sampling, simulation, tests by shuffling, bootstrap intervals, experiments, confounding | Berkeley Data 8 textbook (excerpted); Khan AP Statistics units on study design and probability | Own experiment or survey; page gate | Jul 2027 – Mar 2028 |
| 4. Predict | Planned | Correlation, regression, residuals, cross-validation, trees, clustering | Data 8 prediction chapters; Kaggle Learn Intro to Machine Learning | One Kaggle submission; ASA project competition entry | Apr – Sep 2028 |
| 5. Prove it | Planned | Formula-based inference: sampling distributions, intervals, significance tests, chi-square | Khan Academy AP Statistics; released AP free-response questions | Two timed practice exams at 4 or better; the AP exam | Oct 2028 – May 2029 |

Notes: IDS Unit 1 maps to Phase 1, Units 2–3 to Phase 3, Unit 4 to Phase 4. Python was chosen over R (see `DECISIONS.md`). The Data 8 textbook is written for college freshmen; the reading load is the least certain part of this track. Stretch (A): if the Phase 3 gate is passed by December 2027, Phases 4 and 5 overlap and the exam moves to May 2028.

### k7 Unit 1A: Reading data (`s1a`, written)

| Id | Title | Min | The one idea | The kid produces | Check items |
|---|---|---|---|---|---|
| `s01` | Which hand is faster? | 12 | Predict, measure, look at the dots | 16 reaction times and a two-row dot plot (any device) | `react`, `mc`, `txt` |
| `s02` | Meet CODAP | 15 | One dot is one case (one row) | A CODAP graph of Sleep; finds the longest sleeper | `mc`, `txt` |
| `s03` | Start your own data | 10 | Predict before you collect | A notebook table (Day, Sleep, Screens, Moving) and three predictions; then one row a day for 7 days | `txt`, `mc` |
| `s04` | Two kinds of data | 12 | Categorical vs numeric: would an average make sense? | Four columns marked C or N | `mc` ×3 |
| `s05` | Questions data can answer | 15 | A statistical question is about a group whose answers vary | Two questions about the mammals and a graph answering one | `mc` ×2, `txt` |
| `s06` | Compare groups | 15 | Compare where most of the dots sit, not single dots | Sleep split by Diet; a claim with evidence | `mc`, `mc` + `dots2` fig, `txt` |

Gate 1A (`g-s1a`): 10 questions, 6 unseen `extra` items (`mc`, one with a `dots2` figure) plus 4 drawn from the 10 auto-graded session items. No product.

### k7 Unit 1B: Describing a distribution (`s1b`, written)

| Id | Title | Min | The one idea | The kid produces | Check items |
|---|---|---|---|---|---|
| `s07` | Shape | 15 | Symmetric, skewed right, skewed left, or no clear shape | Shape of Mass and one more column, in the notebook | `mc` + `dot` fig ×2, `mc` |
| `s08` | Center: median and mean | 15 | Median is the middle; mean is total ÷ count; they can disagree | Hand calculation; mean and median shown in CODAP | `num` ×2, `mc` |
| `s09` | Spread: range and IQR | 15 | Range uses the ends; IQR is the width of the middle half | Hand Q1, Q3, IQR; a CODAP box plot | `num` ×2, `mc` |
| `s10` | Outliers and which summary to trust | 15 | Mean and range get pulled by outliers; median and IQR mostly do not | One outlier found and judged (mistake, real, cannot tell) | `mc` ×2, `txt` |
| `s11` | Your data, analyzed | 20 | Compare the median with your prediction; data describes only what it measured | Own data typed into CODAP, dot plots with medians, a screenshot | `txt`, `mc` |
| `s12` | Write your data story | 20 | Question, collection, graph, finding, limit | A five-sentence story pasted in (`min:160` characters) | `txt` |

Gate 1B (`g-s1b`): 10 questions, 6 unseen (`num` ×3, `mc` ×3, one with a `dot` figure) plus 4 from the 12 auto-graded session items. Product: "One-page data story about your own data", five rubric lines, parent sign-off.

Dependencies inside the unit: `s11` needs the 7-day log from `s03` (at least 5 days) or falls back to the `s01` reaction times, which the page lists through `show:{from:"s01.a", kind:"react"}`. `s12` needs the screenshot from `s11`. A kid who tests out of 1A never collects either; see the backlog in `CLAUDE.md`. Today shows a "Time log" reminder from `s03` done until `s11` done.

### k7 Unit 1C: Relationships (`s1c`, outlined)

| # | Topic (from `TRACKS`) | Suggested idea and product |
|---|---|---|
| 1 | Scatter plots: two numbers for every dot | Read one point as a pair. Product: a CODAP scatter plot of Mass vs LifeSpan. |
| 2 | Strong, weak, or no pattern | Describe direction and strength in words. |
| 3 | Lines that fit, and what the slope means | Slope as "for each one more of x, about this much more y". Uses the algebra the kid already has. |
| 4 | Correlation is not causation | Name a third variable for a made-up association. |
| 5 | Choose a dataset you care about | First use of the kid's own interests. Product: a chosen dataset and one question. |
| 6 | Mini-project: one question, one graph, one claim | Product, parent-signed. |

Ends with Gate 1C and then the Phase 1 gate (planned, not in the page): Khan Academy grade 6 and grade 7 statistics unit tests at 90%. The page has no scatter-plot figure kind yet; unit 1C needs one (see `AUTHORING.md`, "Adding a figure kind").

## Track k4 (4th grader)

| Phase | Status | What is learned | Main material | Gate | Pointed at (A) |
|---|---|---|---|---|---|
| 1. Notice | 1A, 1B written; 1C outlined | Bar graphs, picture graphs, dot plots, tallying, asking a question data can answer, middle, most, range | In-page mystery graphs; a paper notebook; real objects | Page gates at 9 of 10; a hand-drawn graph with three sentences; Khan Academy grade 3 "represent and interpret data" unit test at 90% | Nov 2026 – Jan 2027 |
| 2. Collect | Planned | Small surveys and counts, coins and dice, fair and unfair samples, graphs that mislead | Paper, index cards for a weekly data postcard, dice | Three data postcards; page gate | Feb – Jun 2027 |
| 3. Explore | Planned | CODAP on a computer: tables, sorting, bar charts, dot plots, comparing groups | CODAP; Bootstrap Data Literacy lessons 2–10 | ASA poster competition entry | Jul 2027 – Feb 2028 |
| 4. Measure | Planned | Histograms and shape, the mean, box plots, spread | Bootstrap lessons 11–16; Khan grade 6 data and statistics | Khan unit test at 90% | Mar – Dec 2028 |
| 5. Relate | Planned | Scatter plots, association, sampling, probability, first lines of code | Bootstrap lessons 18–20; Khan grade 7 and 8 statistics; Kaggle Learn Intro to Programming | Khan unit tests at 90%; second poster entry | Jan – Jun 2029 |

Two rules specific to this track:

- **Reading load.** Every step is one or two short sentences. The page restates any outside material; the kid never reads a teacher's lesson plan. A "Read it to me" button appears where the browser can speak.
- **Math coupling.** The track never needs math more than a small step past school. The mean needs division and percent needs fractions, so Phase 4 is timed for late 5th grade. If school math runs slower, Phase 4 waits and Phase 3 gets more projects.

### k4 Unit 1A: Graph detective (`m1a`, written)

| Id | Title | Min | The one idea | The kid produces | Check items |
|---|---|---|---|---|---|
| `m01` | Guess, then count | 10 | Guess first; a taller bar means more | 12 small things sorted by color; the page draws the bar graph | `tally` (predict), `mc` |
| `m02` | Mystery graph | 8 | A graph can be read like a puzzle | Spoken guesses as a bar graph of days per month is revealed in three stages | `mc` + fig ×2, `num` + fig |
| `m03` | Tally time | 10 | Tally marks in bundles of five | A notebook tally of something at home | `tally`, `num` |
| `m04` | Picture graph | 10 | A key says what each picture stands for | A picture graph of the tally, with a key | `num` ×2, `mc` |
| `m05` | Bar graph by hand | 10 | Title, names, number line from 0 | A hand-drawn bar graph of the tally | `mc` + fig, `num` + fig, `mc` |
| `m06` | Questions data can answer | 10 | Some questions need counting or asking | Two questions written in the notebook | `mc`, `mc` + fig, `txt` (`min:12`) |

Gate 1A (`g-m1a`): 10 questions, 5 unseen (`num` ×3, `mc` ×2, two with a bar figure) plus 5 from the 13 auto-graded session items. No product.

### k4 Unit 1B: My data (`m1b`, written)

| Id | Title | Min | The one idea | The kid produces | Check items |
|---|---|---|---|---|---|
| `m07` | Ask and collect | 10 | Ask, collect, draw, tell | A question and a fresh tally (5 people or 12 things) | `tally`, `mc` |
| `m08` | Draw your graph | 10 | Check your graph against the page's | A hand-drawn bar graph compared with the page's graph of the `m07` counts (`show`) | `mc` + fig, `num` + fig |
| `m09` | Dot plots | 8 | One dot is one thing; same values stack | Reads a dot plot of days per month | `num` + fig ×2, `mc` + fig |
| `m10` | Middle and most | 10 | Median by removing the ends; mode is the most common | Five paper scraps ordered; the middle found | `num` ×3 |
| `m11` | Measure and range | 10 | Range = biggest − smallest | Five objects measured to the nearest inch | `num` ×2, `mc` |
| `m12` | Tell the story | 12 | I asked… I found… I wonder… | Three sentences typed or dictated (`min:40`) | `txt` |

Gate 1B (`g-m1b`): 10 questions, 6 unseen (`num` ×5, `mc` ×1, two with a dot figure) plus 4 from the 12 auto-graded session items. Product: "Bar graph with three sentences", five rubric lines, parent sign-off.

Dependencies: `m04` and `m05` use the notebook tally from `m03`. `m08` and `m12` show the page's graph of the `m07` counts. `m07` offers "use one you wrote last time" (from `m06`) with a self-contained fallback: watch a pet, or a person, for ten minutes.

### k4 Unit 1C: Fair or not? (`m1c`, outlined)

| # | Topic (from `TRACKS`) | Suggested idea and product |
|---|---|---|
| 1 | Coin flips: predict, then flip 20 times | Chance does not come out the same every time. Product: a heads/tails tally. A complete draft of this session is the worked example in `AUTHORING.md`. |
| 2 | Roll a die 30 times and make a dot plot | Each face comes up about, not exactly, as often. Product: a hand-drawn dot plot. |
| 3 | A handful tells you about the bag | A sample hints at the whole. Product: guess the bag from a handful, then count the bag. |
| 4 | Graphs that trick you | A number line that does not start at 0; pictures of different sizes. Builds on `m05.c`. |
| 5 | Ask eight people two questions | A two-question survey. Product: two tallies. |
| 6 | Make your first poster | Product, parent-signed: question, graph, three sentences. |

Ends with Gate 1C and then the Phase 1 gate (planned, not in the page): Khan Academy grade 3 unit test on representing data at 90%.

## Gates and outside checks, in one place

| Check | Exists in the page? | Pass mark |
|---|---|---|
| Exit check per session | Yes | Finish every item; retries allowed |
| Unit gate quiz | Yes | 9 of 10, one try per question, unlimited retakes |
| Unit product sign-off (second unit of each pair so far) | Yes | Parent ticks all five rubric lines |
| Phase gate: Khan Academy unit tests | No. Needs child accounts set up by a parent. | 90% |
| School standardized math test | No | Trend only. The lower-grade form reports measurement and data together, so it is a weak signal for `k4` until 6th grade. |
| ASA poster and project competitions (A) | No | Entry submitted |
| AP Statistics exam (A) | No | 4 or 5 |

## The four-week calendar at three sessions a week

| Week | k4 | k7 |
|---|---|---|
| 1 | `m01` `m02` `m03` | `s01` `s02` `s03` |
| 2 | `m04` `m05` `m06`, Gate 1A | `s04` `s05` `s06`, Gate 1A |
| 3 | `m07` `m08` `m09` | `s07` `s08` `s09` |
| 4 | `m10` `m11` `m12`, Gate 1B | `s10` `s11` `s12`, Gate 1B |

Session minutes sum to 118 (`k4`) and 179 (`k7`). Warm-ups add about 2 minutes a session and each gate about 10. Phase 1 is 18 sessions; at 3 a week it takes 6 weeks, at 7 a week under 3.

## When to write the next unit

Write 1C when a kid is within three sessions of the end of 1B, or at the week-4 decision if it is "continue". Before writing, read that kid's results (Parent view, or the kid's JSON in the progress repo): first-try rate, which items were missed in gates (`gates[gid].quiz.missed`), `feel` and `solo` reports, and the written answers. Slow down if first-try is under 70%. Then follow `AUTHORING.md`.
