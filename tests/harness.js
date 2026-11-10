
(async()=>{
 const sleep = ms => new Promise(r=>setTimeout(r,ms));
 const P = new URLSearchParams(location.search); const stop = P.get("stop")||"";
 if(!sessionStorage.getItem("hclean")){ localStorage.clear(); sessionStorage.setItem("hclean","1"); location.reload(); return; }
 sessionStorage.removeItem("hclean");
 const R = {ua:navigator.userAgent, w:innerWidth, h:innerHeight, dpr:devicePixelRatio, stop:stop, log:[], errors:[], audit:[], t0:Date.now()};
 window.addEventListener("error", e=>R.errors.push(String(e.message)+" @"+e.lineno));
 window.addEventListener("unhandledrejection", e=>R.errors.push("rej:"+String(e.reason)));
 const SOLVE = async (mode) => {
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
};
 const prim = ()=>document.querySelector("#app button.primary");
 const audit = tag => { const de=document.documentElement; const els=[...document.querySelectorAll("#app button, #app select, #app input, #app textarea, header button, nav button")].filter(e=>e.offsetParent).map(e=>{ const r=e.getBoundingClientRect(); return {t:e.tagName, x:(e.textContent||e.placeholder||e.type||"").trim().slice(0,18), h:Math.round(r.height), w:Math.round(r.width), fs:parseFloat(getComputedStyle(e).fontSize), right:Math.round(r.right)}; });
   const tiny=els.filter(x=>x.h<36 && x.t!=="INPUT" || (x.t==="INPUT" && x.h<36 && x.x!=="checkbox")); const zoom=els.filter(x=>x.t!=="BUTTON" && x.fs<16); const off=els.filter(x=>x.right>innerWidth+1);
   R.audit.push({tag:tag, over:de.scrollWidth-de.clientWidth, n:els.length, ntiny:tiny.length, tiny:tiny.slice(0,5), nzoom:zoom.length, zoom:zoom.slice(0,4), noff:off.length, off:off.slice(0,3)}); };
 const send = async () => { R.ms = Date.now()-R.t0; try{ await fetch("/report", {method:"POST", body:JSON.stringify(R)}); }catch(e){} const d=document.createElement("div"); d.style.cssText="position:fixed;left:0;right:0;bottom:0;background:#000;color:#0f0;font:16px monospace;padding:10px;z-index:99999"; d.textContent="HARNESS "+(R.fail?"FAIL "+R.fail:"DONE")+" sessions="+R.log.filter(l=>l[1]==="session").length+" gates="+R.log.filter(l=>l[1]==="gate").length+" errors="+R.errors.length; document.body.append(d); };
 try{
  await sleep(700);
  R.mode = Store.mode; R.speech = (typeof speechSynthesis!=="undefined"); R.ls = (()=>{ try{ localStorage.setItem("_t","1"); localStorage.removeItem("_t"); return true; }catch(e){ return false; } })();
  audit("home");
  for(const kid of ["k4","k7"]){
   go({name:"kid",kid:kid}); await sleep(60); audit("kid-"+kid);
   for(let step=0; step<80; step++){
    const p = position(kid); const id = p.session ? p.session.id : (p.unit ? p.unit.id : null);
    if(p.kind==="end"){ R.log.push([kid,"END",id]); break; }
    if(p.kind==="session"){
      prim().click(); await sleep(40);
      if(VIEW.stage==="warm"){ const r=await SOLVE("right"); if(r!=="ok") throw new Error("warm "+id+" "+r); if(id==="m03"||id==="s03") audit("warm-"+id); prim().click(); await sleep(40); }
      if(VIEW.stage!=="task") throw new Error("not task "+id+" "+VIEW.stage);
      if(["m02","m09","s02","s05","s11"].includes(id)) audit("task-"+id);
      for(let i=0;i<8;i++){ if(VIEW.stage!=="task") break; prim().click(); await sleep(40); }
      const r = await SOLVE((id==="m02"||id==="s04") ? "wrong" : "right"); if(r!=="ok") throw new Error("solve "+id+" "+r);
      if(["m01","m05","m09","m12","s01","s06","s09","s12"].includes(id)) audit("check-"+id);
      if(stop===id){ R.stopped=id; await send(); return; }
      if(prim().disabled) throw new Error("finish disabled "+id);
      prim().click(); await sleep(40);
      if(VIEW.stage!=="done") throw new Error("not done "+id);
      if(id==="m01") audit("done-m01");
      const st=Store.get(kid); for(const r2 of Object.values(st.rev)) r2.due="2020-01-01";
      go({name:"kid",kid:kid}); await sleep(30); R.log.push([kid,"session",id]);
    } else if(p.kind==="gate"){
      prim().click(); await sleep(40); prim().click(); await sleep(40);
      const r = await SOLVE("right"); if(r!=="ok") throw new Error("gate "+id+" "+r);
      if(id==="m1a") audit("gate-m1a");
      prim().click(); await sleep(40);
      const un = unitsOf(kid).find(x=>x.id===id); const gs = gateState(kid, un);
      R.log.push([kid,"gate",id,(gs.gs.quiz||{}).best,gs.n,gs.quizOk,gs.prodOk]);
      if(!gs.prodOk){ const g=Store.get(kid).gates; const key=un.gate.id; g[key]=g[key]||{}; g[key].sign={t:Date.now(),by:"harness"}; Store.save(kid); const gs2=gateState(kid, un); R.log.push([kid,"signoff",id,gs2.prodOk]); if(!gs2.prodOk) throw new Error("signoff shape "+id+" "+JSON.stringify(g[key]).slice(0,120)); }
      go({name:"kid",kid:kid}); await sleep(30);
    } else throw new Error("pos "+p.kind);
   }
   go({name:"path",kid:kid}); await sleep(60); audit("path-"+kid);
  }
  go({name:"parent"}); await sleep(60); audit("parent");
  R.totals = [counts("k7").total, counts("k4").total];
  R.stored = ["k7","k4"].map(k=>{ try{ const raw = Store.local(k); return raw && raw.done ? Object.keys(raw.done).length : -1; }catch(e){ return "err "+e.message; } });
  go({name:"home"}); await sleep(60);
 }catch(e){ R.fail = String(e.message||e); }
 await send();
})();
