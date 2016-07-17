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
  broadcastAddr=ipaddress.ip_network('192.168.1.0/24')
  sleepTime=5
  alive=True
  def __init__(self,name):
    # initializes a multicast UDP socket and broadkasts the nodes ip address to the subnet.
    #   It also listens for incoming messages
    self.readBuffer=queue.Queue(maxsize=5)
    self.name=name
    self.addr=self.getAddr()
    broadcastMsg=str(self.addr)+" "+self.name
    broadcastThread = threading.Thread(target=self._broadcast, args = (broadcastMsg,))
    broadcastThread.start()

  def listen(self):
      # only one listener per computer. This will be used by the omega server to create a network table.
      listenThread = threading.Thread(target=self._listen, args = ())
      listenThread.start()
  def getAddr(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

  def _broadcast(self, msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while self.alive:
        for addr in self.broadcastAddr:
            sock.sendto(msg.encode("UTF-8"), (str(addr), self.broadcastPort))
    sleep(self.sleepTime)

  def _listen(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((self.addr, self.broadcastPort))
    while self.alive:
      data, addr = sock.recvfrom(1024)
      if not self.readBuffer.full():
        self.readBuffer.put(data.decode("UTF-8"))
      else:
        self.readBuffer.get()
        print("Queue overflow. Dropping datagram.")
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
  nodes=[]
  nodes.append(nodeDiscovery("cat"))
  nodes.append(nodeDiscovery("dog"))
  nodes.append(nodeDiscovery("hog"))
  # person = nodeDiscovery("person")
  # person.listen()
  # nodes.append(person)
  #
  # while 1 :
  #       msg = person.getMsg()
  #       if msg != None:
  #           print(msg)
            # sleep(1)
# test()
