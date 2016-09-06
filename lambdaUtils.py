import sys
import socket
import ipaddress
import threading, subprocess
import queue
import time
import inspect
import re

# ==========================
#   Global Variables
# ==========================
#subNet="192.168.1.0/24"
subNet="127.0.0.1/32"


# ==========================
#   Static Ports
# ==========================a
# MAJOR BUG : need a dynamic distribution of these addresses. 
# if a non lambda-mchine process is using one of these address
# the lambda-machine process will never connect.
ports = {}
ports["alpha"]             = 26000 # HTTP   # HTTP Website frontend
ports["omega"]             = 26001 # HTTP   # Network Table and Minion ID requests
ports["delta"]             = 9200  # TCP    # Elastic Database Access Point
ports["lambda-M"]          = 26003 # HTTP   # push scripts for distribution
# ports["lambda-m"]        = 26004 # TCP    # Lambda minions generate their own TCP socket address

# used for host discovery
ports["OmegaListen"]       = 26101 # UDP    # Receives table entries
ports["OmegaBroadcast"]    = 26102 # UDP    # sends omega server address to subnet

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
paths["alpha_scripts"]          = "codeScrolls"        # GET
paths["omega_TableJSON"]        = "/nodesJSON"          # GET

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
def log(string):
    sys.stdout.write("<log> " + getCallerFile() + " : " + str(string).strip() + "\n")
    sys.stdout.flush()
def error(string, *e):
    sys.stderr.write("<ERROR> " + getCallerFile() + " : " + str(string) + "\n")
    if len(e) > 0:
      sys.stderr.write("============================\n")
      sys.stderr.write(str(e))
    sys.stderr.flush()
    sys.exit(1)
addr = None
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
      error("Could not get address.")
  return addr
def getBroadcast():
    return str(ipaddress.ip_network(subNet).broadcast_address)
	#return ipaddress.ip_network(subNet)
# ==========================
#   Sub Process
# ==========================
class subProc():
  errQueue=queue.Queue() # stderr
  outQueue=queue.Queue() # stdout
  subProc=None
  def getOutput(self):
    # returns touple(stdout, stderr)
    # if there is not output stdout=None or stderr=None
    time.sleep(.1)
    out=None
    err=None
    if(not self.queuesEmpty()):
      try:    out=self.outQueue.get(False).strip()
      except: out=None
      try:    err=self.errQueue.get(False).strip()
      except: err=None
    return (out, err)
  def kill(self):
    self.subProc.kill()
  def queuesEmpty(self):
    # returns true if there is no data left in stdout or stderr
    if(self.errQueue.empty() and self.outQueue.empty()):
      return True
    else:
      return False
  def isAlive(self):
    # returns the state of the process:
    #   None  : process has not started yet
    #   1     : Process is currently executing
    #   0     : Process has terminated
    if (self.subProc):
      if (self.subProc.poll() == None):
        return 1 # alive and running
      else:
        return 0 # terminated
    else:
      return None # has not been born
  def waitForSubProc(self):
    # waits for the subprocess to start
    while (self.isAlive() == None):
      time.sleep(.1)
  def __init__(self, command):
    # initialized 3 threads. Subprocess with command, stdout reader, and stderr reader. All asynchronous.
    threading.Thread(target=self._subProcess, args=(command,), daemon=True).start()
    self.waitForSubProc()
    threading.Thread(target=self._ioQueue, args=(self.subProc.stdout, self.outQueue), daemon=True).start()
    threading.Thread(target=self._ioQueue, args=(self.subProc.stderr, self.errQueue), daemon=True).start()
  def _ioQueue(self, pipe, queue):
    # setup a pipe to output to a queue
    self.waitForSubProc()
    out=None
    while(1):
      for line in pipe:
        queue.put(str(line.decode("UTF-8")),block=True, timeout=None)
      if(self.isAlive() == 0):
        break
      time.sleep(.1)
  def _subProcess(self, command):
    # execute sub process from a thread.
    self.subProc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# ==========================
#  Node Discovery
# ==========================
omegaAddr=None
def getOmegaAddr(*addr):
    global omegaAddr
    if omegaAddr:
        return omegaAddr
    if len(addr) > 0:
        addr = getAddr()
    else:
        addr = addr[0] 
    
    omegaBroadcastReceived = False
    log("Getting Omega Address.")
    while not omegaBroadcastReceived:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(.1)
            #log("Receiving Omega address on " + str((getBroadcast(), ports["OmegaBroadcast"])))
            sock.bind((getBroadcast(), ports["OmegaBroadcast"])) # UDP
            data, a = sock.recvfrom(1024)
            if(len(data) > 0):
                omegaBroadcastReceived = True
        except socket.timeout :
            sock.close()
            time.sleep(.1)
            #log("Could not get Omega Server Address. Retrying")
        except OSError :
            sock.close()
            time.sleep(.1)
            log("Socket in use. THIS MAY BE A BUG. Retrying")
    sock.close()
    omegaAddr=data.decode("UTF-8").split(" ")[0]
    log("Got Omega Address : " + omegaAddr)
    return omegaAddr
class nodeDiscovery():
    # Interprocess communication
    # served over UDP
    sleepTime=5
    alive=True
    queueSize=20
    UDPtimout=500
    omegaAddr=None
    port=None
    addr=getAddr()
    broadcastAddr=getBroadcast()
    def __init__(self, name, *port):
        # initializes a multicast UDP socket and broadcasts the nodes ip address to the subnet.
        #   It also listens for incoming messages
        self.name=name
        self.omegaAddr=getOmegaAddr(self.addr)
        try:    self.port=port[0]
        except: pass
        informOmega = threading.Thread(target=self._informOmega, args = ())
        informOmega.start()
    def _informOmega(self):
          # continually sends out ping messages with the clients ip addr and name. UDP
        msg=str(self.addr)+" "+str(self.name)
        if(self.port):
            msg+=" " + self.port
        while self.alive:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(msg.encode("UTF-8"), (self.omegaAddr, ports["OmegaListen"]))
            time.sleep(self.sleepTime)
    def kill(self):
      # destroys the nodeDiscovery threads
      self.alive=False
# ==========================
#   Main file execution
# ==========================
if __name__ == '__main__':
    print("This file is meant for importation")
