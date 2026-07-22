"""System health check endpoint."""

from http.server import BaseHTTPRequestHandler
import json
import time

class handler(BaseHTTPRequestHandler):
    """Handles basic uptime requests."""
    def do_GET(self):
        """Returns HTTP 200 and current time."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "time": int(time.time())}).encode('utf-8'))
