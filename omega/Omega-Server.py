#!/usr/bin/env python3

# Specifications :
#       1 per cluster

import sys, os
import re
import calendar, time
import threading, socket
import socketserver, http.server
import queue
import json

# ==========================
#   Import lambdaUtils
# ==========================
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# ==========================
#   Network Table
# ==========================
# stores all of the active hosts on the network.
table = None
class networkTable():
    minionNumber=0
    networkTable=None
    def __init__(self):
        self.networkTable=[]
    def getMinionNumber(self):
        # returns nex available minion number
        self.minionNumber=self.minionNumber+1
        return self.minionNumber
    def updateEntry(self, entry):
        #print(entry)
        try :
            entry = json.loads(str(entry))
        except :
           return 1

        entry["epoch"]=int(calendar.timegm(time.gmtime()))  # BUG : not getting updated
        for i in self.networkTable:
            if(i["name"] == entry["name"]):
                i = entry
                return 0
        self.networkTable.append(entry) # append to tabe if entity does not exist
        return 0
    def getTable(self):
        return json.dumps(self.networkTable)

# ==========================
#   Table Requests
# ==========================
# implements a network handler for handling network table requests. returns a python list with http headers. TCP based
class tableRequest():
    def __init__(self):
        socketserver.TCPServer.allow_reuse_address = True
        tableRequestServer = socketserver.TCPServer((lu.getAddr(), 0), tableRequestHandler)    # HTTP
        broadcastThread = threading.Thread(target=self._threadServe, args = (tableRequestServer,)).start()  # serve HTTP in thread
        self.port = tableRequestServer.server_address[1]
        lu.log("Serving HTTP Get Table Requests @ " + str(lu.getAddr()) + ":" + str(self.port))
    def _threadServe(self, httpd):
        httpd.serve_forever()
class tableRequestHandler(http.server.BaseHTTPRequestHandler):
    properPath=str([lu.paths[x] for x in [m.group(0) for l in lu.paths for m in [re.compile("^omega_.*").search(l)] if m]] ) # perfectly conveluded. Gets list of paths from lu.paths based on regex
    def setHeaders(self, code):
        self.send_response(code)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def do_GET(self): # check if contained to directory
        lu.log("Handling the Request to : " + self.path)
        if(self.path == lu.paths["omega_Table"]):
            self.setHeaders(200)
            self.wfile.write(table.getTable().encode("UTF-8"))
        elif(self.path == lu.paths["omega_MinionTable"]):
            self.setHeaders(200)
            self.wfile.write(str(table.getMinionNumber()).encode("UTF-8"))
        else:
            self.setHeaders(500)

# ==========================
#   OmegaNodeDiscovery
# ==========================
class OmegaNodeDiscovery(lu.nodeDiscovery):
    def __init__(self, name, *ports):
        self.name=name
        self.addr=lu.getAddr()
        self.jsonInfo={}
        for i in ports:
            self.jsonInfo[i[0].lower()]=i[1]
        self.jsonInfo["name"]=self.name
        self.jsonInfo["addr"]=self.addr
        # only one listener per computer. This will be used by the omega server to broadcast its address. UDP
        #      otherwise : " OSError: [Errno 98] Address already in use "
        self.readBuffer=queue.Queue(maxsize=self.queueSize)
        # listens to the broadcast messages and adds them to queue. UDP
        listenThread = threading.Thread(target=self._listen, args = ())
        listenThread.start()
        # # broadcast the omega server's address on subnet
        broadcastThread = threading.Thread(target=self._broadcast, args = (lu.getPort("OmegaBroadcast"),))
        broadcastThread.start()
    def _broadcast(self, port):
          # continually sends out ping messages with the clients ip addr and name. UDP
        msg=str(self.addr)+" "+str(self.jsonInfo["omega_tablereq"])
        lu.log("Broadcasting omega address on : " + str(lu.getPort("OmegaBroadcast")) )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.alive:
            #lu.log("Broadcasting omega address on : " + str(lu.getPort("OmegaBroadcast"]) )
            sock.sendto(msg.encode("UTF-8"), (lu.getBroadcast(), lu.getPort("OmegaBroadcast")))
            time.sleep(1)
    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.addr, lu.getPort("OmegaListen"))) # UDP
        lu.log("Binded and listening on " + str((self.addr, lu.getPort("OmegaListen"))))
        while self.alive:
            data, addr = sock.recvfrom(1024)
            time.sleep(.1)
            if not self.readBuffer.full():
                self.readBuffer.put(data.decode("UTF-8"))
            else:
                self.readBuffer.get()
                lu.log("Queue overflow. Dropping datagram.")
    def getMsg (self):
    # returns the most recent broadcast message in the queue
        if not self.readBuffer.empty():
            return self.readBuffer.get()
        else:
            return None
# ==========================
#   Main Method
# ==========================
def main():
    # make network Table
    global table
    table = networkTable()
    # get messages over UDP to update networkTable
    tableRequestObj = tableRequest()
    broadcastListener = OmegaNodeDiscovery("omega", ("omega_tableReq", tableRequestObj.port))
    # get UDP pings from network to create Network table entries
    lu.log("Getting UDP network pings on : " + str(broadcastListener.broadcastAddr) + ", from port : " + str(lu.getPort("OmegaListen")))
    while broadcastListener.alive:
        table.updateEntry(json.dumps(broadcastListener.jsonInfo))
        msg = broadcastListener.getMsg()
        if msg:
            table.updateEntry(msg)
        else:
            time.sleep(1)
            print(table.getTable())
main()
