#!/usr/bin/env python3

import sys
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

# this class runs the scipt it receives and outputs data to database
class executer:
    # run the program
    def run:

    # send output to database
    def databaseInterface:

class network:
    # receives a script from Lambda-M
    def listenForLambda-M:

    # requests a connection to Lambda-M, executes "listenForLambda-m" on Lambda-M
    def requestLambda-M:

    # returns relevent information concerning Lambda-M
    def listenForOmega:
