# Operations

## What runs where

| Thing | Where | Who can change it |
|---|---|---|
| The page | This public repo, branch `main`, file `index.html`, served by GitHub Pages at <https://sthaker.github.io/datalab/> | Anyone with push access to this repo |
| Progress and names | The private repo `sthaker/datalab-progress`, folder `state/` | The page, through a token held on each device; the owner, by hand |
| Hosted copy with coach and written-answer grading | A private Claude artifact titled "Data Lab Mission Control" in the owner's Claude account | The owner, or an agent running in the owner's account with artifact tools |
| Parent guide (rationale, private details) | A private Claude doc in the owner's account | The owner. It names the family; nothing from it may be copied here verbatim. |

There is no server, no build, no CI, and no secrets in this repo.

## Deploy the page

This is the one ship procedure. `CLAUDE.md` carries only a summary of it.

1. Edit `index.html`. Update the docs the change touches in the same commit. For new content, work through the pre-ship checklist in `AUTHORING.md`, including its list of places that repeat content counts.
2. Run every test in `TESTING.md` and read the output against "Clean means"; exit codes alone are not enough. Read the screenshots.
3. Privacy check (see "Privacy operations" below): the grep over the working tree, and `test_gh.py` run with `DATALAB_FORBID` set. You do not know the pattern; ask the owner for it or have the owner run both. An unset `DATALAB_FORBID` means the check did not run.
4. Commit `index.html` (and tests and docs) and push to `main`, **only when the owner has asked for that**.
5. GitHub Pages rebuilds in about a minute. There is no workflow file; Pages is set to deploy from the branch root.
6. Verify the live bytes against what was pushed, not against the working tree:

   ```sh
   git status --short                     # must print nothing
   git show HEAD:index.html | sha256sum
   curl -s "https://sthaker.github.io/datalab/index.html?v=$(date +%s)" | sha256sum
   ```

   The two hashes must match. Hashing the committed file means an uncommitted edit cannot pass or fail the check by accident. Pages caches for about ten minutes; the query string avoids a stale copy. If they still differ after five minutes, check the Pages build under the repo's Actions tab.
7. Republish the hosted Claude artifact from the same file and verify it (next section).
8. Update "Verified / not verified" in `CLAUDE.md`.
9. Devices pick up the new page on their next reload. A page left open keeps running the old code until then.

If you cannot push, cannot reach the artifact, or cannot run a browser, do not work around it; see "Limits an agent may hit" below.

Only `index.html` is deployed in any meaningful sense: the docs and tests ride along in the repo, and the artifact gets `index.html` alone. There is no version number and no changelog; the commit history and `docs/DECISIONS.md` are the record.

Rollback: `git revert` the commit and push, then repeat steps 5 to 7 so both copies match again. Progress data is forward-compatible as long as stored ids were not renamed (see `AUTHORING.md`).

## The hosted Claude artifact copy

The artifact is the same `index.html`, byte for byte. Inside Claude, `window.claude.use` exists, so the page stores progress in the artifact's database and turns on the coach, written-answer grading and the Claude voice. The artifact's database is separate from the GitHub progress repo; the two do not sync with each other. The family uses the public page; the hosted copy is for a supervised computer only, because the device is signed in to the owner's account.

Rule: **both copies stay identical.** After every push to `main`, publish a new version of the artifact from the same file. Never edit the artifact directly.

With artifact tools available in the owner's account: find the artifact by title, read its current version id, and publish `index.html` as a new version on that base. Then read the artifact back and compare the SHA-256 of what it returns with `git show HEAD:index.html | sha256sum`; they must match. If the read-back differs only because the tool wraps or re-serialises the document, say so and report it as not verified. Without artifact access, tell the owner: "Republish the Data Lab Mission Control artifact from `index.html` at commit `<hash>`", give the SHA-256 of the file, and record the hosted copy as behind.

## The progress repo

Files, all written by the page:

| File | Content |
|---|---|
| `state/k7.json`, `state/k4.json` | One kid doc each (shape in `ARCHITECTURE.md`) |
| `state/parent.json` | Parent code and the kids' display names |
| `state/device-check.json` | `{t}` written by the Connect write test |

Every save is one commit, so the repo history is a full audit trail and a backup. The repo must stay private; the page refuses to connect to a public one.

### One-time setup (owner)

1. Create a private repo for progress. It can be empty.
2. Create a fine-grained personal access token: repository access "Only select repositories" → the progress repo; permission **Contents: Read and write**. Nothing else. Set an expiry and note the date.
3. Never put the token in this repo, in a doc, or in a chat with an agent.

### Connect a device (parent, on each phone, iPad or computer)

1. Open the live page. Tap **Parent**.
2. On a device that has never been set up, the sync card ("Already set up on another device?") sits under the code box. Connect **before** choosing a code so the family's existing code and names come across. On a device that already has a code, enter it and scroll to "Sync across devices".
3. Enter the repo as `owner/name`, paste the token, tap **Connect**.
4. The page checks the token, that the repo is private, and that it can write. On success the status line under the header reads "Progress is saved to your private GitHub repo and follows you to other devices", and Parent view relocks with the family's code.
5. Optional: add the page to the home screen. `…/datalab/#k4` and `…/datalab/#k7` open straight to a kid.

Connect error messages and their meaning:

| Message | Cause |
|---|---|
| "Enter the repo as owner/name, and paste the whole token." | Format check failed. |
| "GitHub did not accept that token." | Wrong, expired or revoked token (401). |
| "That repo was not found, or the token cannot see it." | Typo, or the token is not scoped to that repo. |
| "That repo is public. Use a private repo for progress." | Make it private. |
| "The token can read that repo but cannot write to it…" | Token lacks Contents: Read and write. |
| "GitHub could not be reached…" | Network. |

The token and repo name are stored in that device's `localStorage` only (`datalab:gh`). "Disconnect this device" in Parent view removes them and leaves local progress in place.

### Add a device later

Same as Connect. Progress already on the new device merges with the repo; nothing is lost on either side. A device that set its own parent code before connecting adopts the family's code.

## When the status line shows a warning

The line under the header turns amber when something is wrong. Progress is always written to the device first, so a kid can keep working.

| Status text | Meaning | What to do |
|---|---|---|
| "…saved on this device only. GitHub is not reachable right now. It will catch up next time." | A read or write failed. The page retries every 60 s, when the network returns, and when the page is reopened. | Usually nothing. If it lasts a day, open Parent view on that device, Disconnect and Connect again, and check <https://www.githubstatus.com/>. |
| "…The GitHub token stopped working. A parent can fix it in Parent view." | 401. The token expired or was revoked. Retries stop. | Create a new token with the same scope. On every device: Parent → Disconnect this device → Connect with the new token. Local progress merges up. |
| "Progress is saved on this device. It does not follow you to other devices." (not amber) | No backend configured on this device. | Connect it. |
| "…Account storage is not reachable right now." | Hosted copy only: the artifact database failed. | Reload. If it persists, use the public page. |
| "Progress cannot be saved in this view. Use your notebook as the record and tell a parent." | `localStorage` is blocked (private browsing, storage disabled). | Open the page in a normal browser window. |

For a sync bug that is not one of these, see "Debugging sync" below.

## Erase or reset progress

| Goal | How |
|---|---|
| Erase one kid's progress everywhere | Parent view → "Erase …'s progress" → "Yes, erase". This bumps the doc's `epoch`; every device drops that kid's progress on its next sync. Cannot be undone from the page. |
| Clear what a parent did while trying the lessons | Use "Grown-ups: try the lessons" instead; it saves nothing. If real sessions were done as a test, Erase that kid. |
| Undo an erase | Restore the kid's file from the progress repo's history (the commit before the erase), then **raise `epoch` above the current value** in the restored JSON and commit. Without the higher epoch, devices keep the erased state. |
| Correct one record by hand | Edit `state/<kid>.json` in the progress repo, raise `epoch` by one, set `ts` to now in milliseconds, commit. Devices adopt it whole on next sync. Any progress made on a device and not yet synced is lost, so check the status line on each device first. |
| Change or recover the parent code | It is in `state/parent.json` as `code`, in plain text. To change it, edit that value, set `ts` to now in milliseconds, and commit. Devices take the code from the copy with the later `ts`. |
| Change the names | Parent view → Names → Save names. |
| Wipe one device only | Parent → Disconnect this device, then clear the site's data in the browser settings. Nothing remote changes. |
| Wipe everything and start clean | Erase each kid from Parent view (preferred). Deleting files in the progress repo alone does not work: any device that still has a local copy pushes it back. |
| Drop a stuck unfinished session | Today → "Start this session over", or clear `datalab:wip:<kid>` in the device's storage. |

## Debugging sync

### "Done on one device, missing on the other"

Work down the list; most reports end at step 2.

1. **Read the status line under the header on both devices** (`renderSync()` writes it). "saved to your private GitHub repo and follows you" means that device's last read or write worked. "saved on this device only. GitHub is not reachable right now" means a read or write failed and the device may hold progress it has not pushed, or lack progress it has not pulled. "The GitHub token stopped working" means retries have stopped until a new token is connected. "saved on this device. It does not follow you" means that device was never connected. "saved to this account" means it is the hosted Claude copy. Full table: "When the status line shows a warning" above.
2. **Rule out the things that are not bugs.**
   - The session was not finished. Only "Finish session" (`finishSession()`) marks it done. A stopped session is work in progress kept on that device alone (`datalab:wip:<kid>`) and never syncs.
   - It was done in "Grown-ups: try the lessons" or as practice. Neither saves anything.
   - One device is on the hosted Claude copy. Its store is the artifact database, separate from the GitHub repo.
   - The devices are connected to different repos. Compare the repo name shown in Parent view under "Sync across devices" on each.
   - The other device has not pulled yet. `Store.pull` runs at page load, when the tab becomes visible again, on Connect, and when a kid card is tapped on Home. It does not run while a page sits open on a kid's screen. Reload the page.
3. **Look at the progress repo**: `state/<kid>.json` and its commit history. If the session id is missing from `done` and there is no commit from about the time it was finished, the first device did not push: a push fault (status line, token, network on that device). If it is in the file and the second device still lacks it after a reload, it is a pull or merge fault on the second device.
4. **Check `epoch`.** When two copies differ in `epoch`, the higher one wins whole and the other's progress is dropped (`Store.merge`). An Erase on any device, or a hand edit that raised `epoch`, explains progress that vanished everywhere. Compare `epoch` in the repo file with each device's copy.
5. **Inspect a device.** Without a console: Parent view → "Copy all progress as text" gives both kids' docs as JSON, to paste somewhere readable (treat it as private: it holds the kids' written answers). With one: the values in step 2 of the next list. On an iPhone or iPad that needs Safari's Web Inspector from a Mac (on the device: Settings → Safari → Advanced → Web Inspector; on the Mac: Safari → Develop → the device).
6. **Reproduce with the `Mock` class in `tests/test_gh.py`**, never against the real repo.

### For any sync bug

1. Reproduce with `tests/test_gh.py`. It drives two or more browser contexts against a mock of the contents API (`Mock` class) and already covers bad token, wrong repo, public repo, read-only token, two devices, a write conflict, a late-connecting device, erase, offline and back, a revoked token, and disconnect. Add the failing sequence there first.
2. On a real device, open the browser console on the live page: `Store.kind`, `Store.mode`, `Store.err`, `Object.keys(Store.fail)`, `Store.get("k4")`. Then compare with the file in the progress repo and its commit history.
3. Read `Store.merge`, `Store.push` and `Store.pull` together with the merge table in `ARCHITECTURE.md`. Most sync bugs are merge rules (a field that should union or take the max) or a missing `Store.save` after a mutation.
4. Any new field in a doc needs a merge rule. A field `merge` does not know about is dropped, because `merge` builds its result from `blank()`.
5. Never test against the real progress repo. Use the mock, or a throwaway private repo of your own.

## Limits an agent may hit, and what to hand over

| Limit | What to do instead |
|---|---|
| Cannot push to `main` (no credentials, or push blocked by the environment) | Leave the work committed locally only if asked to commit; otherwise leave the working tree. Hand the owner the changed file list, the test output, and the exact commands: `git add …`, `git commit`, `git push origin main`, then the hash check in "Deploy the page". |
| Cannot create a repository or a token | Never try to work around it. Give the owner the setup steps in "One-time setup". |
| No access to the owner's Claude artifacts | State that the hosted copy is now behind, with the commit hash and file SHA-256 to republish from. |
| No access to the progress repo | Expected. An agent should not need it. To tune the next unit, ask the owner to paste "Copy all progress as text" from Parent view, and remind them it contains the kids' names. |
| Cannot fetch the live URL (network policy) | Give the owner the two hash commands. |
| WebKit or Chrome missing for the tests | `python3 -m playwright install webkit chromium`, or set `CHROME`. If a browser cannot be installed, say which tests did not run. Do not report them as passed. |
| Cannot test on a real phone, hear audio, or drag in CODAP | List these as not verified in `CLAUDE.md`. They need the owner. |

## Privacy operations

- Before every commit: `grep -rniE "<family names and places>" . --exclude-dir=.git`, which must print nothing. The pattern is not in this repo and a new developer cannot guess it: ask the owner for it, or have the owner run the command.
- Then run `DATALAB_FORBID='<the same pattern>' python3 tests/test_gh.py`. It fails if `index.html` matches. The match is case-sensitive unless the pattern starts with `(?i)`, and it reads `index.html` only, so it does not replace the grep. If `DATALAB_FORBID` is unset the check did **not** run: `PASS source has no forbidden names` prints vacuously.
- The GitHub account name appears in the Pages URL and the repo names. That is unavoidable and accepted.
- Test names in `tests/` are placeholders. Do not replace them with real ones.
- Screenshots from tests (`tests/*.png`, `tests/phone_shots/`, `tests/out/`) are git-ignored. Keep them that way; a screenshot of a real device could show names.
