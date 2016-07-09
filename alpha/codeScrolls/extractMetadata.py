#!/usr/bin/python3
# Author        : Derek Maier
# Date Created  : 24 April 2016
# Last Revision : 25 April 2016
# Python 3.5.1+
# Version 0.2

# ===============
#   Dependency Versions
# ===============
# ls (GNU coreutils) 8.25
# du (GNU coreutils) 8.25
# md5sum (GNU coreutils) 8.25
# find (GNU findutils) 4.7.0-git
# file-5.25
# extract v1.3
# Metadata extractor version 1.3.3

########## THIS PROGRAM NEEDS TO BE SUBJECTED TO THOROUGH BUG TESTS

# This program uses several methods to collect meta data on the files in a directory.
# It takes one parameter, <path>. The path can be a directory or a file.
# The program prints out JSON encoded objects. This would be particularly useful
#     in documenting your file directory in ElasticSearch.

# Preliminaries:
#   Your user name may not contain spaces


# ===============
#   Imports
# ===============
import subprocess
import sys
import os
import json
import re
import datetime
import calendar
import time
from multiprocessing import Process, Queue, Value

# ===============
#   Global Default Values
# ===============
NUM_PROCESSES = 4
PARALLEL_FLAG = True
DEF_DIRECTORY = "."
LOG_TIME = 100 #DEF: 1
PRETTY_PRINT = False

# ===============
#   Preliminary Values
# ===============
dependencies = ["ls","du","md5sum","find","file","extract","hachoir-metadata"]
fileListLength = 0
fileListCount = Value('i', 0)

# ===============
#   Functions
# ===============
def checkDependencies(prog):
    # PreCondition   : Expects str(ProgramName)
    # PostCondition  : Returns int(Installed)
    assert(type(prog) is str)
    ret = runCommand(["which", prog])
    if(ret[0] != 0 or not ret[1]):
        return 1
    else:
        return 0
def runCommand(command):
    # PreCondition   : Expects list(CommandList)
    # PostCondition  : Returns list(int(0), str(Output))
    # ErrorCondition : Returns list(int(ErrorNum), str(ErrorStr))
    assert(type(command) is list)
    for i in range(len(command)): # remove white spaces on input array
        command[i] = command[i].strip()
        command[i] = command[i].rstrip('\n')
    try:
        proc = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # Execute command
    except FileNotFoundError:
        return (1, "File Not Found")
    except IndexError:
        return (2, "Index Error")
    output = proc.communicate() # Get output (Blocking)
    error = output[1].decode("utf-8").strip()
    output = output[0].decode("utf-8").split("\n") # remove empty lines
    output = list(filter(None, output))
    for i in range(len(output)):
        output[i] = output[i].strip()
    if(error != ''):
        return (1,error)
    else:
        return (0,output)
def getFileInfo(filePath):
    # PreCondition   : Expects str(FilePath)
    # PostCondition  : Returns json.dumps(FileMetaData)
    print(filePath)
    assert(type(filePath) is str)
    JSONobject = {}

    # ===============
    #   md5sum
    # ===============
    hashCode = runCommand(["md5sum", filePath])
    if(hashCode[0] == 0):
        hashCode = str(hashCode[1][0].split(" ")[0]).strip()
    else:
        printError(hashCode[0],hashCode[1])

    # ===============
    #   hachoir-metadata
    # ===============
    hachoirDict = {}
    curSel = None
    hachoir = runCommand(["hachoir-metadata", filePath])
    if(hachoir[0] == 0):
        for i in hachoir[1]:
            if(i):
                if re.compile(r'^File').search(i) is not None:
                    curSel = re.sub(r'^File "',"",i)
                    curSel = re.sub(r'"\:$',"",curSel)
                    hachoirDict[curSel]={}
                elif re.compile(r'\:$').search(i) is not None:
                    curSel = re.sub(r'\:$',"",i).strip()
                    hachoirDict[curSel]={}
                else:
                    i = re.sub(r'-\s+',"",i)
                    i = i.split(":", 1)
                    hachoirDict[curSel][str(i[0].strip())] = i[1].strip()
                    # hachoirDict[curSel].append({i[0].strip():i[1].strip()})
    else:
        hachoir = {} # do nothing, hachoir crashes if it can't read file
    JSONobject["hachoir-metadata"] = hachoirDict

    # ===============
    #   extract
    # ===============
    extractList = {}
    extract = runCommand(["extract", filePath])
    if(extract[0] == 0):
        extract = extract[1][1:]
        extract = list(filter(None, extract))
        for i in extract:
            i = i.split("-",1)
            extractList[i[0].strip()] = i[1].strip()
    else:
        printError(extract[0],extract[1])
    JSONobject["extract"] = extractList

    # ===============
    #   File
    # ===============
    file = runCommand(["file", filePath])
    if(file[0] == 0):
        file = file[1][0].split(":", 1)[1].strip().split(",")
        for i in range(len(file)):
            file[i] = file[i].strip()
    else:
        printError(file[0],file[1])
    JSONobject["file"] = file

    # ===============
    #   ls
    # ===============
    infoLSobject = {}
    infoLS = runCommand(["ls", "-l", "--time-style", "long-iso", filePath])
    if(infoLS[0] == 0):
        infoLS = list(filter(None, infoLS[1]))[0].split()
        infoLSobject["Permissions"] = infoLS[0].strip()
        infoLSobject["HardLinks"] = infoLS[1].strip()
        infoLSobject["Owner"] = infoLS[2].strip()
        infoLSobject["Group"] = infoLS[3].strip()
        infoLSobject["Size"] = infoLS[4].strip()
        infoLSobject["DateModified"] = " ".join(infoLS[5:7]).strip()
        infoLSobject["File"] = " ".join(infoLS[7:]).strip()

    else:
        printError(infoLS[0],infoLS[1])
    JSONobject["ls"] = infoLSobject

    # ===============
    #   du FileSize
    # ===============
    infoDU = runCommand(["du", filePath])
    if(infoDU[0] == 0):
        infoDU = infoDU[1][0].strip()
        infoDU = re.sub(r'\t.*',"",infoDU)
    else:
        printError(infoDU[0],infoDU[1])
    JSONobject["du"] = infoDU.strip()

    # ===============
    #   File Extension
    # ===============
    ext = re.sub(r'.*\/',"",filePath)
    if(r'.' in ext):
        JSONobject["extension"] = re.sub(r'.*\.',"",filePath).strip()
    else:
        JSONobject["extension"] = ""

    # return setup
    JSONobjectOver = {}
    JSONobjectOver["data"] = JSONobject
    JSONobjectOver["md5sum"] = hashCode
    JSONobjectOver["filePath"] = filePath.strip()
    return json.dumps(JSONobjectOver)
def getFileList(filePath):
    # PreCondition   : Expects str(FileOrDirectory)
    # PostCondition  : Returns A List(SubsiquentChildFiles)
    assert(type(filePath) is str)
    lineArray = runCommand(["find", filePath ,"   -type", "f", "-exec", "readlink", "-f", "{}", r";"])
    return(lineArray)
def printError(num, errorstr):
    # PreCondition   : Expects list(num(ErrorNumber),str(ErrorMessage))
    # PostCondition  : Exit(1)
    print("<Error> " + str(num) + " @ " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " : "+ str(errorstr),file=sys.stderr) # prints to stdError
    sys.exit(1)
def printLog(logStr):
    # PreCondition   : Expects list(num(ErrorNumber),str(ErrorMessage))
    # PostCondition  : Print log to StdError with not Error
    print("<Log> @ " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " : "+ str(logStr),file=sys.stderr) # prints to stdError
def parallelGetFileInfo(procFileList, queue, fileListCount):
    # PreCondition   : Expects list(list(ListOfFiles),Queue(DumpOutput))
    # PostCondition  : Puts File Info Into Queue
    #                  Exit(0)
    assert(type(procFileList) == list)
    for i in procFileList:
        queue.put(json.loads(getFileInfo(i)))
        fileListCount.value += 1
    sys.exit(0)
def printSoftwareVersion(software): ######### Need to implement
    assert(type(software) == list)
    # PreCondition   : Expects list(list(ListOfFiles),Queue(DumpOutput))
    # PostCondition  : Prints Installed Software Versions
    #                : Exit(0)
    for i in software:
        print(runCommand([i, "--version"])[1][0])
    sys.exit(0)
def printHelp(): ######### Need to implement
    # PostCondition  : Prints Installed Software Versions
    #                : Exit(0)
    helpMessage = []
    helpMessage.append(("Usage",sys.argv[0] + " <Options>"))
    helpMessage.append(("Default",sys.argv[0] + " -d ."))
    helpMessage.append(("-d","Directory to use tool on"))
    helpMessage.append(("-c","Number of process [def:4]"))
    helpMessage.append(("-h","Help message"))
    helpMessage.append(("-p","Turn on pretty print"))
    helpMessage.append(("--dep","List Dependencies"))
    helpMessage.append(("--nonPar","Run in single thread"))
    for i in helpMessage:
        print("{:10}: {}".format(i[0],i[1]))
    sys.exit(0)
def parseArguments():
    # PostCondition  : N/A
    #                : Sets Global Variables From Command Line
    global DEF_DIRECTORY
    global PARALLEL_FLAG
    global NUM_PROCESSES
    global PRETTY_PRINT
    argList = sys.argv[1:]
    while len(argList) > 0:
        nextVal = str(argList[0].strip())
        if(nextVal == "-h" or nextVal == "--help" or nextVal == "--h" or nextVal == "-help"):
            printHelp()
        elif(nextVal == "--dep"):
            printSoftwareVersion(dependencies)
        elif(nextVal == "-d"):
            try:
                DEF_DIRECTORY = str(argList[1].strip())
            except:
                printError(9,"Parameter Error " + nextVal + " Takes A Variable.")
            if(not os.path.exists(DEF_DIRECTORY)):
                printError(8,"Can Not Access Directory " + str(DEF_DIRECTORY))
            del argList[0]
        elif(nextVal == "--nonPar"):
            PARALLEL_FLAG = False
        elif(nextVal == "-p"):
            PRETTY_PRINT = True
        elif(nextVal == "-c"):
            try:
                NUM_PROCESSES = int(argList[1].strip())
            except:
                printError(9,"Parameter Error " + nextVal + " Takes A Positive Integer.")
            if(NUM_PROCESSES < 1):
                printError(9,"Parameter Error " + nextVal + " Must Specify Atleast One Process Worker.")
            if(NUM_PROCESSES > 20):
                printError(9,"Parameter Error " + nextVal + " Limit: 20.")
            del argList[0]
        else:
            printError(6, "Unknown Argument '"+ argList[0] + "'. Type " + sys.argv[0] + " -h for help.")
        del argList[0]
# ===============
#   Main Method
# ===============
def main():
    global fileListLength
    global fileListCount
    # Dependency test
    depNotMet = ""
    for i in dependencies:
        if(checkDependencies(i) != 0):
            depNotMet += i + ", "
    if(len(depNotMet) > 0):
        printError(3, "[" + re.sub(r',$',"",depNotMet.strip()) + "]"+ " Not Found. Please Install.")
    # Get Arguments
    parseArguments()
    # get directory Listing
    fileList = getFileList(DEF_DIRECTORY)
    if(fileList[0] == 0):
        fileList = list(filter(None, fileList[1]))
    else:
        printError(fileList[0],fileList[1])
    fileListLength = len(fileList)
    # execute on list
    listJSON = []
    if(PARALLEL_FLAG == 0):
        for i in fileList:
            listJSON.append(json.loads(getFileInfo(i)))
    elif(PARALLEL_FLAG == 1):
        workerList = ([],[])
        localFileList = []
        for i in range(NUM_PROCESSES):
            localFileList.append([])
        for i in range(len(fileList)):
            localFileList[i % NUM_PROCESSES].append(fileList[i])
        for i in range(NUM_PROCESSES):
            workerList[1].append(Queue())
            workerList[0].append(Process(target=parallelGetFileInfo, args=((localFileList[i],workerList[1][i],fileListCount))))
            workerList[0][i].start()
    # main loop waiting for processes
        curTime = calendar.timegm(time.gmtime())
        cont = True
        while(cont):
            if(calendar.timegm(time.gmtime()) - curTime > LOG_TIME):
                curTime = calendar.timegm(time.gmtime())
                printLog(str(int(float(fileListCount.value) / fileListLength * 100)) + r"% Done - " + str(fileListCount.value) + "/" + str(fileListLength) +  " Files")
            cont = False
            for proc in workerList[0]:
                if proc.is_alive():
                    cont = True
            for queues in workerList[1]: # Empty queue. This MUST be done in a timely fashion. Or program is susceptible to infinite loop bug (https://bugs.python.org/issue8237)
                cont2 = 0
                while(not queues.empty() and cont2 < 10):
                    listJSON.append(queues.get())
                    cont2 += 1
            proc.join(.2)

    # print Results
    if(PRETTY_PRINT == True):
        for i in listJSON:
            print(json.dumps(i, sort_keys=True, indent=2))
    else:
        for i in listJSON:
            print(json.dumps(i, sort_keys=True))

main()
