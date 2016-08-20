import sys
import socket
import ipaddress
import threading, subprocess
import queue
import time
import inspect
import re

# ==========================
#   Static Ports
# ==========================
ports = {}
ports["alpha"]             = 26000 # HTTP
ports["omega"]             = 26001 # HTTP
ports["delta"]             = 9200  # TCP - Elastic
ports["lambda-M"]          = 26003 # TCP
ports["lambda-m"]          = 26004 # TCP

# used for host discovery
ports["OmegaListen"]    = 26101 # UDP
ports["OmegaBroadcast"]    = 26102 # UDP # sends omega server to subnet
# ports["BroadcastWriter"]    = 26102 # UDP

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
## END subproc
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
def getAddr():
    # returns LAN address
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  return s.getsockname()[0]

# ==========================
#  Node Discovery
# ==========================
def getOmegaAddr(addr):
    omegaBroadcastReceived = False
    log("Getting Omega Address.")
    while not omegaBroadcastReceived:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(.05)
            sock.bind((addr, ports["OmegaBroadcast"])) # UDP
            data, addr = sock.recvfrom(1024)
            if(len(data) > 0):
                omegaBroadcastReceived = True
        except:
            pass
            #log("Could not get Omega Server Address. Retrying")
    sock.close()
    # print(data)
    addr=data.decode("UTF-8").split(" ")
    log("Got Omega Address : " + addr[0])
    omegaAddr = addr[0]
    return omegaAddr
class nodeDiscovery():
    # Interprocess communication
    # served over UDP
    broadcastAddr=ipaddress.ip_network('192.168.1.0/24')
    sleepTime=0.1
    alive=True
    queueSize=20
    UDPtimout=500
    omegaAddr=None
    def __init__(self,name):
        # initializes a multicast UDP socket and broadcasts the nodes ip address to the subnet.
        #   It also listens for incoming messages
        self.name=name
        self.addr=getAddr()
        self.omegaAddr=getOmegaAddr(self.addr)
        informOmega = threading.Thread(target=self._informOmega, args = ())
        informOmega.start()
    def _informOmega(self):
          # continually sends out ping messages with the clients ip addr and name. UDP
        msg=str(self.addr)+" "+str(self.name)
        while self.alive:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(msg.encode("UTF-8"), (self.omegaAddr, ports["OmegaListen"]))
            time.sleep(self.sleepTime)
    def sendMsg(self):
          # temporary may not be implemented.
        if self.alive:
          for addr in self.broadcastAddr:
            self.sock.sendto(msg.encode("UTF-8"), (str(addr), self.broadcastPort))
          return 0
        return -1
    def kill(self):
      # destroys the nodeDiscovery threads
      self.alive=False
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
# ==========================
#   Main file execution
# ==========================
if __name__ == '__main__':
    print("This file is meant for importation")
