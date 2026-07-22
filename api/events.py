from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.ingestion import get_refill_events
from src.transform import process_events

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            raw_events = get_refill_events()
            if 'count' in query_params:
                try:
                    count = max(1, min(int(query_params['count'][0]), 100))
                    raw_events = raw_events[:count]
                except ValueError:
                    pass
            result = process_events(raw_events)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
