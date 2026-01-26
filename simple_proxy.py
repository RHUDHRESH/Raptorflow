#!/usr/bin/env python3
"""
Simple proxy server for testing Raptorflow integration
"""

import json
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_PUT(self):
        self.proxy_request()

    def do_DELETE(self):
        self.proxy_request()

    def do_PATCH(self):
        self.proxy_request()

    def proxy_request(self):
        try:
            # Extract the path after /api/proxy
            if self.path.startswith("/api/proxy"):
                backend_path = self.path[11:]  # Remove '/api/proxy'
                # Ensure the path starts with /
                if not backend_path.startswith("/"):
                    backend_path = "/" + backend_path
                backend_url = f"http://localhost:8000{backend_path}"

                # Get request body for POST/PUT requests
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length > 0 else None

                # Create request
                req = urllib.request.Request(
                    backend_url, data=body, method=self.command
                )

                # Copy headers (excluding host)
                for header, value in self.headers.items():
                    if header.lower() != "host":
                        req.add_header(header, value)

                # Make the request
                with urllib.request.urlopen(req) as response:
                    # Send response
                    self.send_response(response.getcode())

                    # Copy response headers
                    for header, value in response.headers.items():
                        if header.lower() != "connection":
                            self.send_header(header, value)

                    self.end_headers()

                    # Send response body
                    self.wfile.write(response.read())
            else:
                # Serve the test page
                if self.path == "/" or self.path == "/index.html":
                    self.serve_file("test_frontend.html", "text/html")
                else:
                    self.send_error(404, "Not Found")

        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(500, f"Proxy Error: {str(e)}")

    def serve_file(self, filename, content_type):
        try:
            with open(filename, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File Not Found")


if __name__ == "__main__":
    print("🚀 Starting Raptorflow Test Proxy Server...")
    print("📝 Test page: http://localhost:3000")
    print("🔗 Backend: http://localhost:8000")
    print("🔄 Proxy: http://localhost:3000/api/proxy/*")

    server = HTTPServer(("localhost", 3000), ProxyHandler)
    server.serve_forever()
