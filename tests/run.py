import os
import json,sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    dev=p.devices['iPad (gen 7)']
    b=p.webkit.launch(); c=b.new_context(**dev); pg=c.new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8766/test.html'+(sys.argv[1] if len(sys.argv)>1 else ''))
    pg.wait_for_selector('text=HARNESS', timeout=120000)
    print(pg.inner_text('body')[-120:]); print('pageerrors', errs)
    b.close()
r=json.load(open('/tmp/datalab-report.json'))
print({k:r[k] for k in r if k not in ('log','audit')})
print(len(r['log']), r['log'][-3:])
for a in r['audit']: print(a)
