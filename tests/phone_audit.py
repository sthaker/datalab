import os
"""Phone usability audit: WebKit + iPhone 13 profile, dark pass (real timing, all taps) and light pass (__FAST, SOLVE).
Report-only: never modifies the app. Output: phone_audit_report.json + phone_shots/*.png + stdout summary."""
import json, os, re, sys, time, collections
from playwright.sync_api import sync_playwright

URL = os.environ.get('U', 'file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')))
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, 'phone_shots'); os.makedirs(SHOTS, exist_ok=True)

# --- copied verbatim from walk.py -------------------------------------------------------------
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

# --- in-page audit of the current screen --------------------------------------------------------
AUDIT = r'''
() => {
  const VW = document.documentElement.clientWidth, VH = window.innerHeight;
  const out = {stray:[], overflow:[], taps:[], fonts:[], clip:[], contrast:[], figs:[], titleRow:null, svgText:[], meta:{}};
  const vis = e => { const r = e.getBoundingClientRect(); if(r.width<=0 || r.height<=0) return false; const cs = getComputedStyle(e); return cs.visibility!=="hidden" && cs.display!=="none" && +cs.opacity>0; };
  const sig = e => e.tagName.toLowerCase() + (e.getAttribute("class") ? "."+String(e.getAttribute("class")).trim().split(/\s+/).join(".") : "");
  const snip = e => (e.innerText||e.textContent||e.getAttribute("aria-label")||e.getAttribute("placeholder")||e.id||"").trim().replace(/\s+/g," ").slice(0,60);
  const lab = e => (e.innerText||"").trim().replace(/\s+/g," ").slice(0,50) || e.getAttribute("aria-label") || e.getAttribute("placeholder") || e.id || e.type || "";
  // 1 stray text
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for(let n; (n = tw.nextNode()); ){ const p = n.parentElement; if(!p || /^(SCRIPT|STYLE)$/.test(p.tagName)) continue; const t = n.nodeValue.trim(); if(/^(null|undefined|NaN)$/.test(t) || t.includes("[object")) out.stray.push({text:t.slice(0,60), in:sig(p), ctx:snip(p.parentElement||p)}); }
  for(const e of document.querySelectorAll("input,textarea,select,[placeholder],[aria-label],[title]")) for(const a of ["value","placeholder","aria-label","title"]){ const val = a==="value" ? e.value : e.getAttribute(a); if(val!=null && (/^(null|undefined|NaN)$/.test(String(val).trim()) || String(val).includes("[object"))) out.stray.push({text:a+"="+val, in:sig(e), ctx:""}); }
  // 2 overflow
  out.meta.docOverflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  out.meta.bodyOverflow = document.body.scrollWidth - document.body.clientWidth;
  const scroller = e => { for(let p = e.parentElement; p && p!==document.body; p = p.parentElement){ const ox = getComputedStyle(p).overflowX; if(ox==="auto"||ox==="scroll"||ox==="hidden"||ox==="clip") return sig(p)+"["+ox+"]"; } return null; };
  for(const e of document.body.querySelectorAll("*")){
    if(e.closest("svg") && e.tagName.toLowerCase()!=="svg") continue;
    if(!vis(e)) continue; const r = e.getBoundingClientRect();
    if(r.right > VW + 1 || r.left < -1) out.overflow.push({el:sig(e), text:snip(e), left:Math.round(r.left), right:Math.round(r.right), vw:VW, inside:scroller(e)});
  }
  // 3 tap targets, 4 font sizes
  for(const e of document.querySelectorAll("button,a[href],select,input,textarea,summary,label[for]")){
    if(!vis(e)) continue; const r = e.getBoundingClientRect(), tag = e.tagName.toLowerCase();
    if(tag!=="label" && (r.height < 40 || r.width < 40)) out.taps.push({el:sig(e)+(e.type&&tag==="input"?"["+e.type+"]":""), label:lab(e), w:Math.round(r.width), h:Math.round(r.height)});
    if(/^(input|select|textarea)$/.test(tag) && !/^(checkbox|radio)$/.test(e.type||"")){ const fs = parseFloat(getComputedStyle(e).fontSize); if(fs < 16) out.fonts.push({el:sig(e)+"["+(e.type||tag)+"]", label:lab(e), fs}); }
  }
  // 5 clipping / title row / figures
  for(const e of document.body.querySelectorAll("*")){
    if(e.closest("svg")) continue; if(!vis(e)) continue; const cs = getComputedStyle(e);
    if(e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0){
      const ox = cs.overflowX;
      if(ox==="hidden"||ox==="clip") out.clip.push({el:sig(e), text:snip(e), sw:e.scrollWidth, cw:e.clientWidth, kind:"clipped("+ox+")"});
      else if(ox==="auto"||ox==="scroll") out.clip.push({el:sig(e), text:snip(e), sw:e.scrollWidth, cw:e.clientWidth, kind:"h-scroll("+ox+")"});
      else if(/^(input|select)$/i.test(e.tagName)) out.clip.push({el:sig(e)+"["+(e.type||"")+"]", text:"value/placeholder: "+(e.value||e.getAttribute("placeholder")||""), sw:e.scrollWidth, cw:e.clientWidth, kind:"field-text-wider-than-field"});
    }
  }
  for(const e of document.querySelectorAll("input[placeholder]")){ if(!vis(e) || e.value) continue; const c = document.createElement("canvas").getContext("2d"); const cs = getComputedStyle(e); c.font = cs.fontWeight+" "+cs.fontSize+" "+cs.fontFamily; const w = c.measureText(e.getAttribute("placeholder")).width; const inner = e.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight); if(w > inner + 1) out.clip.push({el:sig(e)+"["+e.type+"]", text:"placeholder '"+e.getAttribute("placeholder")+"'", sw:Math.round(w), cw:Math.round(inner), kind:"placeholder-cut-off"}); }
  const tm = document.querySelector("#app .timer");
  if(tm){ const h1 = document.querySelector("#app h1"), a = h1.getBoundingClientRect(), b = tm.getBoundingClientRect(), lh = parseFloat(getComputedStyle(h1).lineHeight)||34;
    out.titleRow = {title:h1.textContent, h1Lines:Math.round(a.height/lh), h1Width:Math.round(a.width), timerWrappedBelow: b.top >= a.bottom - 2, timerLeft:Math.round(b.left), timerRight:Math.round(b.right), timerTop:Math.round(b.top), h1Top:Math.round(a.top), h1Bottom:Math.round(a.bottom)}; }
  for(const f of document.querySelectorAll(".fig")){ if(!vis(f)) continue; const s = f.querySelector("svg"); if(!s) continue; const r = s.getBoundingClientRect(), vb = s.viewBox.baseVal, scale = r.width / vb.width;
    let minPx = 99, clipped = 0, overlaps = 0; const boxes = [];
    for(const t of s.querySelectorAll("text")){ const fs = parseFloat(getComputedStyle(t).fontSize) * scale; if(fs < minPx) minPx = fs; const tb = t.getBoundingClientRect(); if(tb.left < r.left - 1 || tb.right > r.right + 1) clipped++; boxes.push({l:tb.left, r:tb.right, t:tb.top, b:tb.bottom, s:t.textContent}); }
    const ov = []; for(let i=0;i<boxes.length;i++) for(let j=i+1;j<boxes.length;j++){ const A = boxes[i], B = boxes[j]; if(A.l < B.r - 1 && B.l < A.r - 1 && A.t < B.b - 1 && B.t < A.b - 1){ overlaps++; if(ov.length<3) ov.push(A.s+" | "+B.s); } }
    out.figs.push({label:s.getAttribute("aria-label"), svgW:Math.round(r.width), figW:f.clientWidth, widerThanContainer: r.width > f.clientWidth + 1, scroll: f.scrollWidth > f.clientWidth + 1, scale:+scale.toFixed(2), minTextPx:+minPx.toFixed(1), labelsOutsideSvg:clipped, labelOverlaps:overlaps, overlapEx:ov}); }
  // 6 contrast
  const parse = c => { const m = /rgba?\(([^)]+)\)/.exec(c); if(!m) return null; const p = m[1].split(/[ ,\/]+/).map(parseFloat); return {r:p[0], g:p[1], b:p[2], a: p.length>3 ? p[3] : 1}; };
  const over = (f, b) => ({r:f.r*f.a + b.r*(1-f.a), g:f.g*f.a + b.g*(1-f.a), b:f.b*f.a + b.b*(1-f.a), a:1});
  const lum = c => { const f = v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); };
  const hex = c => "#"+[c.r,c.g,c.b].map(v=>Math.round(v).toString(16).padStart(2,"0")).join("");
  const bgOf = e => { const layers = []; let op = 1; for(let p = e; p; p = p.parentElement){ const cs = getComputedStyle(p); op *= +cs.opacity; const c = parse(cs.backgroundColor); if(c && c.a > 0){ layers.push(c); if(c.a >= 1) break; } }
    let base = {r:255,g:255,b:255,a:1}; for(let i = layers.length-1; i>=0; i--) base = over(layers[i], base); return {bg:base, op}; };
  const seen = new Set();
  for(const e of document.body.querySelectorAll("*")){
    if(/^(SCRIPT|STYLE)$/.test(e.tagName)) continue;
    const isSvgText = e.tagName.toLowerCase()==="text";
    if(e.closest("svg") && !isSvgText) continue;
    let own = isSvgText ? e.textContent.trim() : [...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.nodeValue).join("").trim();
    if(/^(INPUT|TEXTAREA)$/.test(e.tagName) && e.value) own = e.value; if(e.tagName==="SELECT") own = e.options[e.selectedIndex] ? e.options[e.selectedIndex].text : "";
    if(!own || !vis(e)) continue;
    const cs = getComputedStyle(e); let fg = parse(isSvgText ? cs.fill : cs.color); if(!fg) continue;
    const {bg, op} = bgOf(isSvgText ? e.closest(".fig")||e.parentElement : e); let fgc = over(fg, bg), bgc = bg;
    if(op < 1 && !isSvgText){ let host = e; while(host.parentElement && +getComputedStyle(host).opacity >= 1) host = host.parentElement; const back = bgOf(host.parentElement||host).bg; fgc = over(Object.assign({}, fgc, {a:op}), back); bgc = over(Object.assign({}, bg, {a:op}), back); }
    const cr = ratio(fgc, bgc); const fs = parseFloat(cs.fontSize) * (isSvgText ? e.closest("svg").getBoundingClientRect().width / e.closest("svg").viewBox.baseVal.width : 1), bold = parseInt(cs.fontWeight,10) >= 700;
    if(cr < 4.5){ const key = sig(e)+"|"+hex(fgc)+"|"+hex(bgc)+(e.disabled?"|disabled":""); if(seen.has(key)) continue; seen.add(key);
      out.contrast.push({el:sig(e)+(e.disabled?"[disabled]":""), text:own.replace(/\s+/g," ").slice(0,40), fg:hex(fgc), bg:hex(bgc), ratio:+cr.toFixed(2), fontPx:+fs.toFixed(1), bold, large: fs>=24 || (bold && fs>=18.66)}); }
  }
  // placeholder contrast
  for(const e of document.querySelectorAll("input[placeholder],textarea[placeholder]")){ if(!vis(e) || e.value) continue; const pc = parse(getComputedStyle(e, "::placeholder").color); if(!pc) continue; const {bg} = bgOf(e); const cr = ratio(over(pc,bg), bg); if(cr < 4.5){ const key = "ph|"+hex(over(pc,bg))+"|"+hex(bg); if(seen.has(key)) continue; seen.add(key); out.contrast.push({el:sig(e)+"::placeholder", text:e.getAttribute("placeholder"), fg:hex(over(pc,bg)), bg:hex(bg), ratio:+cr.toFixed(2), fontPx:parseFloat(getComputedStyle(e).fontSize), bold:false, large:false}); } }
  // meta: primary action placement, fonts, scheme
  const pb = document.querySelector("#app button.primary");
  if(pb){ const r = pb.getBoundingClientRect(); out.meta.primary = {label:pb.textContent, disabled:pb.disabled, pageY:Math.round(r.top + scrollY), inViewport: r.top >= 0 && r.bottom <= VH, w:Math.round(r.width), h:Math.round(r.height)}; }
  out.meta.primaryCount = document.querySelectorAll("#app button.primary").length;
  out.meta.docH = document.documentElement.scrollHeight; out.meta.vw = VW; out.meta.vh = VH; out.meta.scrollY = Math.round(scrollY);
  out.meta.bodyFont = getComputedStyle(document.body).fontFamily; const ff = [...document.fonts]; out.meta.lexend = ff.some(f=>/Lexend/.test(f.family) && f.status==="loaded"); out.meta.brico = ff.some(f=>/Bricolage/.test(f.family) && f.status==="loaded"); out.meta.fontFaces = ff.length;
  out.meta.dark = matchMedia("(prefers-color-scheme: dark)").matches;
  out.meta.small = [...new Set([...document.querySelectorAll("#app *")].filter(e=>!e.closest("svg") && vis(e) && [...e.childNodes].some(n=>n.nodeType===3 && n.nodeValue.trim()) && parseFloat(getComputedStyle(e).fontSize) < 13).map(e=>sig(e)+"@"+parseFloat(getComputedStyle(e).fontSize)+"px"))];
  out.meta.text = document.getElementById("app").innerText;
  return out;
}
'''
STATE = "() => JSON.stringify([VIEW.name, VIEW.stage||'', VIEW.stepIdx==null?'':VIEW.stepIdx, VIEW.kid||'', VIEW.sid||'', !!VIEW.quiz, !!VIEW.justScored, document.getElementById('app').innerText.length, document.getElementById('app').innerText.slice(0,400), [...document.querySelectorAll('#app [aria-pressed=true], #app .right, #app .wrong, #app :disabled, #app :checked, #app details[open]')].length])"
ITEMS = r'''() => { const v = VIEW; let items;
  if(v.name==="session" && v.stage==="warm") items = v.warm.map(w=>w.item);
  else if(v.name==="session" && v.stage==="check") items = findSession(v.kid, v.sid).session.check;
  else if(v.name==="gate" && v.quiz) items = v.quiz.items.map(i=>i.item); else return null;
  return items.map(it=>({t:it.t, a:it.a, opts:it.opts||null, q:it.q, predict:!!it.predict})); }'''
TXT = "I asked which kind there was most of and I found that blue had the most with 7. I wonder if that would change next week if I counted again in a different room of the house, and how the graph would look then."


class Pass:
    def __init__(self, pw, scheme, fast, use_solve, names):
        self.scheme, self.fast, self.use_solve, self.names = scheme, fast, use_solve, names
        self.findings = collections.OrderedDict()   # (cat, key) -> {detail, screens}
        self.errors, self.noadvance, self.log, self.copy, self.metas, self.react = [], [], [], {}, {}, {}
        self.browser = pw.webkit.launch()
        dev = dict(pw.devices['iPhone 13'])
        self.ctx = self.browser.new_context(**dev, color_scheme=scheme)
        self.pg = self.ctx.new_page()
        self.pg.on('pageerror', lambda e: self.errors.append({'screen': self.cur, 'err': 'pageerror: ' + str(e)}))
        self.pg.on('console', lambda m: self.errors.append({'screen': self.cur, 'err': 'console.' + m.type + ': ' + m.text}) if m.type == 'error' else None)
        self.pg.on('requestfailed', lambda r: self.errors.append({'screen': self.cur, 'err': 'requestfailed: ' + r.url[:90]}))
        self.cur = 'boot'
        self.dev = {k: dev.get(k) for k in ('viewport', 'device_scale_factor', 'has_touch', 'is_mobile')}

    # ---- helpers
    def ev(self, js, arg=None): return self.pg.evaluate(js, arg) if arg is not None else self.pg.evaluate(js)
    def wait(self, ms=60): self.pg.wait_for_timeout(ms)
    def add(self, cat, key, detail):
        f = self.findings.setdefault((cat, key), {'detail': detail, 'screens': []})
        if self.cur not in f['screens']: f['screens'].append(self.cur)

    def shot(self, name, full=True):
        try:
            self.pg.screenshot(path=os.path.join(SHOTS, f'{self.scheme}_{name}.png'), full_page=full)
            if full: self.pg.screenshot(path=os.path.join(SHOTS, f'{self.scheme}_{name}_fold.png'), full_page=False)
        except Exception as e:
            self.errors.append({'screen': self.cur, 'err': 'screenshot failed: ' + str(e)[:120]})

    def audit(self, screen):
        self.cur = screen
        a = self.ev(AUDIT)
        for s in a['stray']: self.add('1 stray text', f"{s['text']}|{s['in']}", s)
        if a['meta']['docOverflow'] > 0: self.add('2 page h-overflow', str(a['meta']['docOverflow']), {'px': a['meta']['docOverflow']})
        for o in a['overflow']: self.add('2 element past viewport edge', f"{o['el']}|{o['text'][:25]}|{o['inside']}", o)
        for t in a['taps']: self.add('3 small tap target', f"{t['el']}|{t['label']}|{t['w']}x{t['h']}", t)
        for f in a['fonts']: self.add('4 field font <16px', f"{f['el']}|{f['fs']}", f)
        for c in a['clip']: self.add('5 clipped/scrolling content', f"{c['el']}|{c['kind']}|{c['text'][:25]}", c)
        if a['titleRow']:
            t = a['titleRow']
            if t['timerWrappedBelow'] or t['h1Lines'] > 2: self.add('5 title row wraps', t['title'], t)
            self.metas.setdefault('titleRows', {})[t['title']] = t
        for f in a['figs']:
            if f['widerThanContainer'] or f['scroll']: self.add('5 figure wider than container', f['label'], f)
            if f['minTextPx'] < 11: self.add('5 figure text shrinks below 11px', f"{f['label']}|{f['minTextPx']}", f)
            if f['labelOverlaps']: self.add('5 figure labels overlap', f"{f['label']}", f)
            if f['labelsOutsideSvg']: self.add('5 figure labels outside svg', f"{f['label']}", f)
        for c in a['contrast']: self.add(f'6 contrast <4.5 ({self.scheme})', f"{c['el']}|{c['fg']}|{c['bg']}", c)
        for s in a['meta']['small']: self.add('x text under 13px', s, {'el': s})
        m = a['meta']; self.copy[screen] = m.pop('text'); self.metas[screen] = m
        return a

    def tap(self, loc, what, expect_change=True, settle=60):
        """Real touch tap. Records a finding if the tap throws or the screen state does not change."""
        before = self.ev(STATE)
        try:
            loc.tap(timeout=4000)
        except Exception as e:
            self.noadvance.append({'screen': self.cur, 'tap': what, 'problem': 'tap() failed: ' + str(e).split('\n')[0][:160]})
            return False
        self.wait(settle)
        if expect_change and self.ev(STATE) == before:
            self.wait(250)
            if self.ev(STATE) == before:
                self.noadvance.append({'screen': self.cur, 'tap': what, 'problem': 'tap changed nothing'})
                return False
        return True

    def primary(self): return self.pg.locator('#app button.primary').first
    def btn(self, text, scope='#app'): return self.pg.locator(f'{scope} button').filter(has_text=re.compile('^' + re.escape(text) + '$')).first
    def stage(self): return self.ev("VIEW.stage||''")

    # ---- answering with real taps
    def solve_taps(self, mode='right', label=''):
        items = self.ev(ITEMS); assert items, 'no items at ' + self.cur
        n = self.pg.locator('#app .item').count(); assert n == len(items), (n, len(items))
        for i, it in enumerate(items):
            e = self.pg.locator('#app .item').nth(i); t = it['t']
            def opt(text):
                bs = e.locator('.opts button')
                for k in range(bs.count()):
                    if bs.nth(k).text_content() == text: return bs.nth(k)
                raise AssertionError('mc option missing: ' + text)
            if t == 'mc':
                if mode == 'wrong':
                    self.tap(opt(it['opts'][(it['a'] + 1) % len(it['opts'])]), 'mc wrong option')
                    if not (self.ev("VIEW.name") == 'gate' or self.stage() == 'warm'): self.tap(opt(it['opts'][it['a']]), 'mc right option after wrong')
                else: self.tap(opt(it['opts'][it['a']]), 'mc option: ' + it['opts'][it['a']][:30])
            elif t == 'num':
                e.locator('input[type=number]').fill(str(it['a'])); self.tap(e.locator('button.second').first, 'num Check')
            elif t == 'txt':
                e.locator('textarea').fill(TXT); self.tap(e.locator('button.second').first, 'txt Submit'); self.wait(80)
            elif t == 'pick':
                self.tap(e.locator('.chips button').first, 'pick chip'); self.tap(e.locator('button.second').first, 'Save my picks')
            elif t == 'tally':
                if e.locator('input[id^="tg-"]').count(): e.locator('input[id^="tg-"]').fill('Blue')
                ins = e.locator('.tally-grid input')
                for k, (nm, ct) in enumerate([('Red', 4), ('Blue', 7), ('Green', 2)]):
                    ins.nth(k * 2).fill(nm); ins.nth(k * 2 + 1).fill(str(ct))
                if label: self.audit(label + ' tally typed'); self.shot(label.replace(' ', '_') + '_tally_typed') if 'm01' in label else None
                self.tap(self.btn('Draw my graph'), 'Draw my graph')
                if label: self.audit(label + ' tally graph drawn')
                e.locator('select').select_option('1'); e.locator('input[id^="tt-"]').fill('13')
                self.tap(self.btn('Check'), 'tally Check')
            elif t == 'react':
                self.react_taps(e, label)

    def react_taps(self, e, label):
        pg = self.pg; info = {'fast': self.fast, 'tries': [], 'padMoves': 0}
        if self.fast: self.ev("window.__FAST=true")
        self.audit(label + ' experiment: prediction'); self.shot('s01_experiment_predict')
        self.tap(e.locator('.chips button').first, 'prediction chip')
        pad = e.locator('.reactpad'); lastTop = None
        # one deliberate early tap: should say "Too soon"
        if not self.fast:
            self.tap(pad, 'reactpad (early tap)'); info['earlyText'] = pad.text_content()
        for h, hand in enumerate(['right', 'left']):
            for n in range(8):
                t0 = time.time()
                try: pg.wait_for_selector('#app .reactpad.go', timeout=8000)
                except Exception:
                    self.noadvance.append({'screen': self.cur, 'tap': f'reactpad {hand} try {n+1}', 'problem': 'pad never turned green in 8 s'}); raise
                box = pad.bounding_box(); vh = self.ev("innerHeight")
                rec = {'hand': hand, 'n': n + 1, 'waited': round(time.time() - t0, 2), 'padTop': round(box['y']), 'padH': round(box['height']), 'padInViewport': box['y'] >= 0 and box['y'] + box['height'] <= vh, 'text': pad.text_content(), 'prompt': e.locator('.stack p').first.text_content()}
                if lastTop is not None and abs(lastTop - box['y']) > 1: info['padMoves'] += 1
                lastTop = box['y']
                if h == 0 and n == 3:
                    self.audit(label + ' experiment: mid-run (green)'); self.shot('s01_experiment_midrun')
                before = pad.text_content() + str(e.locator('p').first.text_content())
                pad.tap(timeout=4000); self.wait(40)
                rec['advanced'] = (e.locator('.reactpad').count() == 0) or (pad.text_content() + str(e.locator('p').first.text_content()) != before)
                if not rec['advanced']: self.noadvance.append({'screen': self.cur, 'tap': f'reactpad {hand} try {n+1}', 'problem': 'tap on green pad changed nothing'})
                info['tries'].append(rec)
                if h == 0 and n == 0: self.audit(label + ' experiment: waiting (grey)')
            if h == 0:
                self.audit(label + ' experiment: between hands'); self.shot('s01_experiment_between')
                self.tap(self.btn('Ready'), 'Ready')
        self.wait(80)
        self.audit(label + ' experiment: results'); self.shot('s01_experiment_results')
        txt = e.text_content(); m = re.search(r'right hand: ([\d.]+) ms\. Middle time, left hand: ([\d.]+) ms', txt)
        assert m, 'react-no-result'
        mr, ml = float(m.group(1)), float(m.group(2)); info['medians'] = [mr, ml]
        e.locator('select').select_option('right' if mr < ml else 'left' if ml < mr else 'tie')
        self.tap(self.btn('Check'), 'react Check')
        self.react = info

    def answer(self, mode, label):
        if self.use_solve:
            r = self.ev(SOLVE, mode); assert r == 'ok', (label, r)
        else:
            self.solve_taps(mode, label)
        self.wait(60)

    # ---- flows
    def open_parent(self, label):
        self.tap(self.pg.locator('#nav button', has_text='Parent'), 'nav Parent')
        if self.pg.locator('#pcode').count():
            self.audit(label + ' parent code prompt'); self.shot('parent_code') if not os.path.exists(os.path.join(SHOTS, f'{self.scheme}_parent_code.png')) else None
            self.pg.fill('#pcode', '1234'); self.tap(self.primary(), 'parent Set code/Open')

    def home_to_kid(self, kid):
        self.tap(self.pg.locator('#nav button', has_text='Switch person'), 'nav Switch person', expect_change=self.ev("VIEW.name") != 'home')
        self.tap(self.pg.locator('.who button').nth(0 if kid == 'k7' else 1), f'kid picker card {kid}')
        assert self.ev("VIEW.name") == 'kid' and self.ev("VIEW.kid") == kid, 'kid picker did not open ' + kid

    def run(self):
        pg = self.pg; S = self.scheme
        pg.goto(URL); self.wait(700)
        self.metas['device'] = self.dev
        self.audit('home (fresh)'); self.shot('home')
        if self.names:
            self.open_parent('names')
            ins = pg.locator('#app input[type=text][maxlength="20"]')
            ins.nth(0).fill(self.names['k7']); ins.nth(1).fill(self.names['k4'])
            self.tap(self.btn('Save names'), 'Save names')
            self.audit('parent (fresh, names set)')
            self.tap(pg.locator('#nav button', has_text='Switch person'), 'nav Switch person')
            self.audit('home (names set)'); self.shot('home_named')
        for kid in ['k7', 'k4']:
            self.home_to_kid(kid)
            self.audit(f'{kid} kid (start)'); self.shot(f'kid_{kid}_start')
            self.tap(pg.locator('#nav button', has_text='My path'), 'nav My path'); self.audit(f'{kid} path (start)'); self.shot(f'path_{kid}_start')
            self.tap(pg.locator('#nav button', has_text='Today'), 'nav Today')
            done_gates = 0
            for step in range(80):
                pos = self.ev("k=>{const p=position(k); return {kind:p.kind, id:p.session?p.session.id:(p.unit?p.unit.id:null)}}", kid)
                if pos['kind'] == 'end': self.log.append((kid, 'END', pos['id'])); break
                if pos['kind'] == 'session':
                    sid = pos['id']; L = f'{kid} {sid}'
                    self.audit(f'{L} kid screen')
                    card_route = (kid == 'k4' and sid == 'm05' and self.use_solve)
                    if card_route: self.tap(self.btn('I did it from my card'), 'I did it from my card')
                    else: self.tap(self.primary(), 'Start session: ' + self.primary().text_content())
                    if self.stage() == 'warm':
                        self.audit(f'{L} warm'); self.shot('warmup') if sid in ('s02', 'm02') else None
                        self.answer('wrong' if sid in ('s06',) else 'right', '')
                        self.audit(f'{L} warm answered')
                        self.tap(self.primary(), "warm: On to today's session")
                    if not card_route:
                        assert self.stage() == 'task', (L, self.stage())
                        self.audit(f'{L} task' + (' step 1' if kid == 'k4' else ''))
                        if sid in ('s01', 's02', 's03', 'm01', 'm02', 'm03', 's05', 'm04'): self.shot(f'{sid}_task' + ('_step1' if kid == 'k4' else ''))
                        for k in range(10):
                            if self.stage() != 'task': break
                            lab = self.primary().text_content()
                            self.tap(self.primary(), f'task primary: {lab}')
                            if self.stage() == 'task':
                                a = self.audit(f'{L} task step {k+2}')
                                pm = a['meta'].get('primary') or {}
                                if not pm.get('inViewport'): self.add('x Next-step button off-screen after tapping Next step', L, {'primary': pm, 'scrollY': a['meta']['scrollY'], 'vh': a['meta']['vh']})
                                if sid in ('m01', 'm02', 'm03'): self.shot(f'{sid}_task_step{k+2}', full=(k >= 1))
                    assert self.stage() == 'check', (L, self.stage())
                    self.audit(f'{L} check')
                    if sid in ('m01', 's01', 's02', 's03', 'm02', 'm03', 's07', 'm05'): self.shot(f'{sid}_check')
                    self.answer('wrong' if sid in ('m02', 's04') else 'right', L)
                    self.audit(f'{L} check answered')
                    if sid in ('m01', 's01', 's02', 'm02', 's04'): self.shot(f'{sid}_check_answered')
                    assert not self.ev("document.querySelector('#app button.primary').disabled"), ('finish disabled', L)
                    self.tap(self.primary(), 'Finish session')
                    assert self.stage() == 'done', (L, self.stage())
                    self.tap(pg.locator('#app .chips button').first, 'self-report chip (solo)'); self.tap(pg.locator('#app .chips').nth(1).locator('button').first, 'self-report chip (feel)')
                    self.audit(f'{L} done')
                    if sid in ('s01', 'm01', 's12'): self.shot(f'{sid}_done')
                    self.ev("k=>{const st=Store.get(k); for(const r of Object.values(st.rev)) r.due='2020-01-01';}", kid)
                    self.tap(self.btn('Done for today') if self.btn('Done for today').count() else self.btn('Back to today'), 'Done for today')
                    assert self.ev("VIEW.name") == 'kid', 'Done for today did not return to kid view'
                    self.log.append((kid, 'session', sid))
                    if sid in ('s03', 'm03'):
                        self.audit(f'{kid} kid (after {sid}, review due)'); self.shot(f'kid_{kid}_mid')
                        if self.btn('Do a quick review').count():
                            self.tap(self.btn('Do a quick review'), 'Do a quick review'); self.audit(f'{kid} quick review')
                            self.answer('right', ''); self.tap(self.primary(), 'review Done'); self.audit(f'{kid} quick review done')
                            self.tap(self.primary(), 'Back to today')
                            self.ev("k=>{const st=Store.get(k); for(const r of Object.values(st.rev)) r.due='2020-01-01';}", kid)
                elif pos['kind'] == 'gate':
                    G = f"{kid} gate {pos['id']}"
                    self.audit(f'{G} kid screen'); self.shot(f'kid_{kid}_gate') if done_gates == 0 else None
                    self.tap(self.primary(), 'Open the gate')
                    self.audit(f'{G} intro'); self.shot(f'gate_intro_{kid}') if done_gates == 0 else None
                    self.tap(self.primary(), 'Start the quiz')
                    assert self.ev("!!VIEW.quiz"), G + ': quiz did not start'
                    self.audit(f'{G} quiz'); self.shot(f'gate_quiz_{kid}_{pos["id"]}')
                    self.answer('right', '')
                    self.audit(f'{G} quiz answered')
                    self.tap(self.primary(), 'See my score')
                    self.audit(f'{G} result'); self.shot(f'gate_result_{kid}_{pos["id"]}')
                    gs = self.ev("([k,u])=>{const un=unitsOf(k).find(x=>x.id===u); return gateState(k,un)}", [kid, pos['id']])
                    self.log.append((kid, 'gate', pos['id'], gs['gs'].get('quiz', {}).get('best'), gs['n'], gs['quizOk'], gs['prodOk']))
                    if not gs['prodOk']:
                        self.metas[f'{G} result primaryCount'] = self.ev("document.querySelectorAll('#app button.primary').length")
                        self.open_parent(G)
                        self.audit(f'{G} parent (sign-off pending)'); self.shot(f'parent_{kid}_{pos["id"]}')
                        cbs = pg.locator(f"input[id^='rb-g-{pos['id']}-']")
                        for i in range(cbs.count()): self.tap(cbs.nth(i), 'rubric checkbox')
                        td = pg.locator('td', has=pg.locator(f"#rb-g-{pos['id']}-0"))
                        self.tap(td.locator('button', has_text='Sign off'), 'Sign off')
                        self.audit(f'{G} parent (signed)')
                        self.home_to_kid(kid)
                    else:
                        if self.btn('Back to today').count(): self.tap(self.btn('Back to today'), 'gate: Back to today')
                        else: self.home_to_kid(kid)
                    done_gates += 1
            self.audit(f'{kid} kid (end)'); self.shot(f'kid_{kid}_end')
            self.tap(self.btn('See my whole path'), 'See my whole path'); self.audit(f'{kid} path (end)'); self.shot(f'path_{kid}_end')
            # practice replay from the path
            self.tap(pg.locator('.srow button').first, 'path: replay first session'); self.audit(f'{kid} practice task')
            self.tap(pg.locator('#nav button', has_text='Today'), 'nav Today')
        self.open_parent('final')
        self.audit('parent (end)'); self.shot('parent')
        if pg.locator('details summary').count():
            self.tap(pg.locator('details summary').first, 'Written answers summary'); self.audit('parent (written answers open)'); self.shot('parent_written')
        for kid in ['k7', 'k4']:
            self.tap(pg.locator('#app button', has_text='mission cards').nth(0 if kid == 'k7' else 1), 'Print mission cards')
            self.audit(f'{kid} cards'); self.shot(f'cards_{kid}')
            self.tap(self.btn('Back'), 'cards Back')
        self.tap(pg.locator('#nav button', has_text='Switch person'), 'nav Switch person')
        self.audit('home (end)'); self.shot('home_end')
        # landscape sanity (rotate): page overflow only
        pg.set_viewport_size({'width': 664, 'height': 390}); self.wait(100); self.audit('home (landscape)')
        pg.set_viewport_size({'width': 320, 'height': 568}); self.wait(100); self.audit('home (320px wide)')
        self.ev("go({name:'kid',kid:'k4'})"); self.wait(80); self.audit('k4 kid (320px wide)'); self.shot('kid_k4_320')
        self.browser.close()

    def dump(self):
        return {'scheme': self.scheme, 'fast': self.fast, 'use_solve': self.use_solve, 'log': self.log, 'errors': self.errors, 'noadvance': self.noadvance,
                'react': self.react, 'findings': [{'cat': c, 'key': k, **v} for (c, k), v in self.findings.items()], 'metas': self.metas, 'copy': self.copy}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    res = {}
    with sync_playwright() as pw:
        for scheme, fast, use_solve, names in [('dark', False, False, None), ('light', True, True, {'k7': 'Sam', 'k4': 'Mia'})]:
            if only and only != scheme: continue
            p = Pass(pw, scheme, fast, use_solve, names); t0 = time.time(); crash = None
            try: p.run()
            except Exception as e:
                import traceback; crash = traceback.format_exc()
                try:
                    p.shot('CRASH'); crash += '\nVIEW=' + p.ev("JSON.stringify(VIEW).slice(0,300)") + '\n' + p.ev("document.getElementById('app').innerText.slice(0,600)")
                except Exception: pass
                try: p.browser.close()
                except Exception: pass
            d = p.dump(); d['crash'] = crash; d['secs'] = round(time.time() - t0, 1); res[scheme] = d
            json.dump(res, open(os.path.join(HERE, 'phone_audit_report.json'), 'w'), indent=1)
    for scheme, d in res.items():
        print(f"\n================ {scheme.upper()} pass  ({d['secs']} s, fast={d['fast']}, solver={'SOLVE js' if d['use_solve'] else 'real taps'}) ================")
        print('CRASH:', d['crash'] or 'none'); print('walk log:', len(d['log']), 'entries;', [l for l in d['log'] if l[1] != 'session'])
        print('sessions walked:', ' '.join(l[2] for l in d['log'] if l[1] == 'session'))
        print('ERRORS:', json.dumps(d['errors'], indent=1) if d['errors'] else 'none')
        print('TAPS THAT DID NOT ADVANCE:', json.dumps(d['noadvance'], indent=1) if d['noadvance'] else 'none')
        if d['react']:
            r = d['react']; print('REACT: earlyText=%r padMoves=%s medians=%s padInViewport(all)=%s texts=%s waits=%s' % (r.get('earlyText'), r['padMoves'], r.get('medians'), all(t['padInViewport'] for t in r['tries']), sorted(set(t['text'] for t in r['tries'])), [t['waited'] for t in r['tries']]))
            print('  prompts:', sorted(set(re.sub(r'Try \d', 'Try N', t['prompt']) for t in r['tries'])))
        cat = None
        for f in sorted(d['findings'], key=lambda f: f['cat']):
            if f['cat'] != cat: cat = f['cat']; print('\n--', cat)
            sc = f['screens']; det = {k: v for k, v in f['detail'].items() if k not in ('overlapEx',) or v}
            print('  ', json.dumps(det)[:330], '| n_screens=%d e.g. %s' % (len(sc), '; '.join(sc[:3])))
        m = d['metas']; any_meta = next((v for k, v in m.items() if isinstance(v, dict) and 'lexend' in v), {})
        print('\nfonts loaded: Lexend=%s Bricolage=%s  viewport=%sx%s' % (any_meta.get('lexend'), any_meta.get('brico'), any_meta.get('vw'), any_meta.get('vh')))
        print('title rows:'); [print('  ', json.dumps(v)) for v in m.get('titleRows', {}).values()]
        print('primary button below the fold (pageY > vh) on first paint:')
        for k, v in m.items():
            if isinstance(v, dict) and v.get('primary') and v['primary']['pageY'] > v['vh'] and v.get('vw') == 390 and re.search(r'(s0[1-3]|m0[1-3]) (task|check$)|gate \w+ quiz$', k): print('   %-42s %-38s y=%d docH=%d' % (k, v['primary']['label'][:38], v['primary']['pageY'], v['docH']))


if __name__ == '__main__':
    main()
