#!/usr/bin/env python3

import sys, os
import calendar, time
import threading, socket
import socketserver, http.server
import queue

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
    def updateEntry(self, ip, name, time):
        for i in range(0, len(self.networkTable)):
            if(self.networkTable[i][1] == name): # update existing entities
                self.networkTable[i][0] = ip
                self.networkTable[i][2] = time
                updated = 1
                return
        self.networkTable.append([ip, name, time]) # append to tabe if entity does not exist
        return
    def getTable(self):
        return self.networkTable

# ==========================
#   Table Requests
# ==========================
# implements a network handler for handling network table requests. returns a python list with http headers. TCP based
class tableRequest():
  addr=lu.getAddr()
  port=lu.ports["omega"]
  def __init__(self):
    socketserver.TCPServer.allow_reuse_address = True
    tableRequestServer = socketserver.TCPServer((self.addr, self.port), tableRequestHandler)
    broadcastThread = threading.Thread(target=self._threadServe, args = (tableRequestServer,))
    broadcastThread.start()
    lu.log(" Serving HTTP Get Table Requests @ " + str(self.addr) + ":" + str(self.port))
  def _threadServe(self, httpd):
    httpd.serve_forever()
class tableRequestHandler(http.server.BaseHTTPRequestHandler):
    properPath="/table /lambdaMinionNumber"
    def setHeaders(self, code):
        self.send_response(code)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def do_GET(self): # check if contained to directory
        lu.log("Handling the Request to : " + self.path)
        if(self.path == "/"):
            self.setHeaders(200)
            self.wfile.write(str("Please Request a proper path. Try : "+self.properPath).encode("UTF-8"))
        elif(self.path == "/table"):
            self.setHeaders(200)
            self.wfile.write(str(table.getTable()).encode("UTF-8"))
        elif(self.path == "/lambdaMinionNumber"):
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
        self.addr=lu.getAddr()
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
        while self.alive:
            for addr in self.broadcastAddr:
                sock.sendto(msg.encode("UTF-8"), (str(addr), port))
        sleep(self.sleepTime)
    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.addr, lu.ports["OmegaListen"])) # UDP
        while self.alive:
            data, addr = sock.recvfrom(1024)
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
    # get UDP pings from network to create Network table entries
    lu.log("Getting UDP network pings on : " + str(broadcastListener.broadcastAddr) + ", from port : " + str(lu.ports["OmegaListen"]))
    while 1 :
        msg = broadcastListener.getMsg()
        if msg != None:
            info=msg.split(" ")
            table.updateEntry(info[0], info[1], int(calendar.timegm(time.gmtime())))


main()
