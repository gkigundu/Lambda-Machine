#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

import sys, os
import socket, socketserver
import urllib.request
import threading
import time

# ==========================
#   Import lambdaUtils
# ==========================
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# ==========================
#   Main Function
# ==========================
def main():
    # make a friendly minion to work for you
    myMinion = Minion()
    # start broadcasting his address
    while ( not myMinion.listenPort ):
        time.sleep(.5)
    broadcaster = lu.nodeDiscovery("Lambda-m." + myMinion.ID, str(myMinion.listenPort))
# ==========================
#   Minion Object
# ==========================
class Minion():
    ID=None
    OmegaAddr=None
    TCPScriptReceival=None
    listenPort=None
    def __init__(self):
        # self.port=lu.ports["lambda-m"]
        self.addr=lu.getAddr()
        self.OmegaAddr=lu.getOmegaAddr()
        self.ID = self._getMinionID()
        self._startScriptReceival = threading.Thread(target=self._startScriptReceival).start()
    def _startScriptReceival(self):
        self.TCPScriptReceival=socketserver.TCPServer((self.addr, 0), MinionTCP_Handler)
        self.listenPort=str(self.TCPScriptReceival.server_address[1])
        lu.log("Minion " + str(self.ID) +" is waiting for scripts at TCP socket : " + self.addr+":"+self.listenPort)
        self.TCPScriptReceival.serve_forever()
    def _getMinionID(self):
        requestURL='http://'+str(self.OmegaAddr)+':'+str(lu.getPort("omega_tableReq"))+lu.paths["omega_MinionTable"]
        lu.log("Requesting " + requestURL)
        with urllib.request.urlopen(requestURL) as response:
            minionID = response.read().decode("UTF-8")
            lu.log("Got Minion ID : "+ minionID)
        return minionID
class MinionTCP_Handler(socketserver.BaseRequestHandler):   # handler to deposit script
    def handle(self):
        print("receiveing")
        script=""
        data = self.request.recv(1024)
        while data:
            print(data)
            script += data.decode("UTF-8")
            data = self.request.recv(1024)
        print("minion data : " + script)
        # !!! get script and execute !!!

# this class runs the script it receives and outputs data to database
# class executer:
#     # run the program
#     def run:
#
#     # send output to database
#     def databaseInterface:

main()
