#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import datetime
import ssl
import os

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
            "message": "Mock response from HTTPS server",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode())

def run_server():
    cert_dir = os.path.join(os.path.dirname(__file__), '../certs')
    cert_file = os.path.join(cert_dir, 'server.crt')
    key_file = os.path.join(cert_dir, 'server.key')
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        logging.error("Certificate not found. Run: ./generate_cert.sh")
        return
    
    server = HTTPServer(('0.0.0.0', 443), MockHandler)
    
    # Setup SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    logging.info("🚀 HTTPS Mock server running on port 443")
    logging.info("📡 Listening on all interfaces (0.0.0.0)")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
