#!/usr/bin/env python3

# Manages cluster and deposits scripts. Maintains cluster infromation
# Specifications :
#       1 per cluster

import sys, os
import re
import http.server
import socketserver
import threading

# ==========================
#   Import lambdaUtils
# ==========================
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# ==========================
#   Main function
# ==========================
def main():
    broadcastListener = lu.nodeDiscovery("Lambda-M")
    lu.log("Starting Master.")
    master = Master()
    lu.log("Master initialized.")

# ==========================
#   Master
# ==========================
# Receive a program to be redirected to Lambda-m
class Master:
    def __init__(self):
        self.port=lu.ports["lambda-M"]
        self.addr=lu.getAddr()
        socketserver.TCPServer.allow_reuse_address = True
        scriptPostHTTP = socketserver.TCPServer((self.addr, self.port), scriptPostHandler)    # HTTP
        receiveScriptThread = threading.Thread(target=self._threadServe, args = (scriptPostHTTP,)).start()  # serve HTTP in thread
        lu.log("Serving HTTP Post Script @ " + str(self.addr) + ":" + str(self.port))
    def _threadServe(self, httpd):
        httpd.serve_forever()
class scriptPostHandler(http.server.BaseHTTPRequestHandler):
    properPath=str([lu.paths[x] for x in [m.group(0) for l in lu.paths for m in [re.compile("^master_.*").search(l)] if m]] ) # Gets list of paths from lu.paths based on regex
    def setHeaders(self, code):
        self.send_response(code)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        lu.log("Handling the Request to : " + self.path)
        if(self.path == "/"):
            self.setHeaders(200)
            self.wfile.write(str("Please Request a proper path. Try : "+self.properPath).encode("UTF-8"))
        elif(self.path == lu.paths["master_ClusterStat"]):
            self.setHeaders(200)
            # !!! Gather minion statistics and send to requester !!!
            self.wfile.write(str("Still need to implement").encode("UTF-8"))
        else:
            self.setHeaders(500)
    def do_POST(self):
        if(self.path == lu.paths["master_postScript"]):
            self.setHeaders(200)
            length = self.headers['content-length']
            data = self.rfile.read(int(length)).decode("UTF-8")
            lu.log("Got Payload : \n" + data )
            # !!! Parse input into JSON !!!
            # !!! send to minion based off of json node info !!!
            #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #sock.sendto(data.encode("UTF-8"), ("192.168.1.145" , 53063)) # the minion server
            #sock.close()
        else:
            self.setHeaders(500)
main()
