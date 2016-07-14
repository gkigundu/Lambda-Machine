#!/usr/bin/env python3

import sys
sys.path.append("..")
import lambdaUtils

port = 80000
addr = "127.0.0.1"

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
