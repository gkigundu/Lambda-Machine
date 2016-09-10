#!/usr/bin/env python3

# Manages cluster and deposits scripts. Maintains cluster infromation
# Specifications :
#       1 per cluster

import sys, os
import re
import http.server
import socketserver
import socket
import json
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
    lu.log("Starting Master.")
    master = Master()
    broadcastListener = lu.nodeDiscovery("Lambda-M", ("Master_scriptRec",master.port))
    lu.log("Master initialized.")

# ==========================
#   Master
# ==========================
class Master:
    # This object represents the master entity. It instantiates all of the networking instruments used for distributing programs across the network. 
    def __init__(self):
        self.addr=lu.getAddr()
        socketserver.TCPServer.allow_reuse_address = True
        scriptPostHTTP = socketserver.TCPServer((self.addr, 0), jsonPostHandler)    # HTTP
        self.port=str(scriptPostHTTP.server_address[1])
        receiveScriptThread = threading.Thread(target=self._threadServe, args = (scriptPostHTTP,)).start()  # serve HTTP in thread
        lu.log("Serving HTTP Post Script @ " + str(self.addr) + ":" + str(self.port))
    def _threadServe(self, httpd):
        httpd.serve_forever()


class jsonPostHandler(http.server.BaseHTTPRequestHandler):
    #This module allows for the posting of JSON files concerning programs to execute. When the master receives a JSON file it will purchase it and use the content to build a programs table. it  also provides the functionality to view statistics on the cluster. This mechanism Works in conjunction with Receiving TCP socket and a sending TCP socket to distribute programs to Lambda-Minion nodes.
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
            # parse data to json
            data = self.rfile.read(int(length)).decode("UTF-8")
            data = json.loads(data)
            nodes = data["nodes"]
            script = str(data["script"])
            # send to specified minion
            for i in nodes:
                dest = lu.getAddrOf(i)
                lu.log("Sending script to " + i + ":" + str(dest))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(dest)
                sock.sendto(script.encode("UTF-8"), dest)  # the minion server
                sock.close()
        else:
            self.setHeaders(500)
main()
