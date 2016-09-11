#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

import sys, os
import urllib.request
import threading
import tempfile
import time
import shutil
import socketserver
import os
import subprocess
import zipfile
import re

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
        try:
            folder = tempfile.mkdtemp()
            fp = open(tempfile.mkstemp(dir=folder)[1], 'wb')
            data = self.request.recv(1024)
            while data:
                fp.write(data)
                data = self.request.recv(1024)
            fp.seek(0)
            fileHash = lu.getHash(fp.name)
            lu.log("Finished Receiveing binary program. Hash : " + fileHash)
            fileExecuter = Executer(fp.name, fileHash, folder)
        finally:
            fp.close()


# this class runs the script it receives and outputs data to database
class Executer:
    fileHash=None
    status=None
    # 0  : Executing
    # 1  : Completed Sucessfully
    # -1 : invalid file
    # -2 : No makefile
    def __init__(self, filePath,fileHash, folder):
        self.fileHash=fileHash
        self.folder=folder
        self.filePath=filePath
        self.executeSetup = threading.Thread(target=self._executeSetup).start()
    def _executeSetup(self):
        if zipfile.is_zipfile(self.filePath) :
            ZipFile = zipfile.ZipFile(self.filePath)
            workingDir=os.path.dirname(self.filePath)
            ZipFile.extractall(workingDir)
            self.status=-2
            for root, dirs, files in os.walk(workingDir):
                for f in files:
                    if re.match("makefile", f ,flags=re.IGNORECASE):
                         self.executeMake(os.path.join(root, f))
            if self.status == -2:
                lu.log("Could not find make file")
        else:
            self.executeBash(filePath)
        lu.log("Executer Finished with status : " + str(self.status))
        shutil.rmtree(self.folder)
    def executeBash(self, f):
        lu.log("Executer Initialized with file : " + f)
        command = "bash -c cd " + os.path.dirname(f) + " && ./" + os.path.basename(f)
        lu.log("Exicuting : " + command)
        self.status=0
        p = subprocess.Popen(command.split(" "))
        # execute HERE
        self.status=1
    def executeMake(self, f):
        lu.log("Executer Initialized with file : " + f)
        command = "bash -c cd " + os.path.dirname(f) + " && make"
        lu.log("Exicuting : " + command)
        self.status=0
        p = subprocess.Popen(command.split(" "))
        p.wait(timeout=15)
        print(p.communicate(timeout=15))
        print(p.returncode)
        # execute HERE
        self.status=1


main()
