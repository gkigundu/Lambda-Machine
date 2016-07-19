#!/usr/bin/env python3

import sys, os
import calendar, time
import threading, socket
import socketserver, http.server

filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# args=sys.argv[1:]
# for i in range(len(args)):
#     if (args[i] == "-p"):
#         port = int(args[i+1])
#     if (args[i] == "-a"):
#         addr = str(args[i+1])

table = None
class networkTable():
    # stores all of the active hosts on the network.
    networkTable=None
    def __init__(self):
        self.networkTable=[]
    def updateEntry(self, ip, name, time):
        updated = 0
        for i in range(0, len(self.networkTable)):
            if(self.networkTable[i][1] == name):
                self.networkTable[i][0] = ip
                self.networkTable[i][2]=time
                updated = 1
            if(updated == 1):
                break
        if(updated == 0):
            self.networkTable.append([ip, name, time])
    def getTable(self):
        return self.networkTable

def main():
    global table
    table = networkTable()
    # get messages over UDP to update networkTable
    broadcastListener = lu.nodeDiscovery("omega")
    broadcastListener.listen()
    tableRequestObj = tableReqest()
    while 1 :
        msg = broadcastListener.getMsg()
        if msg != None:
            info=msg.split(" ")
            table.updateEntry(info[0], info[1], int(calendar.timegm(time.gmtime())))

# implement a network handler for handling network table requests.
class tableReqest():
  addr=lu.getAddr()
  port=lu.ports["omega"]
  def __init__(self):
    socketserver.TCPServer.allow_reuse_address = True
    tableRequestServer = socketserver.TCPServer((self.addr, self.port), tableRequestHandler)
    broadcastThread = threading.Thread(target=self._threadServe, args = (tableRequestServer,))
    broadcastThread.start()
    lu.log(" Serving @ " + str(self.addr) + ":" + str(self.port))
  def _threadServe(self, httpd):
    httpd.serve_forever()
class tableRequestHandler(http.server.BaseHTTPRequestHandler):
    def setHeaders(self, code):
        self.send_response(code)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def do_GET(self): # check if contained to directory
        self.setHeaders(200)
        self.wfile.write(str(table.getTable()).encode("UTF-8"))
main()
