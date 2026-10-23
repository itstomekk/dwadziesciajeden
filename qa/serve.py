"""Serve docs/ under /dwadziesciajeden/ like GitHub Pages. Usage: python qa/serve.py [port]"""
import functools, http.server, sys
from pathlib import Path
DOCS = Path(__file__).resolve().parent.parent / "docs"
import os
PREFIX = os.environ.get("DJ_BASE", "/dwadziesciajeden").rstrip("/")  # "" = custom-domain build
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if not PREFIX:
            pass
        elif path.startswith(PREFIX):
            path = path[len(PREFIX):] or "/"
        else:
            path = "/__nope__"
        return super().translate_path(path)
    def send_error(self, code, message=None, explain=None):
        if code == 404 and (DOCS / "404.html").exists():
            body = (DOCS / "404.html").read_bytes()
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        super().send_error(code, message, explain)
    def log_message(self, *a): pass
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8721
http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=str(DOCS))).serve_forever()
