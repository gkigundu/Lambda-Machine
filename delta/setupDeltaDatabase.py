#!/usr/bin/env python3

import urllib.request
import sys, os, zipfile
import subprocess

filePath=os.path.abspath(os.path.join(os.path.dirname(__file__)))
rootPath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(rootPath)
import lambdaUtils as lu
os.chdir(filePath)

port=8000
addr="127.0.0.1"
urlToGet="https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.3.4/elasticsearch-2.3.4.zip"
databaseDir=filePath+"/elasticsearch-2.3.4"
outputZip=filePath+"/master.zip"

def main():
    try:
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
            lu.log("Set up elastic sucessfully.")
        lu.log("Starting elastic.")
        lu.log("=================")

        command = "bash " + databaseDir + "/bin/elasticsearch"
        command = command.split(" ")
        proc = subprocess.Popen(command , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # run server here to respond to http get requests concerning proc
        while (1):
            for line in iter(proc.stdout.readline,''):
                if(len(line) > 0):
                    print(line.decode("utf-8").rstrip() )
    except IOError as e:
        lu.error("Write error", e)
    except KeyboardInterrupt as e:
        lu.log("Keyboard Interupt. Shutting Down.")
        proc.kill()
main()

