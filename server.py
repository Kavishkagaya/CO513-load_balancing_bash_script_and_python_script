#!/usr/bin/env python3
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'  # Ensure no persistent connection

    def do_GET(self):
        hostname = socket.gethostname()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Connection', 'close')
        self.end_headers()
        response = f"Hello from backend server: {hostname}\n"
        self.wfile.write(response.encode())
        self.wfile.flush()  # Ensure it's sent before connection closes

    def log_message(self, format, *args):
        return  # Disable logging

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
