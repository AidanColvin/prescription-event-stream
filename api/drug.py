"""Serverless endpoint: /api/drug?name=<term>

Looks up any drug against RxNorm and the openFDA label database and
returns the shaped card the frontend renders. Responses are edge-cached
for a day so repeat queries never re-hit the upstream APIs.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.drug_lookup import lookup_drug


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            params = parse_qs(urlparse(self.path).query)
            term = (params.get('name') or [''])[0]
            result = lookup_drug(term)
        except Exception:
            result = {"found": False}

        body = json.dumps(result).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control',
                         's-maxage=86400, stale-while-revalidate=604800')
        self.end_headers()
        self.wfile.write(body)
