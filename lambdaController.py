#!/usr/bin/env python3

# this script is not necessary to run the Lambda Machine. You may set the componenets up manually.
# this relys on a terminal emulator like xterm

# this is an interface to the modules that compose the Lambda Machine


import subprocess, threading, queue
import sys, os
import re, io
import time

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
  try:
    while someAlive > 0:
      someAlive=0
      for comp in liveComp:
        out = comp.getOutput()
        if out[0]:
          sys.stdout.write(out[0]+"\n")
          sys.stdout.flush()
        if out[1]:
          sys.stderr.write(out[1]+"\n")
          sys.stderr.flush()
      for comp in liveComp:
        if comp.isAlive() != None:
          someAlive=someAlive+comp.isAlive()
        else:
          someAlive=1
  except KeyboardInterrupt:
    for comp in liveComp:
      lu.log("Killing Process - " + str(comp.subProc.pid))
      comp.kill()
def component(comp):
    if(dockerMode):
      lu.log("Docker Mode is not currently implemented.")
    else:
      compPath=os.path.join(DIR, comp)
      if comp == "alpha":
        return lu.subProc("./alpha/Alpha-Server.py")
      elif comp == "lambda-M":
        return lu.subProc("./lambda-M/LambdaMaster-Server.py")
      elif comp == "lambda-m":
        return lu.subProc("./lambda-m/LambdaMinion-Server.py")
      elif comp == "omega":
        return lu.subProc("./omega/Omega-Server.py")
      elif comp == "delta":
        return lu.subProc("./delta/Delta-Database.py")
      else:
        lu.error(comp + " not a recognized component")
main()