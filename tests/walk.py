import json, sys
from playwright.sync_api import sync_playwright
import os
URL=os.environ.get('U','file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')))
SOLVE = r'''
async (mode) => {
  const sleep = ms => new Promise(r=>setTimeout(r,ms));
  const v = VIEW; let items;
  if(v.name==="session" && v.stage==="warm") items = v.warm.map(w=>w.item);
  else if(v.name==="session" && v.stage==="check") items = findSession(v.kid, v.sid).session.check;
  else if(v.name==="gate" && v.quiz) items = v.quiz.items.map(i=>i.item);
  else return "no-items:"+v.name+":"+(v.stage||"");
  const els = [...document.querySelectorAll("#app .item")];
  if(els.length !== items.length) return "count-mismatch "+els.length+" vs "+items.length;
  for(let i=0;i<items.length;i++){
    const it = items[i], e = els[i];
    if(it.t==="mc"){ const want = mode==="wrong" ? it.opts[(it.a+1)%it.opts.length] : it.opts[it.a]; const b=[...e.querySelectorAll(".opts button")].find(x=>x.textContent===want); if(!b) return "mc-missing "+it.q; b.click(); if(mode==="wrong" && !(v.name==="gate"||v.stage==="warm")){ [...e.querySelectorAll(".opts button")].find(x=>x.textContent===it.opts[it.a]).click(); } }
    else if(it.t==="num"){ const inp=e.querySelector("input[type=number]"); inp.value=String(it.a); e.querySelector("button.second").click(); }
    else if(it.t==="txt"){ e.querySelector("textarea").value = "I asked which kind there was most of and I found that blue had the most with 7. I wonder if that would change next week if I counted again in a different room of the house, and how the graph would look then."; e.querySelector("button.second").click(); await sleep(30); }
    else if(it.t==="pick"){ e.querySelector(".chips button").click(); e.querySelector("button.second").click(); }
    else if(it.t==="tally"){ const g=e.querySelector('input[id^="tg-"]'); if(g) g.value="Blue"; const ins=[...e.querySelectorAll(".tally-grid input")]; const d=[["Red",4],["Blue",7],["Green",2]]; d.forEach((r,k)=>{ ins[k*2].value=r[0]; ins[k*2+1].value=String(r[1]); }); [...e.querySelectorAll("button.second")].find(b=>b.textContent==="Draw my graph").click(); await sleep(10); e.querySelector("select").value="1"; e.querySelector('input[id^="tt-"]').value="13"; [...e.querySelectorAll("button.second")].find(b=>b.textContent==="Check").click(); }
    else if(it.t==="react"){ window.__FAST=true; e.querySelector(".chips button").click();
      for(let h=0;h<2;h++){ for(let n=0;n<8;n++){ for(let w=0;w<300;w++){ const p=e.querySelector(".reactpad"); if(p && p.classList.contains("go")){ await sleep(5+Math.random()*25); p.click(); break; } await sleep(10); } await sleep(5); }
        if(h===0){ await sleep(20); [...e.querySelectorAll("button.second")].find(b=>b.textContent==="Ready").click(); } }
      await sleep(30); const m=/right hand: ([\d.]+) ms\. Middle time, left hand: ([\d.]+) ms/.exec(e.textContent); if(!m) return "react-no-result"; const mr=+m[1], ml=+m[2]; e.querySelector("select").value = mr<ml?"right":ml<mr?"left":"tie"; [...e.querySelectorAll("button.second")].find(b=>b.textContent==="Check").click(); }
  }
  await sleep(20);
  return "ok";
}
'''
errors=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME','/usr/bin/google-chrome'), args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':820,'height':1100})
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append('console:'+m.text) if m.type=='error' else None)
    pg.goto(URL); pg.wait_for_timeout(400)
    pg.screenshot(path='home.png', full_page=True)
    log=[]
    for kid in ['k4','k7']:
        pg.evaluate("k=>go({name:'kid',kid:k})", kid); pg.wait_for_timeout(50)
        if kid=='k4': pg.screenshot(path='kid_k4_start.png', full_page=True)
        for step in range(80):
            pos = pg.evaluate("k=>{const p=position(k); return {kind:p.kind, id:p.session?p.session.id:(p.unit?p.unit.id:null)}}", kid)
            if pos['kind']=='end': log.append((kid,'END',pos['id'])); break
            if pos['kind']=='session':
                pg.click('button.primary'); pg.wait_for_timeout(30)
                st = pg.evaluate("VIEW.stage")
                if st=='warm':
                    r=pg.evaluate(SOLVE,'right'); assert r=='ok', r
                    pg.click('button.primary'); pg.wait_for_timeout(30)
                assert pg.evaluate("VIEW.stage")=='task', pg.evaluate("VIEW.stage")
                bad=pg.evaluate("(()=>{const t=document.body.innerText; const m=t.match(/(^|\\n)\\s*(null|undefined|NaN)\\s*(\\n|$)|\\[object /); return m?m[0]:''})()"); assert not bad, ('stray text in task', pos, bad)
                if pos['id'] in ('s05',): pg.screenshot(path=f"task_{pos['id']}.png", full_page=True)
                for _ in range(8):
                    if pg.evaluate("VIEW.stage")!='task': break
                    pg.click('button.primary'); pg.wait_for_timeout(30)
                r=pg.evaluate(SOLVE, 'wrong' if pos['id'] in ('m02','s04') else 'right'); assert r=='ok', (pos, r)
                if pos['id'] in ('m01','s01'): pg.screenshot(path=f"check_{pos['id']}.png", full_page=True)
                bad=pg.evaluate("(()=>{const t=document.body.innerText; const m=t.match(/(^|\\n)\\s*(null|undefined|NaN)\\s*(\\n|$)|\\[object /); return m?m[0]:''})()"); assert not bad, ('stray text in check', pos, bad)
                dis = pg.evaluate("document.querySelector('#app button.primary').disabled"); assert not dis, ('finish disabled', pos)
                pg.click('button.primary'); pg.wait_for_timeout(30)
                assert pg.evaluate("VIEW.stage")=='done'
                # age the review items so warm-ups appear next time
                pg.evaluate("k=>{const st=Store.get(k); for(const r of Object.values(st.rev)) r.due='2020-01-01';}", kid)
                pg.evaluate("k=>go({name:'kid',kid:k})", kid); pg.wait_for_timeout(20)
                log.append((kid,'session',pos['id']))
            elif pos['kind']=='gate':
                pg.click('button.primary'); pg.wait_for_timeout(30)   # open the gate
                try:
                    pg.click('button.primary', timeout=3000); pg.wait_for_timeout(30)   # start quiz
                except Exception as e:
                    print('FAIL at', pos, log[-3:]); print(pg.evaluate("JSON.stringify(VIEW).slice(0,300)")); print(pg.evaluate("document.getElementById('app').innerText.slice(0,500)")); print(errors); raise
                r=pg.evaluate(SOLVE,'right'); assert r=='ok', r
                pg.click('button.primary'); pg.wait_for_timeout(30)   # score
                gs=pg.evaluate("([k,u])=>{const un=unitsOf(k).find(x=>x.id===u); return gateState(k,un)}", [kid,pos['id']])
                log.append((kid,'gate',pos['id'], gs['gs'].get('quiz',{}).get('best'), gs['n'], gs['quizOk'], gs['prodOk']))
                if not gs['prodOk']:
                    pg.evaluate("go({name:'parent'})"); pg.wait_for_timeout(30)
                    if pg.query_selector('#pcode'):
                        pg.fill('#pcode','1234'); pg.click('button.primary'); pg.wait_for_timeout(30)
                    if kid=='k4': pg.screenshot(path='parent.png', full_page=True)
                    for cb in pg.query_selector_all(f"input[id^='rb-g-{pos['id']}']"): cb.check()
                    btns=[x for x in pg.query_selector_all('button.second') if x.inner_text()=='Sign off']
                    btns[-1 if kid=='k4' else 0].click(); pg.wait_for_timeout(30)
                pg.evaluate("k=>go({name:'kid',kid:k})", kid); pg.wait_for_timeout(20)
        pg.screenshot(path=f'kid_{kid}_end.png', full_page=True)
        pg.evaluate("k=>go({name:'path',kid:k})", kid); pg.wait_for_timeout(30); pg.screenshot(path=f'path_{kid}.png', full_page=True)
    # persistence across reload (device storage)
    pg.reload(); pg.wait_for_timeout(400)
    tot = pg.evaluate("[counts('k7').total, counts('k4').total, counts('k7').authored, counts('k4').authored, Store.mode]")
    # test-out path on a fresh profile
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("go({name:'gate',kid:'k7',gid:'g-s1a'})"); pg.wait_for_timeout(30)
    pg.click('button.primary'); pg.wait_for_timeout(30); r=pg.evaluate(SOLVE,'right'); pg.click('button.primary'); pg.wait_for_timeout(30)
    skip = pg.evaluate("(()=>{const p=position('k7'); const c=counts('k7'); return [p.kind, p.session&&p.session.id, c.total, c.skipped]})()")
    # merge checks
    mg = pg.evaluate('''(()=>{ const a=Store.blank(), b=Store.blank(); a.done.s01={t:5,first:1,auto:1}; a.log.push({d:'2026-11-10',sid:'s01'}); a.stats.fn=3; a.ts=10; b.done.s02={t:7,first:0,auto:1}; b.log.push({d:'2026-11-10',sid:'s01'}); b.log.push({d:'2026-11-11',sid:'s02'}); b.stats.rn=3; b.gates['g']={quiz:{best:8,t:3,tries:2}}; a.gates['g']={quiz:{best:9,t:2,tries:1}}; b.ts=12; const m=Store.merge(a,b); return [Object.keys(m.done).length, m.log.length, m.stats.fn, m.stats.rn, m.gates.g.quiz.best, m.gates.g.quiz.tries, m.ts]; })()''')
    print('merge:', mg)
    ep = pg.evaluate('''(()=>{ const a=Store.blank(), b=Store.blank(); a.done.s01={t:5}; a.ts=10; b.epoch=1; b.ts=11; const m=Store.merge(a,b); const m2=Store.merge(b,a); Store.get('k4').done.m01={t:1,first:1,auto:1}; Store.get('k4').log.push({d:today(),sid:'m01'}); Store.save('k4'); const before=counts('k4').total; Store.reset('k4'); return [Object.keys(m.done).length, m.epoch, Object.keys(m2.done).length, before, counts('k4').total, Store.get('k4').epoch, JSON.parse(localStorage.getItem('datalab:k4')).epoch]; })()''')
    print('epoch/reset:', ep)
    pg.emulate_media(color_scheme='dark'); pg.evaluate("go({name:'kid',kid:'k7'})"); pg.wait_for_timeout(50); pg.screenshot(path='dark_k7.png', full_page=True)
    b.close()
for l in log: print(l)
print('after reload totals:', tot); print('test-out:', r, skip); print('ERRORS:', errors)
