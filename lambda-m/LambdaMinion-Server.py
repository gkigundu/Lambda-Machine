#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

import sys, os
import urllib.request
import threading
import tempfile
import time
import socketserver

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
    lu.log(myMinion)
    # start broadcasting his address
    while ( not myMinion.getPorts()[0][1] ):
        time.sleep(.5)
    broadcaster = lu.nodeDiscovery("Lambda-m." + myMinion.ID, myMinion.getPorts() )
# ==========================
#   Minion Object
# ==========================
class Minion():
    ID=None
    listenPort=None
    def __init__(self):
        self.addr=lu.getAddr()
        self.OmegaAddr=lu.getOmegaAddr()
        self.ID = lu.getHTTP(self.OmegaAddr, lu.getPort("omega_tableReq"), lu.paths["omega_MinionTable"])
        self.TCP_ScriptListener = lu.TCP_BackgroundProcess(self.addr, MinionTCP_Handler).listen()
    def __str__(self):
        return "Minion(" + self.ID + ") @ " + self.addr + " (" + str(self.getPorts()) + ")"
    def getPorts(self):
        return (("minion_scriptRec", self.TCP_ScriptListener.getListenPort()),)
class MinionTCP_Handler(socketserver.BaseRequestHandler):   # handler to deposit script
    def handle(self):
        lu.log("Receiveing binary program.")
        fp = tempfile.NamedTemporaryFile()
        data = self.request.recv(1024)
        while data:
            fp.write(data)
            data = self.request.recv(1024)
        fp.seek(0)
        fileHash = lu.getHash(fp.name)
        lu.log("Finished Receiveing binary program. Hash : " + fileHash)
        fp.close()


# this class runs the script it receives and outputs data to database
# class executer:
#     # run the program
#     def run:
#
#     # send output to database
#     def databaseInterface:

main()
