#!/usr/bin/env python3

# pushes data from alpha to minions

import sys
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

port=lu.ports["lambda-M"]
addr=lu.getAddr()

args=sys.argv[1:]
for i in range(len(args)):
    if (args[i] == "-p"):
        port = int(args[i+1])
    if (args[i] == "-a"):
        addr = str(args[i+1])

def main():
    broadcastListener = lu.nodeDiscovery("Lambda-M")

class network:
    # Receive a program to be redirected to Lambda-m
    def listenForAlpha:

    # returns relevent information concerning Lambda-M
    def listenForOmega:

main()
