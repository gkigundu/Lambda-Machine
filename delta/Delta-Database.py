#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

# TO DO : auto install java. Maybe docker?

import urllib.request
import sys, os, zipfile
import shlex
import subprocess as subP

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
port=lu.getPort("delta")
addr=lu.getAddr()
urlToGet="https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.3.4/elasticsearch-2.3.4.zip"
databaseDir=filePath+"/elasticsearch-2.3.4"
outputZip=filePath+"/master.zip"

# ==========================
#   Elastic Sub Proc
# ==========================
def deltaStart():
    command = "bash bin/elasticsearch --network.host " + addr
    with subP.Popen(shlex.split(command), cwd=databaseDir, stdout=subP.PIPE, stderr=subP.PIPE, universal_newlines=True) as proc:
        for line in proc.stdout:
            print(line, end='')
        for line in proc.stderr:
            print(line, end='')
    lu.log("Delta Terminated.")

# ==========================
#   Main Function
# ==========================
def main():
    try:
        # setup elastic search
        if not os.path.exists(databaseDir):
            os.makedirs(databaseDir)
            req = urllib.request.urlopen(urlToGet)
            lu.log("Downloading elastic.")
            with open(outputZip, 'wb') as output:
                while True:
                    data = req.read(4096)
                    if data:
                        output.write(data)
                    else:
                        break
            lu.log("Unzipping elastic.")
            with zipfile.ZipFile(outputZip,"r") as zip_ref:
                zip_ref.extractall(filePath)
            lu.log("Removing zip file.")
            os.remove(outputZip)
            lu.log("Set up elastic successfully.")
        lu.log("Initialized")
        lu.log("Starting elastic.")
        lu.log("=================")
        deltaStart()
    except IOError as e:
        lu.error("Write error", e)
    # except KeyboardInterrupt as e:
    #     lu.log("Keyboard interrupt. Shutting Down.")
    #     proc.kill()
broadcaster = lu.nodeDiscovery("delta")
main()
