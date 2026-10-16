#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import datetime

logging.basicConfig(level=logging.INFO)

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def handle_request(self, method):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        logging.info(f"=== {method} {self.path} ===")
        logging.info(f"Headers: {dict(self.headers)}")
        if body:
            logging.info(f"Body: {body[:500]}")
        
        # Simpan ke file
        with open('captured_requests.log', 'a') as f:
            f.write(f"\n=== {method} {self.path} ===\n")
            f.write(f"Headers: {dict(self.headers)}\n")
            if body:
                f.write(f"Body: {body.decode('utf-8', errors='ignore')[:1000]}\n")
        
        # Response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            "status": "success",
            "message": "Mock response from PESCM server",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 80), MockHandler)
    logging.info("🚀 Mock server running on port 80")
    logging.info("📡 Listening on all interfaces (0.0.0.0)")
    logging.info("📁 Requests logged to: captured_requests.log")
    server.serve_forever()
