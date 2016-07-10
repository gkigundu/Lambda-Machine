#!/usr/bin/env python3

port = 8000
addr = "127.0.0.1"

args=sys.argv[1:]
for i in range(len(args)):
    if (args[i] == "-p"):
        port = int(args[i+1])
    if (args[i] == "-a"):
        addr = str(args[i+1])

class network:
    # gets a listing of Lambda-m that are connected
    def getMinorTableFromLambda-M:

    # gets execution status of all Lambda-m
    def getStatusFromLambda-m:

    # listen for alpha request. Returns status of Lamda-M and Lambda-m
    def listenForAlpha:
