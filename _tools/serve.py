"""Serve the export locally under its production /naviora-website prefix."""
import http.server, os, socketserver
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "/naviora-website"
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = path[len(PREFIX):] or "/"
        return super().translate_path(path)
    def log_message(self, *a): pass
os.chdir(ROOT)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8098), H) as s:
    s.serve_forever()
