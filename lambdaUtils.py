import sys
import socket
import ipaddress
import threading, subprocess # TODO: remove threading
import queue
import urllib.request
import http.client
import time
import inspect
import re
import json
import ast
import hashlib
import socketserver

# ==========================
#   Global Variables
# ==========================
subNet="127.0.0.1/32"
# subNet="192.168.1.0/24"

# ==========================
#   Global Ports
# ==========================a

_ports = {}
_ports["alpha"]              = 26000 # HTTP   # HTTP Website frontend
_ports["omega_tableReq"]     = None # HTTP   # Network Table and Minion ID requests
_ports["delta"]              = 9200 # TCP    # Elastic Database Access Point
_ports["Master_programRec"]  = None # TCP   # push program for distribution
_ports["Master_JSONpost"]    = None # TCP   # push program for distribution
# _ports["minion_scriptRec"]   = None # TCP   #

# used for host discovery
_ports["OmegaListen"]       = 26101 # UDP    # Receives table entries
_ports["OmegaBroadcast"]    = 26102 # UDP    # sends omega server address to subnet

_ports=dict((k.lower(), v) for k,v in _ports.items())
# ==========================
#   Global Paths
# ==========================
paths = {}
paths["omega_Table"]            = "/table"              # GET
paths["omega_MinionTable"]      = "/lambdaMinionNumber" # GET # change this to miion mumber
paths["master_ClusterStat"]     = "/clusterStatus"      # GET & POST
paths["master_postScript"]      = "/postScript"         # POST
paths["alpha_nodeListing"]      = "/nodes"              # GET
paths["alpha_postScript"]       = "/submitToMaster"     # GET
paths["alpha_scripts"]          = "codeScrolls"         # GET
paths["alpha_stdout"]           = "stdout"              # GET
paths["alpha_stderr"]           = "stderr"              # GET
paths["master_progTable"]       = "/progTable"          # GET

# ==========================
#   Helper Functions
# ==========================
def getCallerFile():
    # uses stack tracing to return the file name of the calling process
    try:
        for i in inspect.stack():
            for j in i:
                if(type(j) == str):
                    if re.match(".*.py$", j.strip()) and not re.match(".*lambdaUtils.py$", j.strip()) :
                        j=re.sub(".*/", "", j)
                        j=re.sub(".py", "", j)
                        return j
    except:
        return "---"
def log(string, *more):
	string = "<LOG> " + getCallerFile() + " : " + str(string).strip()
	for i in more:
		string += " " + str(i)
	string += "\n"
	sys.stdout.write(string)
	sys.stdout.flush()
def logError(string):
    sys.stdout.write("<ERR> " + getCallerFile() + " : " + str(string).strip() + "\n")
    sys.stdout.flush()
def error(string, *e):
    sys.stderr.write("<FATAL ERROR> " + getCallerFile() + " : " + str(string) + "\n")
    if len(e) > 0:
        sys.stderr.write("============================\n")
        sys.stderr.write(str(e))
    sys.stderr.flush()
    sys.exit(1)
addr = None
# =====================================
#   TCP Server as background thread
# =====================================
class TCP_BackgroundProcess:
    listenPort=None
    def __init__(self, addr, handler):
        self.addr=addr
        self.handler=handler
    def listen(self ):
        self._startScriptReceival = threading.Thread(target=self._listen).start()
        while ( not self.listenPort ):
            time.sleep(.5)
        return self
    def _listen(self):
        # socketserver.TCPServer.allow_reuse_address = True
        self.listeningSocket=socketserver.TCPServer((self.addr, 0), self.handler)
        self.listenPort=str(self.listeningSocket.server_address[1])
        log("TCP_BackgroundProcess listener is running at TCP socket : " + self.addr+":"+self.listenPort)
        self.listeningSocket.serve_forever()
    def getListenPort(self):
        return self.listenPort
# ==========================
#   Program Distribution
# ==========================
## Binary
def sendMsg( msg, dest): # sends message as data
    msg=str(msg)
    print("sending : " + msg + "\nto : " + str(dest))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(dest)
    sock.sendto(msg, dest)
    sock.close()
def sendFile( fileLoc, dest): # sends file as data
    f = open(fileLoc, "rb")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(dest)
    try:
        sock.sendto(f.read(), dest)
    finally:
        f.close()
        sock.close()
## HTTP
def postHTTP( msg, addr, port, path): # sends message as data
    conn = http.client.HTTPConnection(addr, port)
    headers = {'Content-type': 'application/json', 'content-length' : len(msg)}
    conn.request("POST", path, msg.encode("UTF-8"), headers)
    response = conn.getresponse()
    print(response.read().decode())
def getHTTP(addr, port, path):
    requestURL='http://'+str(addr)+':'+str(port)+str(path)
    log("Requesting " + requestURL)
    with urllib.request.urlopen(requestURL) as response:
        httpData = response.read().decode("UTF-8")
    log("Got HTTP Request.")
    return httpData
def makeHTTPAddr(addr, port):
    return str('http://'+str(addr)+':'+str(port))
def getHash(fileLoc):
    m = hashlib.md5()
    with open(fileLoc, 'rb') as f:
        m.update(f.read())
    return m.hexdigest()

# ==========================
#  Database Communication
# ==========================
def deltaGetData(location):
    # location = list()
    print("/".join(location))
    if not getAddrOf("delta"):
        logError("Could not get Delta Address")
    if not getPort("delta"):
        logError("Could not get Delta Port")
    else:
        requestURL='http://'+str(getAddrOf("delta"))+':'+str(getPort("delta"))+"/" + "/".join(location)
        log("Requesting " + requestURL)
        msg=None
        try:
            with urllib.request.urlopen(requestURL) as response:
                msg = response.read().decode("UTF-8")
                return msg
        except:
            log("Could get date from delta")
            return None
def deltaPostData(message, location):
    if not getAddrOf("delta"):
        logError("Could not get Delta Address")
    if not getPort("delta"):
        logError("Could not get Delta Port")
    else:
        requestURL='http://'+str(getAddrOf("delta"))+':'+str(getPort("delta"))+"/" + "/".join(location)
        log("Requesting " + requestURL)
        try:
            urllib.request.urlopen(url=requestURL, data=json.dumps(message).encode("UTF-8")).info()
        except:
            logError("Could not post date to delta.")
            return None
# ==========================
#  Node Discovery
# ==========================
omegaAddr=None
def getPort(portName):
    portName=portName.lower()
    global _ports
    table=None
    port=None
    if(_ports[portName]):
        return _ports[portName]
    log("Getting Port over network : " + portName)
    table=getNetworkTable()
    for i in table:
        try:
            _ports[portName] = i[portName]
            return _ports[portName]
        except:
            pass
    logError("Could not get port : " + portName)
    return None
def getNetworkTable():
    msg=None
    requestURL='http://'+str(getOmegaAddr())+':'+str(getPort("omega_tableReq"))+paths["omega_Table"]
    with urllib.request.urlopen(requestURL) as response:
        msg = response.read().decode("UTF-8")
    try:
        msg = json.loads(msg)
    except:
        logError("Could not parse routing table")
        return None
    return msg
def getAddr():
    global addr
    global subNet
    if addr:
        pass
    # returns LAN address
    elif(subNet == "127.0.0.1/32"):
        addr="127.0.0.1"
    # get dynamic addr by connecting to internet
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            log("Connect to internet. Using address : " + s.getsockname()[0])
            return s.getsockname()[0]
        except OSError:
            log("Could not connect to internet. Using localhost 127.0.0.1")
            subNet="127.0.0.1/32"
            addr="127.0.0.1"
        except:
            logError("Could not get address.")
    return addr
def getBroadcast():
    return str(ipaddress.ip_network(subNet).broadcast_address)
def getAddrOf(entityStr):
    node = getNodeByName(entityStr)
    if(node):
        return node["addr"]
    return None
def getNodeByName(entityStr):
    # get the address of the entity specified
    # returns JASON Dump
    msg=None
    requestURL='http://'+str(getOmegaAddr())+':'+str(getPort("omega_tableReq"))+paths["omega_Table"]
    with urllib.request.urlopen(requestURL) as response:
        msg = response.read().decode("UTF-8")
    try:
        msg = json.loads(msg)
    except:
        logError("Could not parse routing table")
        return 1
    foundAddr=None
    for entity in msg:
        if(entity["name"] == entityStr):
            foundAddr=entity
    return foundAddr
def getOmegaAddr():
    global omegaAddr
    if omegaAddr:
        return omegaAddr
    addr = getAddr()
    omegaBroadcastReceived = False
    while not omegaBroadcastReceived:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(10)
            bindLoc = (getBroadcast(), getPort("OmegaBroadcast"))
            sock.bind(bindLoc) # UDP
            log("Getting Omega Address from ", bindLoc)
            data, a = sock.recvfrom(1024)
            if(len(data) > 0):
                omegaBroadcastReceived = True
        except socket.timeout :
            sock.close()
            time.sleep(.1)
            logError("Could not get Omega Server Address. Retrying")
    sock.close()
    omegaAddr=data.decode("UTF-8").split(" ")[0]
    _ports["omega_tablereq"]=data.decode("UTF-8").split(" ")[1]
    log("Got Omega Address : " + omegaAddr)
    return omegaAddr
class nodeDiscovery():
    # Interprocess communication
    # served over UDP
    sleepTime=5
    alive=True
    queueSize=20
    UDPtimout=500
    jsonInfo=None
    broadcastAddr=getBroadcast()
    def __init__(self, name, *ports):
        # initializes a multicast UDP socket and broadcasts the nodes ip address to the subnet.
        #   It also listens for incoming messages
        # ports is a touple : (str(portName), int(portNum))
        self.jsonInfo={}
        if ports:
            ports=ports[0]
            for i in ports:
                self.jsonInfo[i[0].lower()]=i[1]
        self.jsonInfo["name"]=name
        self.jsonInfo["addr"]=getAddr()
        informOmega = threading.Thread(target=self._informOmega, args = ())
        informOmega.start()
    def _informOmega(self):
        # continually sends out ping messages with the clients ip addr and name. UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.alive:
            jsonDump=json.dumps(self.jsonInfo)
            sock.sendto(jsonDump.encode("UTF-8"), (getOmegaAddr(), getPort("OmegaListen")))
            time.sleep(self.sleepTime)
    def kill(self):
            # destroys the nodeDiscovery threads
        self.alive=False
# ==========================
#   Main file execution
# ==========================
if __name__ == '__main__':
    print("This file is meant for importation")
