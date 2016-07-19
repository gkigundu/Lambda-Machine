import sys
import socket
import ipaddress
import threading
import queue
from time import sleep

ports = {}
ports["alpha"]    = 26000
ports["omega"]    = 26001
ports["delta"]    = 26002
ports["lambda-M"] = 26003
ports["lambda-m"] = 26004

def log(string):
    sys.stdout.write("<log>   " + str(string) + "\n")
    sys.stdout.flush()
def error(string, e):
    sys.stderr.write("<ERROR> " + str(string) + "\n")
    sys.stderr.write("============================\n")
    sys.stderr.write(str(e))
    sys.stderr.flush()
    sys.exit(1)
def getAddr():
    # returns LAN address
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  return s.getsockname()[0]

class nodeDiscovery():
    # Interprocess communication
    # served over UDP
  broadcastPort=35353
  broadcastAddr=ipaddress.ip_network('192.168.1.0/24')
  sleepTime=5
  alive=True
  def __init__(self,name):
    # initializes a multicast UDP socket and broadkasts the nodes ip address to the subnet.
    #   It also listens for incoming messages
    self.readBuffer=queue.Queue(maxsize=5)
    self.name=name
    self.addr=getAddr()
    broadcastMsg=str(self.addr)+" "+self.name
    broadcastThread = threading.Thread(target=self._broadcast, args = (broadcastMsg,))
    broadcastThread.start()

  def listen(self):
      # only one listener per computer. This will be used by the omega server to create a network table.
      #      otherwise : " OSError: [Errno 98] Address already in use "
      listenThread = threading.Thread(target=self._listen, args = ())
      listenThread.start()

  def _broadcast(self, msg):
      # continually sends out ping messages with the clients ip addr and name
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while self.alive:
        for addr in self.broadcastAddr:
            sock.sendto(msg.encode("UTF-8"), (str(addr), self.broadcastPort))
    sleep(self.sleepTime)

  def _listen(self):
      # listens to the broadcast messages and adds them to queue
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
      # returns the most recent broadcast message in the queue
    if not self.readBuffer.empty():
      return self.readBuffer.get()
    else:
      return None
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

def test():
    nodes=[]
    for i in range(0,30):
        nodes.append(nodeDiscovery("cat" + str(i)))
    sleep (3)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("tableReq".encode("UTF-8"), ("192.168.1.159", ports["omega"]))
    while 1:
      data, addr = sock.recvfrom(1024) # 1024
      print(data.decode("UTF-8"))

  # person = nodeDiscovery("person")
  # person.listen()
  # nodes.append(person)
  #
  # while 1 :
  #       msg = person.getMsg()
  #       if msg != None:
  #           print(msg)
            # sleep(1)
if __name__ == '__main__':
    test()
