"""Try-the-lessons mode and stop / keep going / start over.
Chromium at phone width against the mock GitHub API from test_gh.py, then one WebKit iPhone 13 pass with real taps.
Screenshots go to tests/out/modes_*.png. Read them; do not trust the numbers alone."""
import os, re, json, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = os.environ.get('U', 'file://' + os.path.abspath(os.path.join(HERE, '..', 'index.html')))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
SOLVE = re.search(r"SOLVE = r'''\n(.*?)\n'''", open(os.path.join(HERE, 'walk.py')).read(), re.S).group(1)
# reuse the mock GitHub API from test_gh.py without running that script
_gh = open(os.path.join(HERE, 'test_gh.py')).read()
_ns = {}
exec("import json, re, base64, hashlib\n" + re.search(r"^GOOD=.*?(?=^mock=Mock\(\))", _gh, re.S | re.M).group(0), _ns)
Mock, GOOD = _ns['Mock'], _ns['GOOD']

res = []; errs = []
def ok(name, cond, extra=''):
    res.append((name, bool(cond), extra)); print(('PASS ' if cond else 'FAIL ') + name, extra if not cond else '')

AUDIT = r'''() => {
  const out = {stray:[], small:[], overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth, past:[]};
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for(let n; (n = tw.nextNode()); ){ const p = n.parentElement; if(!p || /^(SCRIPT|STYLE)$/.test(p.tagName)) continue; const t = n.nodeValue; if(/\b(null|undefined|NaN)\b/.test(t) || t.includes("[object")) out.stray.push(t.trim().slice(0,60)); }
  for(const e of document.querySelectorAll("input,textarea")) if(/^(null|undefined|NaN)$/.test(String(e.value).trim())) out.stray.push("value="+e.value);
  const VW = document.documentElement.clientWidth;
  for(const b of document.querySelectorAll("#app button, #nav button")){ const r = b.getBoundingClientRect(); if(r.width<=0 || r.height<=0) continue;
    if(Math.round(r.height) < 40) out.small.push((b.textContent||"").trim().slice(0,40)+" "+Math.round(r.width)+"x"+Math.round(r.height));
    if(r.right > VW+1 || r.left < -1) out.past.push((b.textContent||"").trim().slice(0,40)); }
  return out; }'''
LS = "JSON.stringify(Object.keys(localStorage).sort().map(k=>[k, localStorage.getItem(k)]))"
SNAP = "JSON.stringify([JSON.stringify(Store.get('k7')), JSON.stringify(Store.get('k4')), JSON.stringify(Store.get('parent')), " + LS + "])"
WIPJ = "k=>JSON.parse(localStorage.getItem('datalab:wip:'+k)||'null')"

def audit(pg, screen):
    a = pg.evaluate(AUDIT)
    ok('clean screen: ' + screen, not a['stray'] and a['overflow'] <= 0 and not a['small'] and not a['past'], json.dumps(a))

def shot(pg, name): pg.screenshot(path=os.path.join(OUT, 'modes_' + name + '.png'), full_page=True)
def btn(pg, text): return pg.locator('#app button').filter(has_text=re.compile('^' + re.escape(text) + '$')).first
def stage(pg): return pg.evaluate("VIEW.stage||''")
def age_reviews(pg, kid): pg.evaluate("k=>{const st=Store.get(k); for(const r of Object.values(st.rev)) r.due='2020-01-01'; Store.setLocal(k, st);}", kid)

def start_real(pg, kid, act):
    """From anywhere: open the kid's Today card and start (or keep going). Clears a warm-up if one shows."""
    pg.evaluate("k=>go({name:'kid',kid:k})", kid); pg.wait_for_timeout(60)
    act(btn(pg, 'Keep going') if btn(pg, 'Keep going').count() else pg.locator('#app button.primary').first); pg.wait_for_timeout(60)
    if stage(pg) == 'warm':
        assert pg.evaluate(SOLVE, 'right') == 'ok'; act(pg.locator('#app button.primary').first); pg.wait_for_timeout(60)

def to_check(pg, act):
    for _ in range(8):
        if stage(pg) != 'task': break
        act(pg.locator('#app button.primary').first); pg.wait_for_timeout(40)
    assert stage(pg) == 'check', stage(pg)

def finish_real(pg, act):
    r = pg.evaluate(SOLVE, 'right'); assert r == 'ok', r
    act(pg.locator('#app button.primary').first); pg.wait_for_timeout(300)
    assert stage(pg) == 'done', stage(pg)

def reload(pg): pg.reload(); pg.wait_for_timeout(900)


def chromium_pass(p):
    mock = Mock(); hits = {'n': 0}
    def handle(route): hits['n'] += 1; return mock.handle(route)
    b = p.chromium.launch(executable_path=os.environ.get('CHROME', '/usr/bin/google-chrome'), args=['--no-sandbox'])
    c = b.new_context(viewport={'width': 390, 'height': 844}); c.route('https://api.github.com/**', handle)
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    click = lambda loc: loc.click()
    pg.goto(URL); pg.wait_for_timeout(400)
    # connect the mocked sync and put some real progress in place, so "unchanged" means something
    pg.evaluate("go({name:'parent'})"); pg.wait_for_timeout(80)
    pg.fill('#pcode', '4321'); pg.click('text=Set code'); pg.wait_for_timeout(80)
    pg.fill('#ghrepo', 'fam/progress'); pg.fill('#ghtok', GOOD); pg.click('button:text-is("Connect")'); pg.wait_for_timeout(900)
    ok('mock sync connected', 'private GitHub repo' in pg.inner_text('#sync'), pg.inner_text('#sync'))
    start_real(pg, 'k4', click); to_check(pg, click); finish_real(pg, click)
    ok('real session leaves no unfinished note', pg.evaluate(WIPJ, 'k4') is None)
    age_reviews(pg, 'k4'); pg.wait_for_timeout(900)

    # ---------- FEATURE 1: try the lessons ----------
    pg.evaluate("go({name:'home'})"); pg.wait_for_timeout(80)
    ok('home has the grown-ups entry', btn(pg, 'Grown-ups: try the lessons').count() == 1 and 'Open any session. Nothing here is saved or counted.' in pg.inner_text('#app'))
    audit(pg, 'home'); shot(pg, 'home')
    pg.evaluate("(()=>{window.__saves=0; const _s=Store.save.bind(Store), _p=Store.push.bind(Store); Store.save=(k)=>{window.__saves++; return _s(k);}; Store.push=(k)=>{window.__saves++; return _p(k);};})()")
    before = pg.evaluate(SNAP); hits['n'] = 0; puts0 = mock.puts
    click(btn(pg, 'Grown-ups: try the lessons')); pg.wait_for_timeout(80)
    ok('opens the tryout list without the parent code', pg.evaluate("VIEW.name") == 'tryout' and pg.locator('#pcode').count() == 0)
    want = pg.evaluate("Object.keys(KIDS).map(k=>unitsOf(k).filter(u=>u.sessions).flatMap(u=>u.sessions.map(s=>k+':'+s.id))).flat().sort()")
    got = pg.evaluate("[...document.querySelectorAll('.trytrack')].flatMap(t=>[...t.querySelectorAll('[data-sid]')].map(x=>t.dataset.kid+':'+x.dataset.sid)).sort()")
    ok('list shows every written session for both tracks', want == got and len(got) == 24, str(len(got)))
    ok('list shows every gate quiz', pg.locator('[data-gid]').count() == 4)
    ok('nothing is locked', pg.locator('.trybtn[disabled]').count() == 0 and 'Locked' not in pg.inner_text('#app'))
    ok('track headings use the display names', pg.evaluate("[...document.querySelectorAll('.trytrack h2')].map(h=>h.textContent).join('|') === KIDS.k7.name+'|'+KIDS.k4.name"))
    ok('nav shows no kid in tryout', 'Today' not in pg.inner_text('#nav') and 'My path' not in pg.inner_text('#nav'))
    audit(pg, 'tryout list'); shot(pg, 'tryout_list')
    for sid in ['s01', 's02', 'm01', 'm08']:
        kid = 'k7' if sid[0] == 's' else 'k4'
        click(pg.locator(f'[data-sid="{sid}"]')); pg.wait_for_timeout(60)
        v = pg.evaluate("[VIEW.name, VIEW.stage, VIEW.tryout, VIEW.practice, VIEW.kid]")
        ok(f'tryout {sid}: opens at the task, no warm-up', v == ['session', 'task', True, True, kid], str(v))
        ok(f'tryout {sid}: banner and back button', 'Trying it out. Nothing is saved.' in pg.inner_text('#app') and btn(pg, 'Back to the list').count() == 1)
        ok(f'tryout {sid}: nav shows no kid, tint follows the track', 'Today' not in pg.inner_text('#nav') and pg.evaluate("document.body.classList.contains('kid-k4')") == (kid == 'k4'))
        ok(f'tryout {sid}: no stop/start-over row', pg.locator('.quietrow').count() == 0)
        audit(pg, f'tryout {sid} task')
        if sid == 'm01':
            shot(pg, 'tryout_session')
            n = pg.evaluate("findSession('k4','m01').session.steps.length")
            ok('4th-grade track starts one step at a time', pg.locator('ol.steps > li').count() == 1)
            click(btn(pg, 'Show all steps')); pg.wait_for_timeout(40)
            ok('Show all steps shows them all', pg.locator('ol.steps > li').count() == n, str(pg.locator('ol.steps > li').count()))
            audit(pg, 'tryout m01 all steps'); shot(pg, 'tryout_session_all_steps')
            click(btn(pg, 'Show one step at a time')); pg.wait_for_timeout(40)
            ok('toggle goes back to one step', pg.locator('ol.steps > li').count() == 1)
        if sid == 's01': ok('7th-grade track has no step toggle', btn(pg, 'Show all steps').count() == 0)
        to_check(pg, click)
        ok(f'tryout {sid}: check keeps the banner', 'Trying it out. Nothing is saved.' in pg.inner_text('#app'))
        audit(pg, f'tryout {sid} check')
        r = pg.evaluate(SOLVE, 'right'); ok(f'tryout {sid}: check answered', r == 'ok', r)
        if sid == 's02': ok('tryout written answer says it is not saved', 'Not saved.' in pg.inner_text('#app') and 'Saved. A parent' not in pg.inner_text('#app'))
        audit(pg, f'tryout {sid} check answered')
        click(btn(pg, 'Finish')); pg.wait_for_timeout(60)
        ok(f'tryout {sid}: finish returns to the list with a note', pg.evaluate("VIEW.name") == 'tryout' and pg.locator('#tryflash').count() == 1 and 'Nothing was saved' in pg.inner_text('#tryflash') and 'Session done' not in pg.inner_text('#app'))
        if sid == 's01': audit(pg, 'tryout list with note'); shot(pg, 'tryout_list_after')
    click(pg.locator('[data-gid="g-m1a"]')); pg.wait_for_timeout(60)
    ok('tryout gate: quiz starts at once, with banner', pg.evaluate("!!VIEW.quiz && VIEW.tryout===true") and 'Trying it out' in pg.inner_text('#app') and pg.locator('#app .item').count() == 10)
    audit(pg, 'tryout gate quiz')
    r = pg.evaluate(SOLVE, 'right'); assert r == 'ok', r
    click(btn(pg, 'See my score')); pg.wait_for_timeout(60)
    ok('tryout gate: shows the score, says it was not saved', '10 of 10' in pg.inner_text('#app') and 'not saved' in pg.inner_text('#app') and 'Gate passed' not in pg.inner_text('#app'))
    audit(pg, 'tryout gate score'); shot(pg, 'tryout_gate_score')
    click(btn(pg, 'Back to the list')); pg.wait_for_timeout(60)
    ok('tryout gate: back at the list', pg.evaluate("VIEW.name") == 'tryout')
    # leave a tryout session half way through, by the banner and by the nav
    click(pg.locator('[data-sid="m02"]')); pg.wait_for_timeout(40); click(btn(pg, 'Back to the list')); pg.wait_for_timeout(40)
    click(pg.locator('[data-sid="s03"]')); pg.wait_for_timeout(40); click(pg.locator('#nav button', has_text='Switch person')); pg.wait_for_timeout(300)
    after = pg.evaluate(SNAP)
    ok('tryout: Store docs and localStorage byte-identical', before == after, '' if before == after else str([i for i, (x, y) in enumerate(zip(json.loads(before), json.loads(after))) if x != y]))
    ok('tryout: zero requests to api.github.com', hits['n'] == 0 and mock.puts == puts0, str(hits['n']))
    ok('tryout: Store.save / Store.push never called', pg.evaluate("window.__saves") == 0, str(pg.evaluate("window.__saves")))
    ok('tryout: gate state untouched', pg.evaluate("Object.keys(Store.get('k4').gates).length") == 0)

    # ---------- FEATURE 2: stop, keep going, start over ----------
    # 4th-grade track, stopped at a task step (m02 has 3 steps; m01 is done, so a warm-up is due)
    logn = pg.evaluate("Store.get('k4').log.length"); WK = "(()=>{const c=counts('k4'); return JSON.stringify([c.todayN,c.weekN,c.total,c.dayStreak,c.weekStreak])})()"; wk = pg.evaluate(WK)
    start_real(pg, 'k4', click)
    ok('k4: at m02 task', pg.evaluate("[VIEW.sid, VIEW.stage, VIEW.stepIdx]") == ['m02', 'task', 0])
    ok('k4: note written when the task starts', (pg.evaluate(WIPJ, 'k4') or {}).get('stepIdx') == 0)
    click(btn(pg, 'Next step')); pg.wait_for_timeout(40)
    w = pg.evaluate(WIPJ, 'k4')
    ok('k4: note follows the step', w and w['sid'] == 'm02' and w['stage'] == 'task' and w['stepIdx'] == 1 and w['card'] is False and sorted(w.keys()) == ['card', 'minutesSoFar', 'sid', 'stage', 'startedAt', 'stepIdx', 't'], str(w))
    ok('session has the quiet bottom row', btn(pg, 'Stop for now').count() == 1 and btn(pg, 'Start over').count() == 1)
    audit(pg, 'k4 session with bottom row'); shot(pg, 'session_bottom_row')
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('Stop for now returns to Today', pg.evaluate("VIEW.name") == 'kid')
    ok('Today card: line, Keep going, Start this session over', pg.inner_text('#wipline') == 'You stopped at step 2 of 3.' and btn(pg, 'Keep going').count() == 1 and btn(pg, 'Start this session over').count() == 1 and pg.locator('#app button.primary').first.inner_text() == 'Keep going', pg.inner_text('#app')[:300])
    audit(pg, 'k4 Today with unfinished session'); shot(pg, 'today_wip')
    ok('stopping does not touch the log or the week count', pg.evaluate("Store.get('k4').log.length") == logn and pg.evaluate(WK) == wk)
    reload(pg); age_reviews(pg, 'k4')
    start_real(pg, 'k4', click)
    ok('k4: resumes at the saved step after a reload, no warm-up', pg.evaluate("[VIEW.sid, VIEW.stage, VIEW.stepIdx]") == ['m02', 'task', 1] and pg.locator('ol.steps > li').count() == 2, str(pg.evaluate("[VIEW.sid, VIEW.stage, VIEW.stepIdx]")))
    # start over from the task: two taps, inline
    dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))
    click(btn(pg, 'Start over')); pg.wait_for_timeout(40)
    ok('start over asks first, inline', pg.evaluate("VIEW.stepIdx") == 1 and btn(pg, 'Yes, start over').count() == 1 and not dialogs)
    audit(pg, 'start-over confirm'); shot(pg, 'start_over_confirm')
    click(btn(pg, 'No, keep my place')); pg.wait_for_timeout(40)
    ok('No keeps the place', pg.evaluate("VIEW.stepIdx") == 1 and btn(pg, 'Start over').count() == 1 and btn(pg, 'Yes, start over').count() == 0)
    click(btn(pg, 'Start over')); click(btn(pg, 'Yes, start over')); pg.wait_for_timeout(60)
    w = pg.evaluate(WIPJ, 'k4')
    ok('start over from the task: back to step 1, clock reset', pg.evaluate("[VIEW.stage, VIEW.stepIdx]") == ['task', 0] and w['stepIdx'] == 0 and w['minutesSoFar'] < 0.2 and '08:00' in pg.inner_text('.timer') or '07:5' in pg.inner_text('.timer'), str(w))
    # stop at the check
    to_check(pg, click)
    ok('k4: note says check', pg.evaluate(WIPJ, 'k4')['stage'] == 'check')
    audit(pg, 'k4 check with bottom row')
    pg.evaluate("(()=>{const it=findSession('k4','m02').session.check[0]; [...document.querySelectorAll('#app .item')[0].querySelectorAll('.opts button')].find(x=>x.textContent===it.opts[it.a]).click();})()")
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('Today card: stopped at the quick check', pg.inner_text('#wipline') == 'You stopped at the quick check.')
    reload(pg); age_reviews(pg, 'k4')
    start_real(pg, 'k4', click)
    ok('k4: resumes at the check, questions unanswered', pg.evaluate("[VIEW.sid, VIEW.stage]") == ['m02', 'check'] and pg.locator('#app .opts button.right').count() == 0 and pg.locator('#app button.primary').first.is_disabled() and pg.locator('#resumeline').count() == 1)
    audit(pg, 'k4 resumed check'); shot(pg, 'resumed_check_k4')
    # start over from the check
    pg.evaluate("(()=>{const it=findSession('k4','m02').session.check[0]; [...document.querySelectorAll('#app .item')[0].querySelectorAll('.opts button')].find(x=>x.textContent===it.opts[it.a]).click();})()")
    click(btn(pg, 'Start over')); click(btn(pg, 'Yes, start over')); pg.wait_for_timeout(60)
    ok('start over from the check: step 1 of the task, answers cleared', pg.evaluate("[VIEW.stage, VIEW.stepIdx, Object.keys(VIEW.results).length]") == ['task', 0, 0])
    # resumed minutes: 4 minutes banked earlier, then finish now
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(40)
    pg.evaluate("(()=>{const w=JSON.parse(localStorage.getItem('datalab:wip:k4')); w.minutesSoFar=4; localStorage.setItem('datalab:wip:k4', JSON.stringify(w));})()")
    reload(pg); age_reviews(pg, 'k4'); start_real(pg, 'k4', click)
    ok('timer carries on from the minutes so far', re.match(r'0[34]:\d\d', pg.inner_text('.timer')) is not None, pg.inner_text('.timer'))
    to_check(pg, click); finish_real(pg, click); pg.wait_for_timeout(600)
    ok('minutes recorded are the total across sittings', pg.evaluate("Store.get('k4').done.m02.mins") == 4, str(pg.evaluate("Store.get('k4').done.m02.mins")))
    ok('note cleared after finish', pg.evaluate(WIPJ, 'k4') is None)
    ok('finished session counts once today', pg.evaluate("Store.get('k4').log.length") == logn + 1)
    # tally widget: start over fully resets it (m03)
    age_reviews(pg, 'k4'); start_real(pg, 'k4', click); to_check(pg, click)
    pg.evaluate("(()=>{const e=document.querySelector('#app .item'); const ins=[...e.querySelectorAll('.tally-grid input')]; [['Red',4],['Blue',7]].forEach((r,k)=>{ins[k*2].value=r[0]; ins[k*2+1].value=String(r[1]);}); [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Draw my graph').click();})()"); pg.wait_for_timeout(40)
    ok('tally graph drawn before start over', pg.locator('#app .item .fig').count() == 1)
    click(btn(pg, 'Start over')); click(btn(pg, 'Yes, start over')); pg.wait_for_timeout(60)
    to_check(pg, click)
    ok('start over resets the tally widget', pg.locator('#app .item .fig').count() == 0 and pg.evaluate("[...document.querySelectorAll('.tally-grid input')].every(i=>i.value==='')"))
    # cap: a silly number of minutes is capped at 3x
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(40)
    pg.evaluate("(()=>{const w=JSON.parse(localStorage.getItem('datalab:wip:k4')); w.minutesSoFar=999; localStorage.setItem('datalab:wip:k4', JSON.stringify(w));})()")
    start_real(pg, 'k4', click)
    ok('timer past time reads Time, not a negative number', pg.inner_text('#app').count('NaN') == 0 and '-' not in (pg.inner_text('.timer') if pg.locator('.timer').count() else ''))
    finish_real(pg, click); pg.wait_for_timeout(600)
    ok('minutes capped at 3x the session', pg.evaluate("Store.get('k4').done.m03.mins === 3*findSession('k4','m03').session.mins"), str(pg.evaluate("Store.get('k4').done.m03.mins")))

    # 7th-grade track
    start_real(pg, 'k7', click)
    ok('k7: at s01 task, all steps shown', pg.evaluate("[VIEW.sid, VIEW.stage]") == ['s01', 'task'] and pg.locator('ol.steps > li').count() == 4)
    audit(pg, 'k7 session with bottom row')
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('k7 Today card line at the task', pg.inner_text('#wipline') == 'You stopped partway through the steps.')
    audit(pg, 'k7 Today with unfinished session')
    reload(pg); start_real(pg, 'k7', click)
    ok('k7: resumes at the task after a reload', pg.evaluate("[VIEW.sid, VIEW.stage, VIEW.resumed]") == ['s01', 'task', True])
    to_check(pg, click)
    pg.locator('#app .item .chips button').first.click(); pg.wait_for_timeout(40)
    ok('experiment under way', pg.locator('.reactpad').count() == 1)
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('k7 Today card line at the experiment', pg.inner_text('#wipline') == 'You stopped at the experiment.')
    reload(pg); start_real(pg, 'k7', click)
    ok('k7: resumes at the check, experiment not started', pg.evaluate("[VIEW.sid, VIEW.stage]") == ['s01', 'check'] and pg.locator('.reactpad').count() == 0 and pg.locator('#app .item .chips button').count() == 3)
    audit(pg, 'k7 resumed check')
    pg.locator('#app .item .chips button').first.click(); pg.wait_for_timeout(40)
    click(btn(pg, 'Start over')); click(btn(pg, 'Yes, start over')); pg.wait_for_timeout(60)
    ok('k7: start over from the check goes to the task', pg.evaluate("VIEW.stage") == 'task')
    to_check(pg, click)
    ok('start over resets the reaction-time experiment', pg.locator('.reactpad').count() == 0 and pg.locator('#app .item .chips button').count() == 3)
    finish_real(pg, click); pg.wait_for_timeout(600)
    ok('k7: note cleared after finish', pg.evaluate(WIPJ, 'k7') is None)
    # typed answers survive a stop at the check (s02 has a written answer)
    age_reviews(pg, 'k7'); start_real(pg, 'k7', click); to_check(pg, click)
    r = pg.evaluate(SOLVE, 'right'); assert r == 'ok', r
    pg.wait_for_timeout(500); click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    reload(pg); age_reviews(pg, 'k7'); start_real(pg, 'k7', click)
    ok('k7: resumed check prefills the typed answer and says so', pg.evaluate("VIEW.stage") == 'check' and pg.inner_text('#resumeline') == 'Your typed answers are still here. Answer the rest again.' and pg.input_value('#app textarea').startswith('I asked which kind') and pg.locator('#app .opts button.right').count() == 0 and pg.locator('#app button.primary').first.is_disabled())
    audit(pg, 'k7 resumed check with typed answer'); shot(pg, 'resumed_check_typed')
    click(btn(pg, 'Stop for now')); pg.wait_for_timeout(600)

    # nothing about unfinished sessions reaches the repo
    blob = json.dumps({k: mock.read(k) for k in mock.files})
    ok('unfinished-session note never reaches the GitHub repo', sorted(mock.files) == ['state/device-check.json', 'state/k4.json', 'state/k7.json', 'state/parent.json'] and 'wip' not in blob and 'minutesSoFar' not in blob and 'stepIdx' not in blob, str(sorted(mock.files)))
    ok('unfinished-session note is not in the Store docs', pg.evaluate("!/wip|minutesSoFar|stepIdx/.test(JSON.stringify([Store.get('k7'),Store.get('k4'),Store.get('parent')]))"))

    # stale notes are dropped
    pg.evaluate("(()=>{const w=JSON.parse(localStorage.getItem('datalab:wip:k7')); w.t=Date.now()-15*24*3600*1000; localStorage.setItem('datalab:wip:k7', JSON.stringify(w));})()")
    pg.evaluate("go({name:'kid',kid:'k7'})"); pg.wait_for_timeout(60)
    ok('note older than 14 days is dropped', pg.evaluate(WIPJ, 'k7') is None and pg.locator('#wipline').count() == 0 and btn(pg, 'Start this session over').count() == 0)
    pg.evaluate("localStorage.setItem('datalab:wip:k7', JSON.stringify({sid:'s09', stage:'task', stepIdx:0, card:false, startedAt:Date.now(), minutesSoFar:1, t:Date.now()}))")
    pg.evaluate("go({name:'kid',kid:'k7'})"); pg.wait_for_timeout(60)
    ok('note for a session that is not next is dropped', pg.evaluate(WIPJ, 'k7') is None and pg.locator('#wipline').count() == 0)
    # Today: Start this session over
    start_real(pg, 'k4', click); click(btn(pg, 'Next step')); click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('k4 has a note before Start this session over', pg.evaluate(WIPJ, 'k4')['stepIdx'] == 1)
    click(btn(pg, 'Start this session over')); pg.wait_for_timeout(60)
    if stage(pg) == 'warm': assert pg.evaluate(SOLVE, 'right') == 'ok'; click(pg.locator('#app button.primary').first); pg.wait_for_timeout(60)
    ok('Start this session over begins at step 1', pg.evaluate("[VIEW.stage, VIEW.stepIdx, VIEW.resumed||false]") == ['task', 0, False] and pg.evaluate(WIPJ, 'k4')['stepIdx'] == 0)
    # Erase clears it (through the real Parent view buttons)
    click(btn(pg, 'Next step')); click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    start_real(pg, 'k7', click); click(btn(pg, 'Stop for now')); pg.wait_for_timeout(60)
    ok('both kids have a note before Erase', pg.evaluate(WIPJ, 'k4') is not None and pg.evaluate(WIPJ, 'k7') is not None)
    pg.evaluate("go({name:'parent'})"); pg.wait_for_timeout(60); pg.fill('#pcode', '4321'); pg.click('text=Open'); pg.wait_for_timeout(60)
    pg.locator('#app button', has_text=re.compile('^Erase .* progress$')).nth(1).click(); pg.wait_for_timeout(40); click(btn(pg, 'Yes, erase')); pg.wait_for_timeout(600)
    ok('Erase clears that kid\'s note only', pg.evaluate(WIPJ, 'k4') is None and pg.evaluate(WIPJ, 'k7') is not None and pg.evaluate("counts('k4').total") == 0)
    pg.evaluate("go({name:'kid',kid:'k4'})"); pg.wait_for_timeout(60)
    ok('after Erase the Today card is a plain start', btn(pg, 'Start session').count() == 1 and pg.locator('#wipline').count() == 0)
    # practice replay from the path writes no note
    pg.evaluate("startSession('k7','s01',true)"); pg.wait_for_timeout(40)
    ok('practice replay has no bottom row', pg.locator('.quietrow').count() == 0)
    ok('no dialogs were used', not dialogs, str(dialogs))
    b.close()


def webkit_pass(p):
    b = p.webkit.launch(); c = b.new_context(**p.devices['iPhone 13']); pg = c.new_page()
    pg.on('pageerror', lambda e: errs.append('webkit: ' + str(e)))
    tap = lambda loc: loc.tap(timeout=4000)
    pg.goto(URL); pg.wait_for_timeout(700)
    audit(pg, 'iPhone home'); shot(pg, 'iphone_home')
    before = pg.evaluate(SNAP)
    tap(btn(pg, 'Grown-ups: try the lessons')); pg.wait_for_timeout(80)
    ok('iPhone: tap opens the tryout list', pg.evaluate("VIEW.name") == 'tryout' and pg.locator('[data-sid]').count() == 24)
    audit(pg, 'iPhone tryout list'); shot(pg, 'iphone_tryout_list')
    tap(pg.locator('[data-sid="m01"]')); pg.wait_for_timeout(80)
    ok('iPhone: tap opens a tryout session with the banner', pg.evaluate("VIEW.tryout===true && VIEW.stage==='task'") and 'Trying it out. Nothing is saved.' in pg.inner_text('#app'))
    audit(pg, 'iPhone tryout session'); shot(pg, 'iphone_tryout_session')
    tap(btn(pg, 'Show all steps')); pg.wait_for_timeout(60)
    ok('iPhone: Show all steps', pg.locator('ol.steps > li').count() == 4)
    audit(pg, 'iPhone tryout all steps')
    to_check(pg, tap); audit(pg, 'iPhone tryout check'); shot(pg, 'iphone_tryout_check')
    tap(btn(pg, 'Back to the list')); pg.wait_for_timeout(60)
    tap(pg.locator('[data-gid="g-s1a"]')); pg.wait_for_timeout(60)
    audit(pg, 'iPhone tryout gate'); assert pg.evaluate(SOLVE, 'right') == 'ok'
    tap(btn(pg, 'See my score')); pg.wait_for_timeout(60); audit(pg, 'iPhone tryout gate score')
    tap(btn(pg, 'Back to the list')); pg.wait_for_timeout(60)
    ok('iPhone: tryout left everything byte-identical', pg.evaluate(SNAP) == before)
    tap(pg.locator('#app button', has_text=re.compile('^Back$'))); pg.wait_for_timeout(60)
    tap(pg.locator('.who button').nth(1)); pg.wait_for_timeout(80)
    tap(btn(pg, 'Start session')); pg.wait_for_timeout(60)
    tap(btn(pg, 'Next step')); pg.wait_for_timeout(60); tap(btn(pg, 'Next step')); pg.wait_for_timeout(60)
    audit(pg, 'iPhone session with bottom row'); shot(pg, 'iphone_session_bottom_row')
    tap(btn(pg, 'Start over')); pg.wait_for_timeout(60)
    audit(pg, 'iPhone start-over confirm'); shot(pg, 'iphone_start_over_confirm')
    tap(btn(pg, 'No, keep my place')); pg.wait_for_timeout(60)
    tap(btn(pg, 'Stop for now')); pg.wait_for_timeout(80)
    ok('iPhone: Stop for now, Today card shows the place', pg.evaluate("VIEW.name") == 'kid' and pg.inner_text('#wipline') == 'You stopped at step 3 of 4.')
    audit(pg, 'iPhone Today with unfinished session'); shot(pg, 'iphone_today_wip')
    reload(pg)
    tap(pg.locator('.who button').nth(1)) if pg.evaluate("VIEW.name") == 'home' else None; pg.wait_for_timeout(80)
    tap(btn(pg, 'Keep going')); pg.wait_for_timeout(80)
    ok('iPhone: Keep going resumes at step 3 after a reload', pg.evaluate("[VIEW.sid, VIEW.stage, VIEW.stepIdx]") == ['m01', 'task', 2])
    tap(btn(pg, 'Next step')); pg.wait_for_timeout(60); to_check(pg, tap)
    audit(pg, 'iPhone check with bottom row'); shot(pg, 'iphone_check_bottom_row')
    tap(btn(pg, 'Stop for now')); pg.wait_for_timeout(80)
    ok('iPhone: stopped at the quick check', pg.inner_text('#wipline') == 'You stopped at the quick check.')
    tap(btn(pg, 'Keep going')); pg.wait_for_timeout(80)
    ok('iPhone: resumes at the check', pg.evaluate("VIEW.stage") == 'check')
    audit(pg, 'iPhone resumed check')
    tap(btn(pg, 'Start over')); pg.wait_for_timeout(60); tap(btn(pg, 'Yes, start over')); pg.wait_for_timeout(80)
    ok('iPhone: start over goes to step 1', pg.evaluate("[VIEW.stage, VIEW.stepIdx]") == ['task', 0])
    to_check(pg, tap); finish_real(pg, tap)
    ok('iPhone: note cleared after finish', pg.evaluate(WIPJ, 'k4') is None and pg.evaluate("!!Store.get('k4').done.m01"))
    # dark scheme look
    pg.emulate_media(color_scheme='dark'); pg.evaluate("go({name:'tryout'})"); pg.wait_for_timeout(80); shot(pg, 'iphone_tryout_list_dark')
    b.close()


with sync_playwright() as p:
    chromium_pass(p)
    webkit_pass(p)
fails = [r for r in res if not r[1]]
print('page errors:', errs)
print('%d passed, %d failed' % (len(res) - len(fails), len(fails)))
print('FAILED:', fails)
sys.exit(1 if fails or errs else 0)
