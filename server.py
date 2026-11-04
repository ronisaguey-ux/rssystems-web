#!/usr/bin/env python3
"""
RS Systems Production Web Server (rs-systems-web.com)
Hosted on mastercrustserver.
Serves the Google Stitch engineered landing page and assets with sub-millisecond response time.
"""

import os
import sys
import json
import time
import socket
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", 8080))
HOST = os.environ.get("HOST", "0.0.0.0")
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
START_TIME = time.time()


class RSSystemsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Health endpoint
        if path in ("/health", "/healthz"):
            data = {
                "status": "healthy",
                "domain": "rs-systems-web.com",
                "platform": "RS Systems Autonomous Platform",
                "host": socket.gethostname(),
                "node": "mastercrustserver",
                "uptime_seconds": int(time.time() - START_TIME),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner": "Tomer Saguey",
                "lead_engineer": "Roni Saguey",
                "contact": "buisness@rs-systems-web.com"
            }
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
            return

        # Fallback root to index.html
        if path == "/" or not os.path.exists(os.path.join(PUBLIC_DIR, path.lstrip("/"))):
            if path in ("", "/"):
                self.path = "/index.html"
            elif not os.path.exists(os.path.join(PUBLIC_DIR, path.lstrip("/"))):
                # SPA fallback for clean routes
                self.path = "/index.html"

        # Apply security headers
        super().do_GET()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        # Concise access logging
        sys.stderr.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {args[0]} {args[1]} -> {args[2]}\n")


def main():
    print(f"==================================================")
    print(f"⚡ RS Systems Web Server — rs-systems-web.com")
    print(f"Host:      {HOST}:{PORT}")
    print(f"Directory: {PUBLIC_DIR}")
    print(f"Server:    {socket.gethostname()}")
    print(f"Started:   {time.ctime(START_TIME)}")
    print(f"==================================================")

    server = HTTPServer((HOST, PORT), RSSystemsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly...")
        server.server_close()


if __name__ == "__main__":
    main()
