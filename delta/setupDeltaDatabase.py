#!/usr/bin/env python3

import urllib.request
import sys, os, zipfile
sys.path.append("..")
import lambdaUtils as lu

port=8000
addr="127.0.0.1"
urlToGet="https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.3.4/elasticsearch-2.3.4.zip"
databaseDir="elastic"
outputZip="master.zip"

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
            zip_ref.extractall(".")
        lu.log("Removing zip file.")
        os.remove(outputZip)
        lu.log("Set up elastic sucessfully.")
except IOError as e:
    lu.error("Write error", e)
