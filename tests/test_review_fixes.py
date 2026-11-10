"""Regression tests for the 10 November 2026 outside review of commit c23ac9a (eight findings).
Chromium at 390x844, page opened from disk, synthetic data only, a fresh browser context per check so no check
depends on another's leftovers. Exits non-zero if any check fails.

  python3 test_review_fixes.py            # all checks
  python3 test_review_fixes.py erase      # only checks whose name contains "erase"
"""
import os, re, sys, json
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = os.environ.get('U', 'file://' + os.path.abspath(os.path.join(HERE, '..', 'index.html')))
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
SOLVE = re.search(r"SOLVE = r'''\n(.*?)\n'''", open(os.path.join(HERE, 'walk.py')).read(), re.S).group(1)
ONLY = sys.argv[1] if len(sys.argv) > 1 else ''

results = []
def ok(name, cond, extra=''):
    results.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + str(extra)[:400]))

# Page-side helpers, installed once per page.
HELPERS = r'''() => {
  window.__T = {
    sleep: ms => new Promise(r=>setTimeout(r, ms)),
    // Another device erased this kid: the remote doc is a blank one with a higher epoch.
    async remoteErase(kid){
      const remote = Object.assign(Store.blank(), {epoch: (Store.get(kid).epoch||0)+1, ts: Date.now()});
      Store.db = {doc: () => ({get: async () => ({exists:true, data:()=>JSON.parse(JSON.stringify(remote))}), set: async () => {}})};
      await Store.pull(kid); await __T.sleep(20); Store.db = null;
    },
    record(kid){ const d = Store.get(kid); return {done:Object.keys(d.done), ans:d.ans, gates:d.gates, log:d.log, rev:Object.keys(d.rev), stats:d.stats, wip:localStorage.getItem('datalab:wip:'+kid)}; },
    emptyRecord(r){ return !r.done.length && !Object.keys(r.ans).length && !Object.keys(r.gates).length && !r.log.length && !r.rev.length && !r.stats.fn && !r.stats.fok && !r.stats.rn && !r.stats.rok && r.wip===null; },
    // Put a kid at a session: everything before it in the track marked done.
    placeAt(kid, sid){ const st = Store.get(kid); for(const u of unitsOf(kid)){ if(!u.sessions) continue; for(const s of u.sessions){ if(s.id===sid){ Store.save(kid); return; } st.done[s.id] = {t:1, first:0, auto:0, mins:1}; st.log.push({d:'2026-01-05', sid:s.id}); } const g = gateState(kid, u); st.gates[u.gate.id] = {quiz:{best:g.n, last:g.n, n:g.n, t:1, d:'2026-01-05', tries:1, missed:[]}, sign:{t:1}}; } },
    toCheck(){ VIEW.stage = 'check'; render(); },
    textItem(){ return [...document.querySelectorAll('#app .item')].find(e=>e.querySelector('textarea')); },
    submitText(text){ const e = __T.textItem(); e.querySelector('textarea').value = text; e.querySelector('button.second').click(); },
    clickMc(e, it, right){ const want = right ? it.opts[it.a] : it.opts[(it.a+1)%it.opts.length]; [...e.querySelectorAll('.opts button')].find(b=>b.textContent===want).click(); },
  };
}'''

def page(browser):
    ctx = browser.new_context(viewport={'width': 390, 'height': 844})
    ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())   # no network: fonts and APIs fail fast
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_function('Store.tried'); pg.evaluate(HELPERS)
    pg.evaluate('window.__FAST = true')
    return ctx, pg, errs

CHECKS = []
def check(fn): CHECKS.append(fn); return fn

# ---------------------------------------------------------------- 1. erase vs an open run (P1)
@check
def erase_old_finish_button(pg):
    r = pg.evaluate(r'''async (SOLVE) => {
      __T.placeAt('k4','m02'); startSession('k4','m02'); __T.toCheck();
      const res = await (0,eval)('('+SOLVE+')')('right'); if(res!=='ok') return {err:res};
      const fin = document.querySelector('#app button.primary'); const ready = !fin.disabled;
      await __T.remoteErase('k4');
      fin.click();   // a detached button still runs its handler
      await __T.sleep(50);
      return {ready, rec:__T.record('k4'), view:VIEW.name, flash:!!document.querySelector('#kidflash')}; }''', SOLVE)
    ok('erase: the old Finish button writes nothing; the kid lands on Today with a note', r.get('ready') and pg.evaluate('r=>__T.emptyRecord(r)', r['rec']) and r['view'] == 'kid' and r['flash'], r)

@check
def erase_pending_grade(pg):
    r = pg.evaluate(r'''async () => {
      let release; AI.sample = () => new Promise(res=>{ release = res; });
      __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck();
      const s = findSession('k7','s02').session; const els = [...document.querySelectorAll('#app .item')];
      s.check.forEach((it,i)=>{ if(it.t==='mc') __T.clickMc(els[i], it, true); });
      const fin = document.querySelector('#app button.primary');
      __T.submitText('Synthetic answer that names an animal, a column and a reason.');
      await __T.sleep(20);
      await __T.remoteErase('k7');
      release({text: JSON.stringify({ok:true, fb:'Nice.'})}); await __T.sleep(50);
      fin.click(); await __T.sleep(50);
      return __T.record('k7'); }''')
    ok('erase: a text grade that returns after the erase writes nothing', pg.evaluate('r=>__T.emptyRecord(r)', r), r)

@check
def erase_open_gate(pg):
    r = pg.evaluate(r'''async (SOLVE) => {
      const u = unitsOf('k4')[0]; for(const s of u.sessions){ Store.get('k4').done[s.id] = {t:1,first:0,auto:0,mins:1}; } Store.save('k4');
      go({name:'gate', kid:'k4', gid:u.gate.id}); [...document.querySelectorAll('#app button.primary')].find(b=>/quiz/.test(b.textContent)).click();
      const res = await (0,eval)('('+SOLVE+')')('right'); if(res!=='ok') return {err:res};
      const fin = [...document.querySelectorAll('#app button.primary')].find(b=>b.textContent==='See my score');
      await __T.remoteErase('k4'); fin.click(); await __T.sleep(30);
      return {rec:__T.record('k4'), view:VIEW.name}; }''', SOLVE)
    ok('erase: an open gate quiz writes no score', r.get('rec') and pg.evaluate('r=>__T.emptyRecord(r)', r['rec']) and r['view'] == 'kid', r)

@check
def erase_open_warmup(pg):
    r = pg.evaluate(r'''async () => {
      __T.placeAt('k4','m02'); const key = autoItems(unitsOf('k4')[0]).find(a=>a.sid==='m01').key; schedule('k4',key,true); Store.get('k4').rev[key].due = '2020-01-01'; Store.save('k4');
      startSession('k4','m02'); if(VIEW.stage!=='warm') return {err:'no warm-up: '+VIEW.stage};
      const els = [...document.querySelectorAll('#app .item')], items = VIEW.warm.map(w=>w.item);
      await __T.remoteErase('k4');
      items.forEach((it,i)=>{ if(it.t==='mc') __T.clickMc(els[i], it, true); else { els[i].querySelector('input').value = String(it.a); els[i].querySelector('button.second').click(); } });
      await __T.sleep(30); return __T.record('k4'); }''')
    ok('erase: answering an open warm-up afterwards writes no review stats', r.get('err') is None and pg.evaluate('r=>__T.emptyRecord(r)', r), r)

@check
def erase_then_new_session_saves(pg):
    r = pg.evaluate(r'''async (SOLVE) => {
      __T.placeAt('k4','m02'); startSession('k4','m02'); await __T.remoteErase('k4');
      startSession('k4','m01'); if(VIEW.stage==='warm') return {err:'warm'}; __T.toCheck();
      const res = await (0,eval)('('+SOLVE+')')('right'); if(res!=='ok') return {err:res};
      document.querySelector('#app button.primary').click(); await __T.sleep(30);
      const d = Store.get('k4'); return {done:Object.keys(d.done), log:d.log.length, epoch:d.epoch, wip:localStorage.getItem('datalab:wip:k4')}; }''', SOLVE)
    ok('erase: a session started afterwards saves normally', r.get('done') == ['m01'] and r['log'] == 1 and r['epoch'] == 1 and r['wip'] is None, r)

@check
def erase_drops_note_from_old_epoch(pg):
    r = pg.evaluate(r'''() => {
      __T.placeAt('k4','m02'); localStorage.setItem('datalab:wip:k4', JSON.stringify({sid:'m02', stage:'task', stepIdx:1, card:false, startedAt:Date.now(), minutesSoFar:1, t:Date.now(), att:'x', epoch:0, drafts:{}}));
      Store.get('k4').epoch = 3; return WIP.get('k4'); }''')
    ok('erase: a note written in an older epoch is not offered', r is None, r)

# ---------------------------------------------------------------- 2. merge (P1)
@check
def merge_distinct_items(pg):
    r = pg.evaluate(r'''() => { const a = Store.blank(), b = Store.blank();
      a.ans.s01 = {a:{right:[200], left:[210], predict:'My right hand', mr:200, ml:210}}; b.ans.s01 = {c:{a:'Synthetic reflection', ok:null, fb:''}};
      return [Store.merge(a,b), Store.merge(b,a)].map(m=>Object.keys(m.ans.s01).sort().join()); }''')
    ok('merge: distinct unfinished items both survive, in either order', r == ['a,c', 'a,c'], r)

@check
def merge_survives_reload(pg):
    pg.evaluate(r'''() => { const a = Store.blank(), b = Store.blank(); a.ans.s01 = {a:{right:[1],left:[2]}}; b.ans.s01 = {c:{a:'x'}};
      Store.adopt('k7', Store.merge(a, b)); Store.save('k7'); }''')
    pg.reload(); pg.wait_for_function('Store.tried')
    r = pg.evaluate("Object.keys(Store.get('k7').ans.s01||{}).sort().join()")
    ok('merge: the merged items survive a reload', r == 'a,c', r)

@check
def merge_competing_edits(pg):
    r = pg.evaluate(r'''() => { const mk = v => Object.assign(Store.blank(), {ans:{s01:{c:v}}});
      const timed = [Store.merge(mk({a:'one',u:5}), mk({a:'two',u:9})), Store.merge(mk({a:'two',u:9}), mk({a:'one',u:5}))].map(m=>m.ans.s01.c.a);
      const legacy = [Store.merge(mk({a:'one'}), mk({a:'two'})), Store.merge(mk({a:'two'}), mk({a:'one'}))].map(m=>m.ans.s01.c.a);
      return {timed, legacy}; }''')
    ok('merge: competing edits to one item: later edit wins; without edit times the pick is the same in both orders', r['timed'] == ['two', 'two'] and r['legacy'][0] == r['legacy'][1], r)

@check
def merge_finished_vs_draft(pg):
    r = pg.evaluate(r'''() => { const a = Store.blank(), b = Store.blank();
      a.done.s02 = {t:10, first:2, auto:2, mins:12}; a.ans.s02 = {c:{a:'final', ok:true, fb:'ok'}};
      b.ans.s02 = {c:{a:'old partial draft', ok:null, fb:''}, z:{a:'stray'}};
      return [Store.merge(a,b), Store.merge(b,a)].map(m=>JSON.stringify(m.ans.s02)); }''')
    ok('merge: a finished attempt keeps its answers together against another device\'s draft', r[0] == r[1] and json.loads(r[0]) == {'c': {'a': 'final', 'ok': True, 'fb': 'ok'}}, r)

@check
def merge_erase_vs_old_draft(pg):
    r = pg.evaluate(r'''() => { const a = Object.assign(Store.blank(), {epoch:1}), b = Store.blank(); b.ans.s01 = {c:{a:'old'}}; b.done.s01 = {t:5};
      return [Store.merge(a,b), Store.merge(b,a)].map(m=>[m.epoch, Object.keys(m.ans).length, Object.keys(m.done).length]); }''')
    ok('merge: an erase beats an old draft in either order', r == [[1, 0, 0], [1, 0, 0]], r)

@check
def drafts_do_not_sync_before_finish(pg):
    r = pg.evaluate(r'''async () => { __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck(); __T.submitText('A draft that should stay on this device until Finish.'); await __T.sleep(30);
      const w = JSON.parse(localStorage.getItem('datalab:wip:k7')); return {store: Store.get('k7').ans.s02 || null, draft: w && w.drafts && w.drafts.b && w.drafts.b.a}; }''')
    ok('drafts: a submitted answer stays in the device note until Finish', r['store'] is None and (r['draft'] or '').startswith('A draft'), r)

# ---------------------------------------------------------------- 3. start over (P2)
TEXT = 'I found the last dot in the graph, and it was the animal with the most sleep.'
def _typed(pg, setup):
    return pg.evaluate(r'''async ([setup, TEXT]) => { __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck(); __T.submitText(TEXT); await __T.sleep(30);
      await (0,eval)('(async()=>{'+setup+'})')(); await __T.sleep(30);
      if(VIEW.name==='session' && VIEW.stage!=='check'){ VIEW.stage='check'; render(); }
      const e = __T.textItem(); return {view:VIEW.name, stage:VIEW.stage, value: e ? e.querySelector('textarea').value : null, stored: Store.get('k7').ans.s02 || null}; }''', [setup, TEXT])

@check
def restart_in_session(pg):
    r = _typed(pg, "restartSession(VIEW);")
    ok('start over (in session): the text box is empty and nothing was stored', r['value'] == '' and r['stored'] is None, r)

@check
def restart_from_today(pg):
    r = _typed(pg, "[...document.querySelectorAll('#app button')].find(b=>b.textContent==='Stop for now').click(); await __T.sleep(20); [...document.querySelectorAll('#app button')].find(b=>b.textContent==='Start this session over').click();")
    ok('start over (from Today): the text box is empty', r['value'] == '' and r['stored'] is None, r)

@check
def keep_going_restores(pg):
    r = _typed(pg, "[...document.querySelectorAll('#app button')].find(b=>b.textContent==='Stop for now').click(); await __T.sleep(20); [...document.querySelectorAll('#app button')].find(b=>b.textContent==='Keep going').click();")
    ok('keep going: the typed answer comes back', r['value'] == TEXT and r['stage'] == 'check', r)

@check
def keep_going_after_reload(pg):
    _typed(pg, "[...document.querySelectorAll('#app button')].find(b=>b.textContent==='Stop for now').click();")
    pg.reload(); pg.wait_for_function('Store.tried'); pg.evaluate(HELPERS)
    r = pg.evaluate(r'''async () => { go({name:'kid', kid:'k7'}); [...document.querySelectorAll('#app button')].find(b=>b.textContent==='Keep going').click(); await __T.sleep(20);
      return {value: __T.textItem().querySelector('textarea').value, line: (document.querySelector('#resumeline')||{}).textContent}; }''')
    ok('keep going after a reload: the typed answer comes back and the page says so', r['value'] == TEXT and 'still here' in (r['line'] or ''), r)

@check
def restart_with_pending_grade(pg):
    r = pg.evaluate(r'''async (TEXT) => { let release; AI.sample = () => new Promise(res=>{ release = res; });
      __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck(); __T.submitText(TEXT); await __T.sleep(20);
      restartSession(VIEW); release({text: JSON.stringify({ok:true, fb:'Good.'})}); await __T.sleep(50);
      VIEW.stage = 'check'; render();
      const w = JSON.parse(localStorage.getItem('datalab:wip:k7'));
      return {results:Object.keys(VIEW.results), drafts:Object.keys((w||{}).drafts||{}), value:__T.textItem().querySelector('textarea').value, stored:Store.get('k7').ans.s02||null}; }''', TEXT)
    ok('start over with a grade pending: the late grade lands nowhere', r['results'] == [] and r['drafts'] == [] and r['value'] == '' and r['stored'] is None, r)

@check
def legacy_saved_answer(pg):
    r = pg.evaluate(r'''async () => { __T.placeAt('k7','s02'); Store.get('k7').ans.s02 = {b:{a:'Legacy answer from an older version', ok:null, fb:''}}; Store.save('k7');
      startSession('k7','s02'); __T.toCheck(); const fresh = __T.textItem().querySelector('textarea').value;
      go({name:'home'});   // leave first: go() saves the outgoing session's own note
      // a note from before drafts were kept in it, as an upgraded device would have: Keep going imports the old answer once
      localStorage.setItem('datalab:wip:k7', JSON.stringify({sid:'s02', stage:'check', stepIdx:0, card:false, startedAt:Date.now(), minutesSoFar:1, t:Date.now()}));
      go({name:'kid', kid:'k7'}); [...document.querySelectorAll('#app button')].find(b=>b.textContent==='Keep going').click(); await __T.sleep(20);
      const resumed = __T.textItem().querySelector('textarea').value;
      restartSession(VIEW); VIEW.stage = 'check'; render(); const after = __T.textItem().querySelector('textarea').value;
      return {fresh, resumed, after}; }''')
    ok('older saved answer: a fresh start ignores it, an old note imports it once, start over clears it', r['fresh'] == '' and r['resumed'].startswith('Legacy') and r['after'] == '', r)

@check
def replay_keeps_original_answers(pg):
    r = pg.evaluate(r'''async (SOLVE) => { __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck();
      if(await (0,eval)('('+SOLVE+')')('right') !== 'ok') return {err:1}; document.querySelector('#app button.primary').click(); await __T.sleep(30);
      const orig = JSON.stringify(Store.get('k7').ans.s02);
      startSession('k7','s02',true); __T.toCheck(); const pre = __T.textItem().querySelector('textarea').value;
      if(await (0,eval)('('+SOLVE+')')('right') !== 'ok') return {err:2}; document.querySelector('#app button.primary').click(); await __T.sleep(30);
      return {same: JSON.stringify(Store.get('k7').ans.s02)===orig, pre, done: VIEW.stage}; }''', SOLVE)
    ok('practice replay of a finished lesson leaves its saved answers alone', r.get('same') and r['done'] == 'done', r)

# ---------------------------------------------------------------- 4. tally (P2)
DRAW = r'''(rows) => { const e = document.querySelector('#app .item'); const ins = [...e.querySelectorAll('.tally-grid input')];
  ins.forEach(i=>{ i.value=''; }); rows.forEach((r,k)=>{ ins[k*2].value = r[0]; ins[k*2+1].value = String(r[1]); });
  const g = e.querySelector('input[id^="tg-"]'); if(g) g.value = 'Red';
  [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Draw my graph').click();
  return {graph: !!e.querySelector('.fig'), msg: (e.querySelector('.fb.bad')||{}).textContent || '', focus: document.activeElement && document.activeElement.id}; }'''
def _tally(pg):
    pg.evaluate("()=>{ __T.placeAt('k4','m03'); startSession('k4','m03',false,true); }")
    assert pg.evaluate("VIEW.stage") == 'check' and pg.evaluate("findSession('k4','m03').session.check[0].t") == 'tally'

@check
def tally_row_rules(pg):
    _tally(pg)
    cases = [
        ('blank optional row is skipped', [['Red', 4], ['Blue', 7], ['', '']], True),
        ('name without a count', [['Red', 4], ['Blue', 7], ['Green', '']], False),
        ('count without a name', [['Red', 4], ['Blue', 7], ['', 3]], False),
        ('negative count', [['Red', 4], ['Blue', 7], ['Green', -1]], False),
        ('fractional count', [['Red', 4], ['Blue', 1.5]], False),
        ('count over 500', [['Red', 4], ['Blue', 501]], False),
        ('boundary 0 and 500', [['Red', 0], ['Blue', 500]], True),
    ]
    for name, rows, want in cases:
        r = pg.evaluate(DRAW, rows)
        good = r['graph'] == want and (want or (r['msg'] and r['focus']))
        ok('tally: ' + name + (' draws' if want else ' is refused, with the row named and focused'), good, r)

@check
def tally_edit_after_draw(pg):
    _tally(pg)
    r = pg.evaluate(DRAW, [['Red', 4], ['Blue', 7]])
    gone = pg.evaluate(r'''() => { const e = document.querySelector('#app .item'); const c = e.querySelectorAll('.tally-grid input')[3]; c.value = '9'; c.dispatchEvent(new Event('input', {bubbles:true})); return !e.querySelector('.fig') && !e.querySelector('select'); }''')
    ok('tally: editing a count after drawing removes the old graph and questions', r['graph'] and gone)
    r2 = pg.evaluate(DRAW, [['Red', 4], ['Blue', 9]])
    res = pg.evaluate(r'''async () => { const e = document.querySelector('#app .item'); const sel = e.querySelector('select'), tot = e.querySelector('input[id^="tt-"]'), chk = [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Check');
      sel.value = '1'; tot.value = '11'; chk.click(); const oldTotalRefused = !VIEW.results.a;
      tot.value = '13'; chk.click(); await __T.sleep(10);
      const bars = [...e.querySelectorAll('.fig rect.mark')].map(r=>+r.getAttribute('height'));
      const w = JSON.parse(localStorage.getItem('datalab:wip:k4'));
      return {oldTotalRefused, accepted: !!VIEW.results.a, saved: w.drafts.a.vals, bars}; }''')
    ok('tally: the check grades, plots and saves the same counts', r2['graph'] and res['oldTotalRefused'] and res['accepted'] and res['saved'] == [4, 9] and len(res['bars']) == 2 and abs(res['bars'][1] / res['bars'][0] - 9 / 4) < 0.01, res)

@check
def tally_tie_either(pg):
    _tally(pg)
    pg.evaluate(DRAW, [['Red', 5], ['Blue', 5]])
    r = pg.evaluate(r'''() => { const e = document.querySelector('#app .item'); e.querySelector('select').value = '0'; e.querySelector('input[id^="tt-"]').value = '10'; [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Check').click(); return !!VIEW.results.a; }''')
    ok('tally: either tied maximum is accepted', r)

# ---------------------------------------------------------------- 5. grader (P2)
@check
def grader_parsing(pg):
    r = pg.evaluate(r'''async () => { AI.GRADE_MS = 300; const item = {q:'Q', rubric:'R'}, out = {};
      const cases = {true_:JSON.stringify({ok:true, fb:'Good.'}), false_:JSON.stringify({ok:false, fb:'Add a reason.'}), string_false:JSON.stringify({ok:'false', fb:'Try again'}),
        missing_ok:JSON.stringify({fb:'Hi'}), missing_fb:JSON.stringify({ok:true}), malformed:'{ok: true, fb: nope', no_json:'Looks great!'};
      for(const [k,t] of Object.entries(cases)){ AI.sample = async () => ({text:t}); out[k] = await AI.grade('k7', item, 'answer'); }
      AI.sample = () => new Promise(()=>{}); const t0 = Date.now(); out.never = await Promise.race([AI.grade('k7', item, 'answer'), __T.sleep(3000).then(()=>'still waiting after 3 s')]); out.waited = Date.now()-t0;
      return out; }''')
    good = r['true_'] == {'ok': True, 'fb': 'Good.'} and r['false_'] == {'ok': False, 'fb': 'Add a reason.'} and all(r[k] is None for k in ('string_false', 'missing_ok', 'missing_fb', 'malformed', 'no_json', 'never')) and r['waited'] < 1500
    ok('grader: only a boolean ok and a text fb count; everything else, including a hang, goes to a parent', good, r)

def _grade_flow(pg, sample_js):
    return pg.evaluate(r'''async ([SOLVE, sample]) => { AI.GRADE_MS = 300; AI.sample = (0,eval)(sample);
      __T.placeAt('k7','s02'); startSession('k7','s02'); __T.toCheck();
      if(await (0,eval)('('+SOLVE+')')('right') !== 'ok') return {err:'solve'};
      await __T.sleep(500);
      const fin = document.querySelector('#app button.primary'); if(fin.disabled) return {err:'finish stuck'};
      fin.click(); await __T.sleep(30);
      Store.get('parent').code = '1234'; Store.save('parent'); go({name:'parent'}); parentOpen = true; render();
      const pill = [...document.querySelectorAll('#app .item .pill')].map(p=>p.textContent)[0];
      return {ok: Store.get('k7').ans.s02.b.ok, pill}; }''', [SOLVE, sample_js])

@check
def grader_flow_string_false(pg):
    r = _grade_flow(pg, "async () => ({text: JSON.stringify({ok:'false', fb:'Try again.'})})")
    ok('grader: a malformed verdict is stored unchecked and Parent view says "Not checked"', r.get('ok') is None and r.get('pill') == 'Not checked', r)

@check
def grader_flow_hang(pg):
    r = _grade_flow(pg, "() => new Promise(()=>{})")
    ok('grader: a request that never settles still lets the kid finish', r.get('ok') is None and r.get('pill') == 'Not checked', r)

@check
def grader_flow_pass(pg):
    r = _grade_flow(pg, "async () => ({text: JSON.stringify({ok:true, fb:'Nice work.'})})")
    ok('grader: a real pass is stored and shown as a pass', r.get('ok') is True and r.get('pill') == 'Coach: meets it', r)

# ---------------------------------------------------------------- 6. s11 data (P2)
REACT_IN = r'''async (sel) => { const e = document.querySelector(sel); e.querySelector('.chips button').click();
  for(let h=0;h<2;h++){ for(let n=0;n<8;n++){ for(let w=0;w<300;w++){ const p=e.querySelector('.reactpad'); if(p && p.classList.contains('go')){ await __T.sleep(5+Math.random()*20); p.click(); break; } await __T.sleep(10); } await __T.sleep(5); }
    if(h===0){ await __T.sleep(20); [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Ready').click(); } }
  await __T.sleep(30); const m = /right hand: ([\d.]+) ms\. Middle time, left hand: ([\d.]+) ms/.exec(e.textContent); if(!m) return 'no result';
  e.querySelector('select').value = +m[1] < +m[2] ? 'right' : +m[2] < +m[1] ? 'left' : 'tie'; [...e.querySelectorAll('button.second')].find(b=>b.textContent==='Check').click(); return 'ok'; }'''

@check
def s11_after_test_out(pg):
    pg.evaluate(r'''() => { const u = unitsOf('k7')[0], g = gateState('k7', u); Store.get('k7').gates[u.gate.id] = {quiz:{best:g.n, last:g.n, n:g.n, t:1, d:'2026-01-05', tries:1, missed:[]}};
      for(const s of unitsOf('k7')[1].sessions){ if(s.id==='s11') break; Store.get('k7').done[s.id] = {t:1, first:0, auto:0, mins:1}; } Store.save('k7'); }''')
    before = pg.evaluate("(()=>{const c=counts('k7'); return [c.total, c.skipped]})()")
    pg.evaluate("startSession('k7','s11')")
    shown = pg.evaluate("[VIEW.stage, !!document.querySelector('#collect'), (document.querySelector('ol.steps')||{}).textContent||'']")
    ok('s11 after a test-out: the page offers the reaction-time test in place', shown[0] == 'task' and shown[1] and 'do the reaction-time test below first' in shown[2], shown)
    ran = pg.evaluate(REACT_IN, '#collect .item'); pg.wait_for_timeout(1500)
    r = pg.evaluate(r'''() => { const st = Store.get('k7'), c = counts('k7'); return {right:(st.ans.s01&&st.ans.s01.a&&st.ans.s01.a.right||[]).length, s01done:!!st.done.s01, counts:[c.total, c.skipped], listed: /Your reaction times/.test(document.querySelector('#app').textContent), collectGone: !document.querySelector('#collect')}; }''')
    ok('s11 after a test-out: the times are stored for s11, listed, and no session credit is given', ran == 'ok' and r['right'] == 8 and not r['s01done'] and r['counts'] == before and r['listed'] and r['collectGone'], [ran, r, before])
    q = pg.evaluate("findSession('k7','s11').session.check[0]")
    ok('s11: the written question and rubric accept the log or the reaction times', "each hand" in q['q'] and 'Log' in q['q'] and 'Accept either kind' in q['rubric'], q['q'])

@check
def s11_with_stored_times(pg):
    r = pg.evaluate(r'''() => { __T.placeAt('k7','s11'); Store.get('k7').ans.s01 = {a:{right:[250,260,270], left:[300,310,320], predict:'My right hand', mr:260, ml:310}}; Store.save('k7');
      startSession('k7','s11'); if(VIEW.stage==='warm'){ VIEW.stage='task'; render(); }
      return {collect: !!document.querySelector('#collect'), listed: /Right: 250, 260, 270/.test(document.querySelector('#app').textContent), predict: /Your prediction before the test: My right hand/.test(document.querySelector('#app').textContent)}; }''')
    ok('s11 with stored reaction times: they and the prediction are listed, and no extra test is offered', not r['collect'] and r['listed'] and r['predict'], r)

@check
def s11_tryout_saves_nothing(pg):
    before = pg.evaluate("JSON.stringify([Store.get('k7'), Object.keys(localStorage).sort()])")
    pg.evaluate("startSession('k7','s11',true,false,{tryout:true})")
    has = pg.evaluate("!!document.querySelector('#collect')")
    ran = pg.evaluate(REACT_IN, '#collect .item'); pg.wait_for_timeout(1500)
    after = pg.evaluate("JSON.stringify([Store.get('k7'), Object.keys(localStorage).sort()])")
    ok('s11 in tryout: the in-place test runs and saves nothing', has and ran == 'ok' and before == after, [has, ran])

# ---------------------------------------------------------------- 7. log (P2)
@check
def log_one_session_two_dates(pg):
    r = pg.evaluate(r'''() => { const mon = weekStart(today()), sun = addDays(mon, -1);
      const a = Store.blank(), b = Store.blank(); a.done.s01 = {t:1}; b.done.s01 = {t:2}; a.log = [{d:sun, sid:'s01'}]; b.log = [{d:mon, sid:'s01'}];
      const m = [Store.merge(a,b), Store.merge(b,a)].map(x=>JSON.stringify(x.log));
      Store.adopt('k7', Store.merge(a,b)); Store.get('k7').log = [{d:mon, sid:'s01'}, {d:sun, sid:'s01'}];   // an older, un-normalized log too
      const c = counts('k7');
      Store.get('parent').code = '1234'; go({name:'parent'}); parentOpen = true; render();
      const kpi = [...document.querySelectorAll('#app .kpi')].filter(k=>/last 4 weeks/.test(k.textContent)).map(k=>k.querySelector('b').textContent);
      return {m, sun, total:c.total, weekN:c.weekN, kpi}; }''')
    ok('log: one session finished Sunday and Monday counts once, in the earlier week', r['m'][0] == r['m'][1] and json.loads(r['m'][0]) == [{'d': r['sun'], 'sid': 's01'}] and r['total'] == 1 and r['weekN'] == 0 and r['kpi'][0] == '1', r)

@check
def log_distinct_sessions_and_reviews(pg):
    r = pg.evaluate(r'''() => { const mon = weekStart(today()), tue = addDays(mon, 1);
      const a = Store.blank(), b = Store.blank(); a.done.s01 = {t:1}; b.done.s02 = {t:2};
      a.log = [{d:mon, sid:'s01'}, {d:mon, sid:'review'}]; b.log = [{d:mon, sid:'s02'}, {d:tue, sid:'review'}, {d:mon, sid:'review'}];
      const m = Store.merge(a, b); Store.adopt('k7', m); const c = counts('k7');
      return {n: m.log.length, sessions: m.log.filter(e=>e.sid!=='review').length, reviews: m.log.filter(e=>e.sid==='review').length, weekN: c.weekN}; }''')
    ok('log: two sessions on one day both count, and one review per day is kept', r == {'n': 4, 'sessions': 2, 'reviews': 2, 'weekN': 2}, r)

# ---------------------------------------------------------------- 8. select tap targets (P2)
@check
def select_heights(pg):
    _tally(pg)
    pg.evaluate(DRAW, [['Red', 4], ['Blue', 7]])
    tally = pg.evaluate("(()=>{const s=document.querySelector('#app select'); const r=s.getBoundingClientRect(); return [Math.round(r.height), parseFloat(getComputedStyle(s).fontSize)]})()")
    pg.evaluate("startSession('k7','s01',true,false,{tryout:true}); VIEW.stage='check'; render();")
    pg.evaluate(REACT_IN, '#app .item')
    react = pg.evaluate("(()=>{const s=document.querySelector('#app select'); const r=s.getBoundingClientRect(); return [Math.round(r.height), parseFloat(getComputedStyle(s).fontSize)]})()")
    overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    ok('selects: tally and reaction-time selects are at least 44 px high with 16 px text, no sideways scroll at 390 px', tally[0] >= 44 and react[0] >= 44 and tally[1] >= 16 and react[1] >= 16 and overflow <= 0, [tally, react, overflow])


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        page_errors = []
        for fn in CHECKS:
            if ONLY and ONLY not in fn.__name__: continue
            ctx, pg, errs = page(b)
            try: fn(pg)
            except Exception as e: ok(fn.__name__ + ' (crashed)', False, repr(e))
            page_errors += [fn.__name__ + ': ' + e for e in errs]
            ctx.close()
        b.close()
    ok('no page errors', not page_errors, page_errors)
    failed = [n for n, c in results if not c]
    print(f'{len(results) - len(failed)} passed, {len(failed)} failed')
    print('FAILED:', failed)
    sys.exit(1 if failed else 0)

if __name__ == '__main__':
    main()
