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

ADDR=lu.getAddr()

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
    def updateEntry(self, netList):
        for i in range(0, len(self.networkTable)):
            if(self.networkTable[i][1] == netList[1]): # name
                self.networkTable[i][0] = netList[0]   # ip
                self.networkTable[i][2] = netList[2]   # time
                updated = 1
                return
        self.networkTable.append(netList) # append to tabe if entity does not exist
        return
    def getTable(self):
        return self.networkTable

# ==========================
#   Table Requests
# ==========================
# implements a network handler for handling network table requests. returns a python list with http headers. TCP based
class tableRequest():
  addr=ADDR
  port=lu.ports["omega"]
  def __init__(self):
    socketserver.TCPServer.allow_reuse_address = True
    tableRequestServer = socketserver.TCPServer((self.addr, self.port), tableRequestHandler)    # HTTP
    broadcastThread = threading.Thread(target=self._threadServe, args = (tableRequestServer,)).start()  # serve HTTP in thread
    lu.log("Serving HTTP Get Table Requests @ " + str(self.addr) + ":" + str(self.port))
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
        if(self.path == "/"):
            self.setHeaders(200)
            self.wfile.write(str("Please Request a proper path. Try : "+self.properPath).encode("UTF-8"))
        elif(self.path == lu.paths["omega_Table"]):
            self.setHeaders(200)
            self.wfile.write(str(table.getTable()).encode("UTF-8"))
        elif(self.path == lu.paths["omega_TableJSON"]):
            self.setHeaders(200)
            tableJSON=[]
            for i in table.getTable():
                try:
                    tableJSON.append(dict({"name":i[1],"addr":i[0],"time":i[2],"port":i[3]})) # make this a better test
                except:
                    tableJSON.append(dict({"name":i[1],"addr":i[0],"time":i[2]}))

            self.wfile.write(str(json.dumps(tableJSON)).encode("UTF-8"))
        elif(self.path == lu.paths["omega_MinionTable"]):
            self.setHeaders(200)
            self.wfile.write(str(table.getMinionNumber()).encode("UTF-8"))
        else:
            self.setHeaders(500)

# ==========================
#   OmegaNodeDiscovery
# ==========================
class OmegaNodeDiscovery(lu.nodeDiscovery):
    def __init__(self, name):
        self.name=name
        self.addr=ADDR
        # only one listener per computer. This will be used by the omega server to broadcast its address. UDP
        #      otherwise : " OSError: [Errno 98] Address already in use "
        self.readBuffer=queue.Queue(maxsize=self.queueSize)
        # listens to the broadcast messages and adds them to queue. UDP
        listenThread = threading.Thread(target=self._listen, args = ())
        listenThread.start()
        # # broadcast the omega server's address on subnet
        broadcastThread = threading.Thread(target=self._broadcast, args = (lu.ports["OmegaBroadcast"],))
        broadcastThread.start()
    def _broadcast(self, port):
          # continually sends out ping messages with the clients ip addr and name. UDP
        msg=str(self.addr)+" "+str(self.name)
        lu.log("Broadcasting on port : " + str(port) )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # POTENTIAL MAJOR BUG : Test that this while loop does not overflow network Bandwidth 
        while self.alive:
            for addr in self.broadcastAddr:
                sock.sendto(msg.encode("UTF-8"), (str(addr), port))
            time.sleep(self.sleepTime)
    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.addr, lu.ports["OmegaListen"])) # UDP
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
    broadcastListener = OmegaNodeDiscovery("omega")
    tableRequestObj = tableRequest()
    table.updateEntry( [broadcastListener.addr, "omega", int(calendar.timegm(time.gmtime()))] )
    # get UDP pings from network to create Network table entries
    lu.log("Getting UDP network pings on : " + str(broadcastListener.broadcastAddr) + ", from port : " + str(lu.ports["OmegaListen"]))
    while broadcastListener.alive :
        table.updateEntry([broadcastListener.addr, "omega", int(calendar.timegm(time.gmtime()))])
        msg = broadcastListener.getMsg()
        if msg:
            info         =msg.split(" ")
            ipAddr       =info[0]
            name         =info[1]
            epochTime    =int(calendar.timegm(time.gmtime()))
            port         =None
            try:    port =info[2]
            except: pass
            info=[ipAddr, name, epochTime]
            if(port):
                info.append(port)
            table.updateEntry(info)
        else:
            time.sleep(1)
            print(table.getTable())
main()
