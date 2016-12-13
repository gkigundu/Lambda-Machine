#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

import sys, os
import urllib.request
import threading
import tempfile
import time
import shutil
import shlex
import json
import socketserver
import os
import subprocess as subP
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
#   Global Variables
# ==========================
minionID=-1 # temporary mechanism # fix in beta to reduce tight coupling between classes

# ==========================
#   Main Function
# ==========================
def main():
    checkDependencies("unzip")
    # make a friendly minion to work for you
    myMinion = Minion()
    global minionID
    minionID = myMinion.ID
    lu.log(myMinion)
    # start broadcasting his address
    while ( not myMinion.getPorts()[0][1] ):
        time.sleep(.5)
    broadcaster = lu.nodeDiscovery("Lambda-m." + myMinion.ID, myMinion.getPorts() )
    lu.log("Initialized")
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
        lu.log("Receiving binary program.")
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


# ==========================
#   Dependencies for minions
# ==========================
def isInstalled( command):
    # this class runs the script it receives and outputs data to database
    for path in os.getenv("PATH").split(os.path.pathsep):
        fullPath = path + os.sep + command
        if os.path.exists(fullPath):
            return True
    return False
def checkDependencies(*prog):
    for i in prog:
        if not isInstalled(i):
            install(i)
def install( command):
    if isInstalled("apt"):
        blockSubProc("sudo apt-get install " + command)
    elif isInstalled("dnf"):
        blockSubProc("sudo dnf install " + command)
    elif isInstalled("yum"):
        blockSubProc("sudo yum install " + command)
    elif isInstalled("pacman"):
        blockSubProc("sudo pacman -S " + command)
# ==========================
#   Executer
# ==========================
def blockSubProc( command):
    p = subP.Popen(shlex.split(command))
    p.wait()
    lu.log("Command [" + command + "] Got return code : " + str(p.poll()))
class Executer:
    fileHash=None
    status=None
    # 0  : Executing
    # 1  : Completed Successfully
    # -1 : invalid file
    # -2 : No makefile
    # -3 : unzip not installed on node
    def __init__(self, filePath,fileHash, folder):
        self.fileHash=fileHash
        self.folder=folder
        self.filePath=filePath
        self.dataBase=lu.getAddrOf("delta") + ":" + str(lu.getPort("delta")) + "/"
        self.executeSetup = threading.Thread(target=self._executeSetup).start()
    def _executeSetup(self):
        # ZIP FILE
        if zipfile.is_zipfile(self.filePath) :
            ZipFile = zipfile.ZipFile(self.filePath)
            workingDir=os.path.dirname(self.filePath)
            subP.Popen(shlex.split("unzip -d " + workingDir + " " +self.filePath)).wait() # python unzip does not preserve file permissions so i must use linux unzip.
            # ZipFile.extractall(workingDir) # https://bugs.python.org/issue15795
            self.status=-2
            for root, dirs, files in os.walk(workingDir):
                for f in files:
                    if re.match("makefile", f ,flags=re.IGNORECASE):
                        self.filePath=os.path.join(root, f)
                        command = "make"
                        self.status=None
            if self.status == -2:
                lu.log("Could not find Makefile")
        # TEXT SCRIPT
        else:
            command = "bash " + os.path.basename(self.filePath)
        self.execute(command)
        shutil.rmtree(self.folder)
    def execute(self, command):
        lu.log("Executing : " + command)
        self.status=0
        self.proc = subP.Popen(shlex.split(command), cwd=os.path.dirname(self.filePath), universal_newlines=True, stdout=subP.PIPE, stderr=subP.PIPE)
        self.pollSubProc()
    def pollSubProc(self):
        global minionID
        stdout=["stdout", self.fileHash, str(minionID)] # location array passed to deltaPostData
        stderr=["stderr", self.fileHash, str(minionID)]
        metaInfo=["meta", self.fileHash, str(minionID)] # describes lines of output
        stdoutUpdate=["stdout", self.fileHash, str(minionID), "_update"]
        stderrUpdate=["stderr", self.fileHash, str(minionID), "_update"]
        stdIndex=1 # stdout index tracker
        errIndex=1 # stderr index tracker
        # init table
        data={int(0):""}
        lu.deltaPostData(data, stdout)
        lu.deltaPostData(data, stderr)
        lu.deltaPostData(data, metaInfo)
        while self.proc.poll() == None: # While process is running
            stdLine=None
            stdLine = self.proc.stdout.readline() # stdout
            if stdLine:
                data={"doc": {int(stdIndex):str(stdLine) }}
                lu.deltaPostData(data, stdoutUpdate)
                stdIndex += 1
            errLine=None
            errLine = self.proc.stderr.readline() # stderr
            if errLine:
                data={"doc": {int(errIndex):str(errLine) }}
                lu.deltaPostData(data, stderrUpdate)
                errIndex += 1
            if not stdLine and not errLine: # sleep if no output from either
                time.sleep(1)
		# get final output after proc ends
        for line in self.proc.stdout: # stdout
            data={"doc": {int(stdIndex):str(line) }}
            lu.deltaPostData(data, stdoutUpdate)
            stdIndex += 1
        for line in self.proc.stderr: # stderr
            data={"doc": {int(errIndex):str(line) }}
            lu.deltaPostData(data, stderrUpdate)
            errIndex += 1
        # update status
        self.status=self.proc.poll()
        lu.log("Executer Finished with status : " + str(self.status))
        # Update Meta Info
        data={"std":stdIndex,"err":errIndex,"code":self.status}
        lu.deltaPostData(data, metaInfo)
main()
