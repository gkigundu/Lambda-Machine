#!/usr/bin/env python3

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
        self.port=lu.ports["lambda-m"]
        self.addr=lu.getAddr()
        self.OmegaAddr=lu.getOmegaAddr(self.addr)
        self.ID = self._getMinionID()
        self._startScriptReceival = threading.Thread(target=self._startScriptReceival).start()
    def _startScriptReceival(self):
        self.TCPScriptReceival=socketserver.TCPServer((self.addr, 0), MinionTCP_Handler)
        self.listenPort=str(self.TCPScriptReceival.server_address[1])
        lu.log("Minion " + str(self.ID) +" got listening port : " + self.listenPort)
        self.TCPScriptReceival.serve_forever()
    def _getMinionID(self):
        requestURL='http://'+str(self.OmegaAddr)+':'+str(lu.ports["omega"])+'/lambdaMinionNumber'
        lu.log("Requesting " + requestURL)
        with urllib.request.urlopen(requestURL) as response:
            minionID = response.read().decode("UTF-8")
            lu.log("Got Minion ID : "+ minionID)
        return minionID
class MinionTCP_Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # self.request.sendall(self.data.upper())



# this class runs the script it receives and outputs data to database
# class executer:
#     # run the program
#     def run:
#
#     # send output to database
#     def databaseInterface:
#
# class network:
#     # receives a script from Lambda-M
#     def listenForLambda-M:
#
#     # requests a connection to Lambda-M, executes "listenForLambda-m" on Lambda-M
#     def requestLambda-M:
#
#     # returns relevant information concerning Lambda-M
#     def listenForOmega:

main()
