#!/bin/env python3

import http.server
import socketserver
import signal
import sys, os, re, cgi

# Global Defaults
port    = 8000
codeDir = "codeScrolls"

# get args
args=sys.argv[1:]
for i in range(len(args)):
  if (args[i] == "-p"):
    port = int(args[i+1])

# checks
if not os.path.exists(codeDir):
    os.makedirs(codeDir)

class handler(http.server.BaseHTTPRequestHandler):
    def set_headers(self, code):
      self.send_response(code)
      self.send_header(b'Content-type', 'text/html')
      self.end_headers()

    # GET
    def do_GET(self): # check if contained to directory
      filePath=re.sub("^/",os.getcwd()+"/",self.path)
      if os.path.isfile(filePath):
        self.set_headers(200)
        f = open(filePath, 'r')
        for i in f:
          self.wfile.write(i.encode("UTF-8"))
        f.close
      elif os.path.isdir(filePath):
        index=os.path.join(filePath,"index.html")
        if os.path.isfile(index):
          self.set_headers(200)
          f = open(index, 'r')
          for i in f:
            self.wfile.write(i.encode("UTF-8"))
          f.close
        else:
          for i in os.listdir(filePath):
            i = "<a href=\'" + self.path + i + "\'>"+i+"</a>"
            self.wfile.write(i.encode("UTF-8"))
      elif not os.path.exists(filePath):
        self.set_headers(404)
        string="File : '" + filePath + "' not found."
        self.wfile.write(string.encode("UTF-8"))
      else:
        self.set_headers(500)
    # POST
    def do_POST(self):
        fp=self.rfile
        length = int(self.headers.get_all('content-length')[0])
        headers=self.headers
        self.set_headers(200)
        f = open("test", 'wb')
        f.write(fp.read(length))
        f.close()
    def do_DELETE(self):
        self._set_headers()
        self.wfile.write(b"<html><body><h1>delete!</h1></body></html>")

# run server
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", port), handler)
print("Serving at port", port)
try:
  httpd.serve_forever()
except KeyboardInterrupt:
  sys.exit(0)
