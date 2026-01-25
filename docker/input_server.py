#!/usr/bin/env python3
"""
Simple HTTP server to send input to the ADVENT screen session.
Used by the demo mode to send keystrokes.

Listens on port 8083 and accepts POST requests to /send with body containing the text to send.
"""

import http.server
import subprocess
import urllib.parse

PORT = 8083

class InputHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/send':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            # Send to screen session
            try:
                # Use screen's 'stuff' command to send input
                subprocess.run(
                    ['screen', '-S', 'advent', '-X', 'stuff', body],
                    check=True,
                    timeout=5
                )
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"ok":false,"error":"{str(e)}"}}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print(f'Input server listening on port {PORT}')
    server = http.server.HTTPServer(('127.0.0.1', PORT), InputHandler)
    server.serve_forever()
