#!/usr/bin/env python3

# Specifications :
#       1 per Cluster/Network

import http.server
import socketserver
import signal
import urllib.request
import json

import sys, os, re
import cgi

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
if not os.path.exists(lu.paths["alpha_scripts"]):
    os.makedirs(lu.paths["alpha_scripts"])

# ==========================
#   Main user front end server
# ==========================
class HTTP_webpageHandler(http.server.BaseHTTPRequestHandler):
    # set http headers
    def setHeaders(self, code):
        self.send_response(code)
        self.send_header(b'Content-type', 'text/html')
        self.end_headers()
    def writeDataToHandler(self, readFile):
        f = open(readFile, 'rb')
        bufferSize=50
        try:
            data = f.read(bufferSize)
            while (len(data) > 0):
                self.wfile.write(data)
                data = f.read(bufferSize)
        finally:
            f.close()
    # GET
    def do_GET(self): # check if contained to directory
        lu.log("Get Request - " + self.path)
        filePath=re.sub("^/",os.getcwd()+"/",self.path)
        filePath=re.sub("%20"," ",filePath)
        filePath=re.sub("/+","/",filePath)
        pathSplit=[x for x in self.path.split("/") if x] # TODO : Restructure get using pathSplit
        if (self.path == lu.paths["alpha_nodeListing"]): # node
            requestURL='http://'+str(lu.getOmegaAddr())+':'+str(lu.getPort("omega_tableReq"))+lu.paths["omega_Table"]
            lu.log("Requesting " + requestURL)
            msg=None
            try:
                with urllib.request.urlopen(requestURL) as response:
                    self.setHeaders(200)
                    try:
                        msg = response.read().decode("UTF-8")
                        self.wfile.write(msg.encode("UTF-8"))
                    except:
                        lu.error("Could not parse routing table")
                        return 1
            except:
                lu.log("Could not get network table from Omega.")
        elif os.path.isfile(filePath):
            self.setHeaders(200)
            self.writeDataToHandler(filePath)
        elif os.path.isdir(filePath):
            index=os.path.join(filePath,"index.html")
            if os.path.isfile(index):
                self.setHeaders(200)
                self.writeDataToHandler(index)
            else:
                if(len(os.listdir(filePath))):
                    for i in os.listdir(filePath):
                        i = "<a href=\'" + self.path + "/" + i + "\'>"+i+"</a></br>"
                        self.wfile.write(i.encode("UTF-8"))
                else:
                    self.wfile.write("directory empty".encode("UTF-8"))
        elif pathSplit[0] == lu.paths["alpha_stdout"]:
            self.setHeaders(200)
            print(pathSplit)
        elif pathSplit[0] == lu.paths["alpha_stderr"]:
            self.setHeaders(200)
            print(pathSplit)
        elif not os.path.exists(filePath):
            self.setHeaders(404)
            string="File : '" + filePath + "' not found."
            lu.log(string)
            self.wfile.write(string.encode("UTF-8"))
        else:
            self.setHeaders(500)
    # POST
    def do_POST(self):
        lu.log("Post Request - " + self.path)
        pathroot=self.path.split("/")
        while "" in pathroot:
            pathroot.remove("")
        if(pathroot[0] == lu.paths["alpha_scripts"]): ## TEST : file upload
            lu.log("Uploading Script - " + self.path)
            fp=self.rfile
            filePath=re.sub("^/",os.getcwd()+"/",self.path)
            filePath=re.sub("%20"," ",filePath)
            length = int(self.headers.get_all('content-length')[0])
            self.setHeaders(200)
            if(length > 0):
                f = open(filePath, 'wb')
                f.write(fp.read(length))
                f.close()
        elif(self.path == lu.paths["alpha_postScript"]): # post to master
            masterAddr = lu.getAddrOf("Lambda-M")
            if not masterAddr:
                lu.log("Could not get Master Addr.")
                self.setHeaders(500)
            length = int(self.headers.get_all('content-length')[0])
            if(length > 0):
                # send json to master http post
                data = json.loads(self.rfile.read(length).decode("UTF-8"))
                data["FileLoc"]=lu.paths["alpha_scripts"] + "/" + data["script"]
                data["Hash"] = lu.getHash(data["FileLoc"])
                lu.log("Hashed Program : " + data["Hash"])
                lu.postHTTP(json.dumps(data),masterAddr,lu.getPort("Master_JSONpost"),lu.paths["master_postScript"])

                # send binary data to socket
                lu.sendFile(data["FileLoc"],(masterAddr,int(lu.getPort("Master_programRec"))))
                self.setHeaders(200)
            else:
                lu.log("Nothing to send to master")
        else:
            lu.log("Could not post " + self.path)

    # redirects a client using javascript
    def redirect(self, dest):
        html1='''
            <!DOCTYPE HTML>
            <html lang="en-US">
             <head>
                <meta charset="UTF-8">
                <script type="text/javascript">
                     window.location = " '''
        html2=''' ";
                 </script>
            </head>
            </html>
        '''
        html = html1 + dest + html2
        self.wfile.write(html.encode("UTF-8"))
    # deletes a script
    def do_DELETE(self):
        lu.log("Delete Request - " + self.path)
        self._setHeaders()
        self.wfile.write(b"<html><body><h1>delete!</h1></body></html>")

# ==========================
#   Iniitialize
# ==========================
try:
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer((lu.getAddr(),
    lu.getPort("alpha")), HTTP_webpageHandler)
    broadcastListener = lu.nodeDiscovery("alpha")
    lu.log(" Serving @ " + str(lu.getAddr()) + ":" + str(lu.getPort("alpha")))
    httpd.serve_forever()
except OSError:
    lu.error("Port in use - " + str(lu.getPort("alpha")))
except KeyboardInterrupt:
    sys.exit(0)
