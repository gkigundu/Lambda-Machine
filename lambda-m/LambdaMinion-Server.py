#!/usr/bin/env python3

import sys, os
import socket
import urllib.request
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

args=sys.argv[1:]
for i in range(len(args)):
    if (args[i] == "-p"):
        port = int(args[i+1])
    if (args[i] == "-a"):
        addr = str(args[i+1])

def main():
    myMinion = minion()
    print(myMinion.name)
    print(myMinion.omegaSerLoc)
    # start broadcasting my address
    broadcastListener = lu.nodeDiscovery("Lambda-m." + getMinionNumber())

class minion():
    UDPtimout=1
    def __init__(self):
        self.port=lu.ports["lambda-m"]
        self.addr=lu.getAddr()
        self.omegaSerLoc = self._getOmegaSerLoc()
        self.name = self._getName()
    # find out where the Omega Server is
    def _getName(self):
        # print('http://'+str(self.addr)+':'+str(self.port)+'/lambdaMinionNumber')
        with urllib.request.urlopen('http://'+str(self.addr)+':'+str(self.port)+'/lambdaMinionNumber') as response:
            html = response.read()
            print(html)
        return ""
    def _getOmegaSerLoc(self):
        omegaBroadcastReceived = False
        while not omegaBroadcastReceived:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.UDPtimout)
                sock.bind((self.addr, lu.ports["BroadcastListenerAddr"])) # UDP
                data, addr = sock.recvfrom(1024)
                print(data)
                if(len(data) > 0):
                    omegaBroadcastReceived = True
            except socket.timeout as e:
                lu.log("Could not get Omega Server Address. Retrying")
        # print(data)
        lu.log("Got Address : " + data)
        return data



# this class runs the scipt it receives and outputs data to database
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
#     # returns relevent information concerning Lambda-M
#     def listenForOmega:

main()
