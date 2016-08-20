#!/usr/bin/env python3

import sys, os
import socket
import urllib.request

# ==========================
#   Import lambdaUtils
# ==========================
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# ==========================
#   Parse Args
# ==========================
args=sys.argv[1:]
for i in range(len(args)):
    if (args[i] == "-p"):
        port = int(args[i+1])
    if (args[i] == "-a"):
        addr = str(args[i+1])

# ==========================
#   Main Function
# ==========================
def main():
    # make a friendly minion to work for you
    myMinion = minion()
    # start broadcasting his address
    broadcaster = lu.nodeDiscovery("Lambda-m." + myMinion.ID)

# ==========================
#   Minion Object
# ==========================
class minion():
    ID=None
    OmegaAddr=None
    def __init__(self):
        self.port=lu.ports["lambda-m"]
        self.addr=lu.getAddr()
        self.OmegaAddr=lu.getOmegaAddr(self.addr)
        self.ID = self._getMinionID()
    # find out where the Omega Server is
    def _getMinionID(self):
        # print('http://'+str(self.addr)+':'+str(self.port)+'/lambdaMinionNumber')
        requestURL='http://'+str(self.OmegaAddr)+':'+str(lu.ports["omega"])+'/lambdaMinionNumber'
        lu.log("Requesting " + requestURL)
        with urllib.request.urlopen(requestURL) as response:
            minionID = response.read().decode("UTF-8")
            lu.log("Got Minion ID : "+ minionID)
        return minionID




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
