"""Serve the export locally under its production /naviora-website prefix."""
import http.server, os, socketserver
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "/naviora-website"
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = path[len(PREFIX):] or "/"
        return super().translate_path(path)
    def send_error(self, code, *a, **k):
        # Mimic GitHub Pages: unknown paths serve /404.html with a 404 status.
        if code == 404 and os.path.exists(os.path.join(ROOT, "404.html")):
            body = open(os.path.join(ROOT, "404.html"), "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try: self.wfile.write(body)
            except Exception: pass
            return
        super().send_error(code, *a, **k)
    def log_message(self, *a): pass
os.chdir(ROOT)
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True
with TS(("127.0.0.1", 8111), H) as s:
    s.serve_forever()
