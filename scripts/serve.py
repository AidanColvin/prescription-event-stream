"""Local development server: static files plus the events API.

Mirrors the Vercel deployment closely enough to test every page:
clean URLs (/pharmacist serves pharmacist/index.html) and /api/events
running the same pipeline the serverless function runs.

    python3 scripts/serve.py [port]
"""

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingestion import get_refill_events
from src.transform import process_events


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path.startswith("/api/events"):
            payload = process_events(get_refill_events())
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path != "/" and not Path(ROOT / path.lstrip("/")).suffix:
            candidate = ROOT / path.lstrip("/") / "index.html"
            if candidate.exists():
                self.path = f"{path}/index.html"
        super().do_GET()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    print(f"serving on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
