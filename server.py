import http.server
import socketserver

PORT = 8090

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    print(f"Serving UI at http://localhost:{PORT}")
    socketserver.TCPServer(("", PORT), MyHandler).serve_forever()
