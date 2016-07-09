#!/bin/env python3

# Difficulties:
#	 posting data to server using a form


import http.server
import socketserver
import signal
import sys, os, re
import cgi

# debuging
import cgitb
cgitb.enable()

# Global Defaults
port = 8000
addr = "127.0.0.1"
codeDir = "codeScrolls"

# get args
args=sys.argv[1:]
for i in range(len(args)):
	if (args[i] == "-p"):
		port = int(args[i+1])
	if (args[i] == "-a"):
		addr = str(args[i+1])

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
		filePath=re.sub("%20"," ",filePath)
		filePath=re.sub("/+","/",filePath)
		if os.path.isfile(filePath):
			self.set_headers(200)
			f = open(filePath, 'rb')
			try:
				data = f.read(50)
				while (len(data) > 0):
					self.wfile.write(data)
			finally:
				f.close()
		if os.path.isdir(filePath):
			index=os.path.join(filePath,"index.html")
			if os.path.isfile(index):
				self.set_headers(200)
				f = open(index, 'rb')
				bufferSize=50
				try:
					data = f.read(bufferSize)
					while (len(data) > 0):
						print(data)
						self.wfile.write(data)
						data = f.read(bufferSize)
				finally:
					f.close()
			#	 for i in f:
			#	 self.wfile.write(i) # .encode("UTF-8")
			#	 f.close
			else:
				for i in os.listdir(filePath):
					i = "<a href=\'" + self.path + i + "\'>"+i+"</a></br>"
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
		filePath=re.sub("^/",os.getcwd()+"/",self.path)
		length = int(self.headers.get_all('content-length')[0])
		print(length)
		self.set_headers(200)
		if(length > 0):
			f = open(filePath, 'wb')
			f.write(fp.read(length))
			f.close()
		# self.redirect("/")
	def redirect(self, dest):
		html1='''
			<!DOCTYPE HTML>
			<html lang="en-US">
			 <head>
				<meta charset="UTF-8">
				<script type="text/javascript">
					 window.location = " '''
		html2=''' ";
				 </script>
			</head>
			</html>
		'''
		html = html1 + dest + html2
		self.wfile.write(html.encode("UTF-8"))
	def do_DELETE(self):
		self._set_headers()
		self.wfile.write(b"<html><body><h1>delete!</h1></body></html>")

# run server
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer((addr, port), handler)
print("<log> Serving @ " + str(addr) + ":" + str(port))
try:
	httpd.serve_forever()
except KeyboardInterrupt:
	sys.exit(0)
