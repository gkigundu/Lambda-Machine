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
import tempfile
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
global progTable
def main():
    global progTable
    lu.log("Starting Master.")
    progTable = ProgTable()
    master = Master()
    broadcastListener = lu.nodeDiscovery("Lambda-M", master.getPorts())
    lu.log("Initialized")

# ==========================
#   Program Table
# ==========================
class ProgTable:
    table=None
    def __init__(self):
        self.table=[]
    def updateEntry(self, entry):
        # print(self.getTable())
        try :
            entry = json.loads(entry)
        except :
            lu.log("Failed to load json into prog table")
            return 1
        for i in self.table:
            if(i["Hash"] == entry["Hash"]):
                self.table.remove(i)
                lu.log("deleted table entry")
        self.table.append(entry) # append to table if entity does not exist
        lu.log("Added table entry")
        return 0
    def getTable(self):
        return json.dumps(self.table)
    def getProgByHash(self, fileHash):
        entry=None
        for i in self.table:
            if (fileHash == i["Hash"]):
                entry=i
        return entry
# ==========================
#   Master
# ==========================
class Master:
    # This object represents the master entity. It instantiates all of the networking instruments used for distributing programs across the network.
    def __init__(self):
        self.addr=lu.getAddr()
        self.TCP_ProgramListener = lu.TCP_BackgroundProcess(self.addr, programBinaryHandler).listen()
        self.HTTP_JSONListener = lu.TCP_BackgroundProcess(self.addr, jsonPostHandler).listen()
    def getPorts(self):
        return (("Master_programRec",self.TCP_ProgramListener.getListenPort()),
                ("Master_JSONpost",self.HTTP_JSONListener.getListenPort()))
class programBinaryHandler(socketserver.BaseRequestHandler): # TCP
    #This handler waits to receive binary program data. It will then hash the data and reference the process table to Determine the intent of the user. It works in conjunction with the JSON post Handler to forward the process to the minion nodes.
    global progTable
    def handle(self):
        lu.log("Receiveing binary program.")
        fp = tempfile.NamedTemporaryFile()
        data = self.request.recv(1024)
        while data:
            fp.write(data)
            data = self.request.recv(1024)
        lu.log("Finished Receiveing binary program.")
        fp.seek(0)
        fileHash = lu.getHash(fp.name)
        lu.log("Hashed Program : " + fileHash)
        # print(progTable.getTable())
        progEntry = progTable.getProgByHash(fileHash)
        for i in progEntry["nodes"]:
            node=lu.getNodeByName(i)
            lu.sendFile ( fp.name , (node["addr"], int(node["minion_scriptrec"]))) ## SEND DATA TO NODES
        fp.close()
        lu.log("Finished sending binary program.")

class jsonPostHandler(http.server.BaseHTTPRequestHandler): # HTTP
    #This handler allows for the posting of JSON files concerning programs to execute. When the master receives a JSON file it will purchase it and use the content to build a programs table. it  also provides the functionality to view statistics on the cluster. This mechanism Works in conjunction with Receiving TCP socket and a sending TCP socket to distribute programs to Lambda-Minion nodes.
    properPath=str([lu.paths[x] for x in [m.group(0) for l in lu.paths for m in [re.compile("^master_.*").search(l)] if m]] ) # Gets list of paths from lu.paths based on regex
    global progTable
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
        elif(self.path == lu.paths["master_progTable"]):
            self.setHeaders(200)
            self.wfile.write(str(progTable.getTable()).encode("UTF-8"))
        else:
            self.setHeaders(500)
    def do_POST(self):
        lu.log("Handling the Post to : " + self.path)
        if(self.path == lu.paths["master_postScript"]):
            length = self.headers['content-length']
            # parse data to json
            data = self.rfile.read(int(length)).decode("UTF-8")
            progTable.updateEntry(data)
            self.setHeaders(200)
        else:
            self.setHeaders(500)
main()
