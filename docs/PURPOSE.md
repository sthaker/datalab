# Purpose

## The gap this fills

Reading a graph and judging whether a claim holds up is a basic literacy. Standard school math gives it little room.

- The usual sequence is built to reach calculus: arithmetic, algebra, geometry, more algebra, precalculus. Data and statistics get the time left over.
- In the Common Core, grades K–5 have a "Measurement and Data" domain. The "Statistics and Probability" domain starts in grade 6. When the standards were drafted, the American Statistical Association's review said data analysis, probability and statistics had only a limited role in K–5 and argued they should extend into those grades: <https://magazine.amstat.org/blog/2010/05/13/commoncore5_10/2/>.
- The outcome is measurable. A 2023 analysis of NAEP results found that scores in data analysis, statistics and probability fell between 2019 and 2022 in both grade 4 and grade 8, with the larger drop in grade 8, and that fewer grade 4 teachers reported emphasising data analysis: <https://www.k12dive.com/news/data-literacy-test-scores-decline/642780/>.

The parents saw the same thing at home: very little data work in this year's schoolwork for the 4th grader, and science labs only for the 7th grader. That observation comes from school email, not from teachers.

Data Lab is a home curriculum that runs next to school. It is not a math-support program and not a replacement for anything.

## What success means

### First: adoption and sustainment (the four-week trial)

The first question is not "did they learn statistics". It is "do they come back, and can they finish inside the time budget without a parent sitting there". The trial is 12 sessions per kid, three a week, for four weeks. The decision is made with the kids at the end, by this rule:

| Result at week 4 | Decision |
|---|---|
| 9 or more of 12 sessions done, mostly without a parent alongside, and the kid wants to continue | Continue. Write the next unit (1C). |
| 6 to 8 sessions, or 9 or more only with a parent alongside | Change the time slot or shorten the sessions, then run two more weeks. |
| Fewer than 6, or the kid does not want to | Stop. No make-up work, no guilt. |

Inputs to the rule, all visible in Parent view:

- Sessions done (`done`), not counting units skipped by passing a gate early. A test-out is not a session.
- The kid's own answers after each session: "Did you do it by yourself?" and "How was it?".
- Sessions this week, last four weeks, and weeks in a row on target.

What the kids should be able to show at week 4 (targets, not results):

- Track `k4`: a hand-drawn bar graph answering a question the kid picked, with three sentences about it. Can read bar graphs, picture graphs and dot plots, and find the middle, the most common and the range.
- Track `k7`: a one-page data story about a week of the kid's own life, with real graphs. Can compare groups and say when a median is more honest than a mean.

### Long term: the arc (aspirations, not commitments)

Everything below assumes the trial works and session length grows as planned. No normed test of data science exists for these ages, so each target is defined by a check that someone else scores. Dates show where the plan points.

| Track | Target | Scored by | Pointed at |
|---|---|---|---|
| k7 | AP Statistics exam, score 4 or 5 | College Board | May 2029 (9th grade); stretch May 2028 |
| k7 | Python: load, clean, plot and model a dataset unaided; four projects | Kaggle Learn exercises; a parent against a rubric | Rolling |
| k7 | One entry in the ASA Statistics Project Competition | ASA judges | June 2028 or 2029 |
| k4 | Grade 6, 7 and 8 statistics and probability units at 90% | Khan Academy unit tests | June 2029 (end of 6th grade) |
| k4 | Two entries in the ASA Data Visualization Poster Competition | ASA judges | April 2028 and 2029 |
| Both | Rising statistics score on the school's standardized math test | The test publisher, through school | Each testing window |

The owner's shorthand for the long-term bar is "95th percentile competence". The AP target is the proxy for that. The reasoning in the parent guide (share of a graduating class that scores 4 or 5) is an inference from two numbers, one of them unchecked, so treat it as a direction and not a measured percentile. Whether `k7` can sit an AP exam through their school is also unverified.

Estimated effort for the full arc: about 250 focused hours for `k7` and 130 for `k4` over 30 months. These are planning numbers.

## Who uses it

| User | What they do | Device |
|---|---|---|
| The 7th grader (track `k7`, age 12 in `KIDS`) | Works alone. Session 1 on any device; from session 2 mostly CODAP on a computer with a mouse or trackpad. Keeps a paper notebook. Algebra is ahead of grade level, so slope and formulas are usable soon. | Phone for `s01`, computer after |
| The 4th grader (track `k4`, age 9 in `KIDS`) | Does each mission on paper or with real objects, from the screen or from a printed mission card. The screen is for the short check. Needs only counting, adding, subtracting and comparing. | Phone or iPad, plus paper |
| The parents | Set up once (about an hour), connect each device to sync, print mission cards, then spend about 10 minutes a week: look at the numbers, read one written answer per kid, sign off projects. One parent maintains it; the other is a deliberate skeptic whose objections shaped the trial. | Any |

## Constraints

- **On top of school.** Sessions are 8–12 minutes (`k4`) and 10–20 minutes (`k7`), three a week. With warm-ups and two gates that is about 40 and 55 minutes a week. If it crowds out anything that matters, it loses.
- **Little oversight.** The page must make the next step obvious and decide by itself what counts. Nothing may depend on a parent standing there or on a kid saying "I did it".
- **Phone, iPad and computer.** A 390 px wide phone is the baseline for every screen. CODAP sessions need a computer; the page says so.
- **No accounts for kids.** Kids cannot have Claude or GitHub accounts. The page is a public static file. Progress syncs through a private repo the parent owns, with a token stored only on the device.
- **Public page, private data.** No names, school or location in this repo. See the privacy rule in `CLAUDE.md`.
- **One maintainer.** If the weekly check lapses, a kid reaches the end of the written sessions and the page says so. Nothing breaks.
- **Content is unpiloted.** The sessions were written in two days and reviewed by a second AI system and automated tests, not by a teacher. The first weeks with the kids are the pilot.
