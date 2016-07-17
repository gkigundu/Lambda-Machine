import sys
import socket
import ipaddress
import threading
import queue
from time import sleep


def log(string):
    sys.stdout.write("<log>   " + str(string) + "\n")
    sys.stdout.flush()
def error(string, e):
    sys.stderr.write("<ERROR> " + str(string) + "\n")
    sys.stderr.write("============================\n")
    sys.stderr.write(str(e))
    sys.stderr.flush()
    sys.exit(1)

# https://wiki.python.org/moin/UdpCommunication
# Interprocess communication
class nodeDiscovery():
  broadcastPort=35353
  broadcastAddr=ipaddress.ip_network('192.168.0.0/22')
  sleepTime=5
  readBuffer=None
  alive=True
  # sock=None
  # addr=None
  def __init__(self,name):
    # initializes a multicast UDP socket and broadkasts the nodes ip address to the subnet.
    #   It also listens for incoming messages
    self.readBuffer=queue.Queue(maxsize=100)
    self.name=name
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.addr=self.getAddr()
    self.sock.bind((self.addr, self.broadcastPort))
    listenThread = threading.Thread(target=self._listen, args = ())
    listenThread.start()
    broadcastMsg=str(self.addr)+" "+self.name
    broadcastThread = threading.Thread(target=self._broadcast, args = (broadcastMsg,))
    broadcastThread.start()
    
  def getAddr(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
  
  def _broadcast(self, msg):
    while self.alive:
      for addr in self.broadcastAddr:
        self.sock.sendto(msg.encode("UTF-8"), (str(addr), self.broadcastPort))
      sleep(self.sleepTime)
  
  def _listen(self):
    while self.alive:
      data, addr = self.sock.recvfrom(1024)
      if not self.readBuffer.full():
        self.readBuffer.put(data.decode("UTF-8"))
      else:
        self.readBuffer.get()
  def getMsg (self):
    if not self.readBuffer.empty():
      return self.readBuffer.get()
    else:
      return None
  def sendMsg(self):
    if self.alive:
      for addr in self.broadcastAddr:
        self.sock.sendto(msg.encode("UTF-8"), (str(addr), self.broadcastPort))
      return 0
    return -1
  def kill(self):
    self.alive=False
  
def test():
  n1 = nodeDiscovery("cat")
  n2 = nodeDiscovery("dog")
  n2.kill() # :(
  n3 = nodeDiscovery("hamster")
  while 1 :
    msg = n1.getMsg()
    if msg != None:
      print(msg)
test()