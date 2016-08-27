#!/usr/bin/env python3

# pushes data from alpha to minions

import sys, os

# ==========================
#   Import lambdaUtils
# ==========================
filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

# ==========================
#   Init Setup
# ==========================
port=lu.ports["lambda-M"]
addr=lu.getAddr()

# ==========================
#   Main function
# ==========================
def main():
    master = Master()
    broadcastListener = lu.nodeDiscovery("Lambda-M")

# ==========================
#   Master
# ==========================
class Master:
    # Receive a program to be redirected to Lambda-m
    def receiveScript(self):
        print()
main()
