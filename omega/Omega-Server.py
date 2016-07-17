#!/usr/bin/env python3

import sys, os
import calendar, time
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

port = 8000
addr = "127.0.0.1"

args=sys.argv[1:]
for i in range(len(args)):
    if (args[i] == "-p"):
        port = int(args[i+1])
    if (args[i] == "-a"):
        addr = str(args[i+1])

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
    def getTable():
        return self.networkTable

def main():
    table = networkTable()
    broadcastListener = lu.nodeDiscovery("omega")
    broadcastListener.listen()
    while 1 :
        msg = broadcastListener.getMsg()
        if msg != None:
            info=msg.split(" ")
            table.updateEntry(info[0], info[1], int(calendar.timegm(time.gmtime())))
# class network:
#     # gets execution status of all Lambda-m
#     def getStatusFromLambda-m:
#
#     # listen for alpha request. Returns status of Lamda-M and Lambda-m
#     def listenForAlpha:
main()
