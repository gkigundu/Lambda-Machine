#!/usr/bin/env python3

import sys
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

class minions:
    minionTable = []

class network:
    # Receive a program to be redirected to Lambda-m
    def listenForAlpha:

    # receive connections from Lambda-m
    def listenForLambda-m:

    # returns relevent information concerning Lambda-M
    def listenForOmega:
