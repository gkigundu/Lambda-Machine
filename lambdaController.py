#!/usr/bin/env python3

# this script is not necessary to run the Lambda Machine. You may set the componenets up manually.
# this relys on a terminal emulator like xterm

import subprocess, threading
import sys, os
import re, io
import lambdaUtils as lu

# help
help= [
        ("-h", "help message"),
        ("-y", "Skip Verification messages"),
        ("-d", "Docker Mode Enabled")
      ]

DIR=os.path.dirname(os.path.realpath(__file__))
dockerMode=0
skipVerification=0
compList=[]
termEmulator=""

# parse args
args=sys.argv[1:]
i=0
while i < len(args):
  if args[i] == "-d" :
    dockerMode=1
  elif args[i] == "-y" :
    skipVerification=1
  elif args[i] == "-h" :
    print("  " + sys.argv[0] + " <comp1> <comp2> <comp..> <options>")
    print("  Options:")
    for i in help:
      print("\t{:5}{:20}".format(i[0],i[1]))
    exit(0)
  else:
    compList.append(args[i])
  i=i+1

# options log
lu.log("Docker Mode Enabled : " + str(bool(dockerMode)))
lu.log("Skip Verification messages : " + str(bool(skipVerification)))
lu.log("Specified component list : " + str(compList))

def main():
  global termEmulator
  components=["alpha","lambda-M","lambda-m","omega","delta"]
  setup=[]
  error=[]
  for arg in compList:
    arg=re.sub("[^a-zA-Z0-9]", "", arg) # remove any none num or alpha char
    if arg in components:
      setup.append(arg)
    else:
      error.append(arg)
  if len(setup) == 0 or len(error) > 0:
    lu.error("Please specify a list of valid components to start.\n\tValid componenets : " + str(components) +
      "\n\tYou specified : " + str(sys.argv[1:]) +
      "\n\tThe following are invalid : " + str(error))
  choice=""
  if skipVerification == 0 :
    choice = input("Do you want to setup " + str(setup) + " on this node? Y/n: ")
    choice=re.sub("[^a-zA-Z0-9]", "", choice) # remove any none num or alpha char
  liveComp=[]
  if(choice == "" or choice == "y" or choice == "Y"):
    for comp in setup:
      liveComp.append(component(comp))
  else:
    lu.error("You've Chosen not to continue.")
  someAlive=1
  while someAlive > 0:
    someAlive=0
    for comp in liveComp:
      out = comp.getOutput()
      if not out == None:
        sys.stdout.write(out[0])
        sys.stderr.write(out[1])
        sys.stdout.flush()
        sys.stderr.flush()
    for comp in liveComp:
      if comp.isAlive() != None:
        someAlive=someAlive+comp.isAlive()
      else:
        someAlive=1
class component():
  subProc=None
  def getOutput(self):
    if(self.subProc):
      return "cat" ######### <<<<<
    return None
  def isAlive(self):
    if (self.subProc != None):
      if (self.subProc.poll() == None):
        return 1
      else:
        return 0
    else:
      return None
  def __init__(self, comp):
    if(dockerMode):
      lu.log("Docker Mode is not currently implemented.")
      # if comp == "alpha":
      #   print(comp)
      # elif comp == "lambda-M":
      #   print(comp)
      # elif comp == "lambda-m":
      #   print(comp)
      # elif comp == "omega":
      #   print(comp)
      # elif comp == "delta":
      #   print(comp)
      # else:
      #   lu.error(comp + " not a recognized component")
    else:
      compPath=os.path.join(DIR, comp)
      if comp == "alpha":
        print(comp)
      elif comp == "lambda-M":
        print(comp)
      elif comp == "lambda-m":
        print(comp)
      elif comp == "omega":
        print(comp)
      elif comp == "delta":
        self.proc=self.subProcess("./test ") # + compPath
      else:
        lu.error(comp + " not a recognized component")
  def subProcess(self, command):
    threading.Thread(target=self._subProcess, args=(command,), daemon=True).start()
  def _subProcess(self, command):
    self.subProc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
main()