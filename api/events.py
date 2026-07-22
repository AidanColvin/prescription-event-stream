from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.ingestion import generate_events
from src.transform import transform_events

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            count = int(query_params.get('count', [20])[0])
            count = max(1, min(count, 100))
            
            raw_events = generate_events(count)
            result = transform_events(raw_events)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
