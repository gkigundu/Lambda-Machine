#!/usr/bin/env python3

# Specifications :
#       1/Many per cluster

# TO DO : auto install java. Maybe docker?

import urllib.request
import sys, os, zipfile
import shlex
import subprocess

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
    command = "bash " + databaseDir + "/bin/elasticsearch --network.host " + addr
    proc = subprocess.Popen(shlex.split(command), cwd=databaseDir, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while not proc.poll():
        try:        print(proc.communicate(timeout=1))
        except:     pass
    status=proc.poll()
    lu.log("Finished with status : " + str(status))

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
    except KeyboardInterrupt as e:
        lu.log("Keyboard interrupt. Shutting Down.")
        proc.kill()
broadcaster = lu.nodeDiscovery("delta")
main()
