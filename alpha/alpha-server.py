#!/bin/env python3

import http.server
import socketserver
import signal
import sys, os

# Global Defaults
port = 8000

# get args
args=sys.argv[1:]
for i in range(len(args)):
  if (args[i] == "-p"):
    port = int(args[i+1])
    
# checks
if not os.path.exists("code"):
    os.makedirs("code")
    

class handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        self._set_headers()
        f = open('index.html', 'r')
        for i in f:
          self.wfile.write(i.encode("UTF-8"))
        f.close
    def do_POST(self):
        self._set_headers()
        data = self.rfile.read(int(self.headers.get_all('content-length')[0]))
        f = open ("code/" + self.path,'w')
        f.write(data.decode("UTF-8"))
        f.close()
    def do_DELETE(self):
        self._set_headers()
        self.wfile.write(b"<html><body><h1>delete!</h1></body></html>")

# run server
httpd = socketserver.TCPServer(("", port), handler)
print("Serving at port", port)
try:
  httpd.serve_forever()
except KeyboardInterrupt:
  sys.exit(0)
    