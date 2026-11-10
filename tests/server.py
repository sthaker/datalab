import os
import http.server,os
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); d=self.rfile.read(n)
        open(os.environ.get('REPORT','/tmp/datalab-report.json'),'wb').write(d)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self,*a): pass
os.chdir(os.environ.get('SITE', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')))
http.server.ThreadingHTTPServer(('127.0.0.1',8766),H).serve_forever()
