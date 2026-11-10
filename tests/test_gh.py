import os
import json, re, base64, hashlib, sys
from playwright.sync_api import sync_playwright
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
SOLVE = re.search(r"SOLVE = r'''\n(.*?)\n'''", open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'walk.py')).read(), re.S).group(1)
GOOD='github_pat_GOODTOKEN_0123456789abcdef'
class Mock:
    def __init__(s): s.files={}; s.conflict_once=False; s.readonly=False; s.offline=False; s.puts=0; s.private=True
    def sha(s,c): return hashlib.sha1(c.encode()).hexdigest()
    def handle(s, route):
        rq=route.request; url=rq.url.split('?')[0]
        if s.offline: return route.abort()
        if rq.method=='OPTIONS': return route.fulfill(status=204, headers={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'})
        H={'access-control-allow-origin':'*','content-type':'application/json'}
        if rq.headers.get('authorization')!='Bearer '+GOOD: return route.fulfill(status=401, headers=H, body='{"message":"Bad credentials"}')
        m=re.match(r'https://api.github.com/repos/([^/]+/[^/]+)(?:/contents/(.+))?$', url)
        if not m or m.group(1)!='fam/progress': return route.fulfill(status=404, headers=H, body='{}')
        path=m.group(2)
        if not path: return route.fulfill(status=200, headers=H, body=json.dumps({'private':s.private}))
        if rq.method=='GET':
            if path not in s.files: return route.fulfill(status=404, headers=H, body='{"message":"Not Found"}')
            f=s.files[path]; return route.fulfill(status=200, headers=H, body=json.dumps({'content':f['content'],'sha':f['sha']}))
        if rq.method=='PUT':
            if s.readonly: return route.fulfill(status=403, headers=H, body='{"message":"Resource not accessible by personal access token"}')
            body=json.loads(rq.post_data)
            if s.conflict_once and path=='state/k4.json':
                s.conflict_once=False
                d=json.loads(base64.b64decode(s.files[path]['content']).decode()); d['done']['m03']={'t':5,'first':1,'auto':1,'mins':9}; d['ts']=d.get('ts',0)+1
                c=base64.b64encode(json.dumps(d).encode()).decode(); s.files[path]={'content':c,'sha':s.sha(c+'x')}
            cur=s.files.get(path)
            if cur and not body.get('sha'): return route.fulfill(status=422, headers=H, body='{"message":"sha was not supplied"}')
            if cur and body['sha']!=cur['sha']: return route.fulfill(status=409, headers=H, body='{"message":"sha mismatch"}')
            s.puts+=1; sh=s.sha(body['content']+str(s.puts)); s.files[path]={'content':body['content'],'sha':sh}
            return route.fulfill(status=200, headers=H, body=json.dumps({'content':{'sha':sh}}))
        return route.fulfill(status=405, headers=H, body='{}')
    def read(s,path): return json.loads(base64.b64decode(s.files[path]['content']).decode())
mock=Mock(); res=[]; errs=[]
def ok(name, cond, extra=''): res.append((name, bool(cond), extra)); print(('PASS ' if cond else 'FAIL ')+name, extra)
def newdev(b, **kw):
    c=b.new_context(viewport={'width':820,'height':1100}, **kw); c.route('https://api.github.com/**', mock.handle); pg=c.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(400); return pg
def connect(pg, token=GOOD, repo='fam/progress'):
    pg.fill('#ghrepo', repo); pg.fill('#ghtok', token); pg.click('button:text-is("Connect")'); pg.wait_for_timeout(900)
def do_session(pg, kid, card=False):
    pg.evaluate("k=>go({name:'kid',kid:k})", kid); pg.wait_for_timeout(60)
    if card: pg.click('text=I did it from my card')
    else: pg.click('button.primary')
    pg.wait_for_timeout(50)
    if pg.evaluate("VIEW.stage")=='warm':
        assert pg.evaluate(SOLVE,'right')=='ok'; pg.click('button.primary'); pg.wait_for_timeout(50)
    if not card:
        for _ in range(8):
            if pg.evaluate("VIEW.stage")!='task': break
            pg.click('button.primary'); pg.wait_for_timeout(40)
    st=pg.evaluate("VIEW.stage"); assert st=='check', st
    r=pg.evaluate(SOLVE,'right'); assert r=='ok', r
    pg.click('button.primary'); pg.wait_for_timeout(300)
    assert pg.evaluate("VIEW.stage")=='done'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME','/usr/bin/google-chrome'), args=['--no-sandbox'])
    A=newdev(b)
    FORBID=os.environ.get('DATALAB_FORBID','')
    ok('source has no forbidden names', (not FORBID) or not re.search(FORBID, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')).read()))
    ok('default labels', 'Seventh grader' in A.inner_text('#app') and 'Fourth grader' in A.inner_text('#app'))
    A.evaluate("go({name:'parent'})"); A.wait_for_timeout(80)
    ok('new device offers sync before the code', A.query_selector('#ghrepo') is not None and 'Already set up on another device' in A.inner_text('#app'))
    A.fill('#pcode','4321'); A.click('text=Set code'); A.wait_for_timeout(80)
    # bad inputs
    connect(A, token='short'); ok('rejects short token', 'paste the whole token' in A.inner_text('#app'))
    connect(A, token='github_pat_WRONG_0123456789abcdef'); ok('bad token message', 'did not accept that token' in A.inner_text('#app'), A.inner_text('#app')[-200:].replace('\n',' ')[:0])
    connect(A, repo='fam/other'); ok('missing repo message', 'not found' in A.inner_text('#app'))
    mock.private=False; connect(A); ok('public repo refused', 'public' in A.inner_text('#app')); mock.private=True
    mock.readonly=True; connect(A); ok('read-only token message', 'cannot write' in A.inner_text('#app')); mock.readonly=False
    ok('nothing stored after failures', A.evaluate("localStorage.getItem('datalab:gh')") is None and len(mock.files)==0)
    connect(A)
    ok('connected status line', 'private GitHub repo' in A.inner_text('#sync'), A.inner_text('#sync'))
    ok('write test file', 'state/device-check.json' in mock.files)
    ok('parent state pushed with code', mock.read('state/parent.json').get('code')=='4321' if 'state/parent.json' in mock.files else False)
    ins=A.query_selector_all("input[aria-label^='Name for']"); ins[0].fill('Sam'); ins[1].fill('Mia'); A.click('text=Save names'); A.wait_for_timeout(500)
    ok('names saved to repo', mock.read('state/parent.json').get('names')=={'k7':'Sam','k4':'Mia'})
    A.evaluate("go({name:'home'})"); A.wait_for_timeout(60); ok('names shown', 'Sam' in A.inner_text('#app') and 'Mia' in A.inner_text('#app'))
    do_session(A,'k4'); A.wait_for_timeout(500)
    ok('session reached repo', 'm01' in mock.read('state/k4.json')['done'])
    # second device
    B=newdev(b)
    B.evaluate("go({name:'parent'})"); B.wait_for_timeout(80); connect(B); B.wait_for_timeout(300)
    ok('B: asks for existing code after sync', 'Enter the parent code' in B.inner_text('#app'), B.inner_text('#app')[:120].replace('\n',' '))
    B.evaluate("go({name:'home'})"); B.wait_for_timeout(60)
    ok('B: names and progress arrived', 'Mia' in B.inner_text('#app') and B.evaluate("counts('k4').total")==1)
    do_session(B,'k4'); B.wait_for_timeout(500)
    ok('B: card flag absent on normal run', 'card' not in mock.read('state/k4.json')['done']['m02'])
    # a device that set its own code before connecting must not replace the family's code
    D=newdev(b); D.evaluate("go({name:'parent'})"); D.wait_for_timeout(80); D.fill('#pcode','9999'); D.click('text=Set code'); D.wait_for_timeout(80); connect(D); D.wait_for_timeout(600)
    ok('late connect keeps the family code and names', mock.read('state/parent.json').get('code')=='4321' and mock.read('state/parent.json').get('names')=={'k7':'Sam','k4':'Mia'} and D.evaluate("Store.get('parent').code")=='4321', str(mock.read('state/parent.json').get('code')))
    ok('parent view relocks after connect', D.query_selector('#pcode') is not None)
    A.reload(); A.wait_for_timeout(900)
    ok('A: sees B session after reload', A.evaluate("counts('k4').total")==2 and 'private GitHub repo' in A.inner_text('#sync'))
    # conflict: another device writes between A's read and write
    mock.conflict_once=True
    do_session(A,'k4', card=True); A.wait_for_timeout(900)   # A does m03 via card... the mock injects m03 too; then A does it
    d=mock.read('state/k4.json')
    ok('conflict retried and merged', set(['m01','m02','m03']).issubset(d['done'].keys()) and 'private GitHub repo' in A.inner_text('#sync'), str(sorted(d['done'].keys())))
    ok('card run flagged', A.evaluate("Store.get('k4').done.m03.card")==1)
    # erase on A reaches B
    A.evaluate("Store.reset('k4')"); A.wait_for_timeout(600)
    B.reload(); B.wait_for_timeout(900)
    ok('erase reaches other device', B.evaluate("counts('k4').total")==0 and mock.read('state/k4.json')['epoch']==1)
    # offline
    mock.offline=True; A.reload(); A.wait_for_timeout(1200)
    ok('offline: warns and keeps working', 'saved on this device only' in A.inner_text('#sync') and 'GitHub is not reachable' in A.inner_text('#sync'), A.inner_text('#sync'))
    do_session(A,'k4'); ok('offline: session still completes', A.evaluate("counts('k4').total")==1)
    mock.offline=False; A.reload(); A.wait_for_timeout(1200)
    ok('back online: catches up', 'm01' in mock.read('state/k4.json')['done'] and 'private GitHub repo' in A.inner_text('#sync'))
    # visibility pull
    do_session(B,'k7') if False else None
    # revoked token
    A.evaluate("(()=>{const c=JSON.parse(localStorage.getItem('datalab:gh')); c.token='github_pat_REVOKED_0123456789abcd'; localStorage.setItem('datalab:gh', JSON.stringify(c));})()"); A.reload(); A.wait_for_timeout(1000)
    ok('revoked token: tells the parent', 'token stopped working' in A.inner_text('#sync'), A.inner_text('#sync'))
    # disconnect
    A.evaluate("go({name:'parent'})"); A.wait_for_timeout(60); A.fill('#pcode','4321'); A.click('text=Open'); A.wait_for_timeout(60); A.click('text=Disconnect this device'); A.wait_for_timeout(100)
    ok('disconnect clears token', A.evaluate("localStorage.getItem('datalab:gh')") is None and 'saved on this device' in A.inner_text('#sync'))
    # cards
    C=newdev(b)
    C.evaluate("go({name:'cards',kid:'k4'})"); C.wait_for_timeout(100)
    n=len(C.query_selector_all('.mcard')); txt=C.inner_text('#app')
    ok('12 cards', n==12, str(n)); ok('reveal kept off the card', txt.count('The whole graph is in Data Lab')==2, str(txt.count('The whole graph is in Data Lab')))
    C.screenshot(path='cards_k4.png', full_page=True)
    C.emulate_media(media='print'); C.pdf(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','mission-cards-k4.pdf'), format='Letter', margin={'top':'12mm','bottom':'12mm','left':'12mm','right':'12mm'}, print_background=False)
    C.emulate_media(media='screen')
    # m08 via card shows the page's graph in the check
    for i in range(12):
        C.evaluate("go({name:'kid',kid:'k4'})"); C.wait_for_timeout(60)
        pos=C.evaluate("(()=>{const p=position('k4'); return [p.kind, p.session?p.session.id:null]})()")
        if pos[0]=='gate':
            C.click('button.primary'); C.wait_for_timeout(40); C.click('button.primary'); C.wait_for_timeout(40); assert C.evaluate(SOLVE,'right')=='ok'; C.click('button.primary'); C.wait_for_timeout(60); continue
        if pos[1]=='m08': break
        do_session(C,'k4', card=(i%2==0))
    ok('at m08', C.evaluate("position('k4').session.id")=='m08', str(C.evaluate("position('k4').session && position('k4').session.id")))
    C.click('text=I did it from my card'); C.wait_for_timeout(60)
    if C.evaluate("VIEW.stage")=='warm': assert C.evaluate(SOLVE,'right')=='ok'; C.click('button.primary'); C.wait_for_timeout(50)
    ok('m08 card path shows the drawn graph in the check', C.evaluate("VIEW.stage")=='check' and 'The graph the page drew from your counts' in C.inner_text('#app'))
    C.screenshot(path='m08_card_check.png', full_page=True)
    # older kid has no card button
    C.evaluate("go({name:'kid',kid:'k7'})"); C.wait_for_timeout(60); ok('no card button for the older kid', 'I did it from my card' not in C.inner_text('#app'))
    # touch targets
    sizes=C.evaluate("[...document.querySelectorAll('nav button')].map(b=>Math.round(b.getBoundingClientRect().height))"); ok('nav targets >=44', min(sizes)>=44, str(sizes))
    b.close()
print('page errors:', errs); print('FAILED:', [r for r in res if not r[1]])
