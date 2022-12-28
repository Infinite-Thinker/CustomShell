import subprocess
import os, sys
# import grp
# import pwd
import shutil
import signal
from datetime import datetime

class specific_colors:
    FAIL = '\033[91m'
    STOP = '\033[0m'

# Simple shell
# COMMANDS        
# 1. info XX    - Checks file/dir exists
# 2. files      - Shows files in directory
# 3. delete XX  - Checks directory/ file exists and delete it
# 4. copy XX YY - Copies XX in YY
# 5. where      - Shows current directory
# 6. down DD    - Checks directory exists and enters
# 7. up         - Check you're not in the root and goes up in the directory tree
# 8. finish     - terminate program
# 9. program name to run external program
# Type any linux command - It will work! :)

#column headers
HeaderFilesCmd = ["File Name", "Type"]
global DirPath
HeaderInfoCmd = ["File Name", "Type", "Owner User", "Owner Group", "Last modified time", "Size", "Executable"]
width = [25, 11, 20, 20, 26, 11, 11]

path = os.environ['PATH']
THE_PATH = path.split(':')

# Run commands
# Run an executable somewhere on the path
# Any number of arguments
def RunCmd(fields):
    global PID, THE_PATH

    cmd = fields[0]
    cnt = 0
    args = []
    while cnt < len(fields):
        args.append(fields[cnt])
        cnt += 1

    execName = AddPath(cmd, THE_PATH)

    # run executable
    if not execName:
        print('Executable file ' + str(cmd) + ' not found')
    else:
    #execute cmd
        print(execName)

# execv executes a new program, replacing the current process; on success, it does not return.
# On Unix, the new executable is loaded into  the current process, and will have the same process id as the caller.

    try:
        pid = os.fork()
        if pid == 0:
            os.execv(execName, args)
            os._exit(0)
        else:
            #wait for child process to exit

            _, status = os.waitpid(0, 0)
            exitCode = os.WEXITSTATUS(status)
            if exitCode == 0:
                print('Process terminated with exit code %d' %(exitCode))


    except:
        print('Something went wrong')
        os._exit(0)


#construct path to run the external command
#check to see if file is executable

def AddPath(cmd, path):
    if cmd[0] not in ['/', '.']:
        for d in path:
            execName = d + "/" + cmd
            if os.path.isfile(execName) and os.access(execName, os.X_OK):
                return execName
        return False
    else:
        return cmd

#list file and directory names:
def filesCmd(fields, filename):
    global info
    info = []
    if checkArgs(fields, 0):
        info.append(filename)
        info.append(getFileType(filename))

#list file info
def infoCmd(fields):
    global info
    info = []
    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            printHeader("info")
            info.append(argument)
            info.append(getFileType(argument))
            statInfo = os.stat(argument)
            uid = statInfo.st_uid
            gid = statInfo.st_gid
            # user = pwd.getpwuid(uid)[0]
            # group = grp.getgrgid(gid)[0]
            # info.append(user)
            # info.append(group)
            info.append(datetime.fromtimestamp(os.stat(argument).st_mtime).strftime('%b %d %Y %H:%M:%S'))
            info.append(os.path.getsize(argument))
            if os.access(argument, os.X_OK):
                info.append("No")
            else:
                info.append("Yes")
        else:
            print("File/ Dir doesnt exist")


# delete files
def deleteCmd(fields):
    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            try:
                os.remove(argument)
                print("File deleted")
            except OSError:
                print("File cannot be deleted")
    else:
        print("File doesnt exist")

#copy command -> from to
def copyCmd(fields):
    if checkArgs(fields, 2):
        argument1 = fields[1]
        argument2 = fields[2]
        if os.access(argument1, os.F_OK) and not os.access(argument2, os.F_OK):
            shutil.copyfile(argument1, argument2)
        else:
            print("Cannot copy because either the source file doesnt exist or destination file exits unexpectedly")

#where command
def whereCmd(fields):
    if checkArgs(fields, 0):
        DirPath = os.getcwd()
        print(DirPath)

#changing directory
def downCmd(fields):
    if checkArgs(fields, 1):
        argument = fields[1]
        if os.access(argument, os.F_OK):
            os.chdir(argument)
        else:
            print("The directory doesnt exist")
        
#change dir to up (parent)
def upCmd(field):
    if checkArgs(fields, 0):
        if os.path.realpath(DirPath) == os.path.realpath("/"):
            print("Already in root, can't go up")
        else:
            os.chdir("../")
        
#finish task and exit shell
def finishCmd(fields):
    if checkArgs(fields, 0):
        exit()


#other than commands -> to exe cmds check

#check for the arguments
def checkArgs(fields, num):
    numArgs = len(fields) - 1
    if numArgs == num:
        return True
    if numArgs > num:
        print("unexpected argument " + fields[num + 1] + " for command " + fields[0])
    else:
        print("Missing argument for command "+ fields[0])

#print file informations
def printFileInfo():
    fieldNum = 0
    output = ''
    while fieldNum < len(info):
        output += '{field:{fill}<{width}}'.format(field = info[fieldNum], fill = ' ', width = width[fieldNum])
        fieldNum += 1
    print(output)

# print header
def printHeader(typeHeader):
    fieldNum = 0
    output = ''
    if typeHeader == "files":
        while fieldNum < 2:
            output += '{field:{fill}<{width}}'.format(field = HeaderInfoCmd[fieldNum], fill = ' ', width = width[fieldNum])
            fieldNum += 1
        print(output)
        print('-' * 36)
    elif typeHeader == "info":
        while fieldNum < len(HeaderInfoCmd):
            output += '{field:{fill}<{width}}'.format(field = HeaderInfoCmd[fieldNum], fill = ' ', width = width[fieldNum])
            fieldNum += 1
        print(output)
        length = sum(width)
        print('-' * length)


# type of file cmd check
def getFileType(filename):
    if os.path.isdir(filename):
        return "Dir"
    elif os.path.isfile(filename):
        return "File"
    elif os.path.islink(filename):
        return "Link"


# infinite looping for inputs (main)

while True:
    DirPath = os.getcwd()
    base = os.path.basename(DirPath)
    line = input(specific_colors.FAIL + base + " > InfiniteN00b_Shell>" + specific_colors.STOP)
    fields = line.split()
    # split commands into fields stored in the fields list
    # fields[0] is the command name followed by the arguments in the command

    if fields[0] == "files":
        printHeader("files")
        for filename in os.listdir('.'):
            filesCmd(fields, filename)
            printFileInfo()
    elif fields[0] == "info":
        infoCmd(fields)
        printFileInfo()
    elif fields[0] == "delete":
        deleteCmd(fields)
    elif fields[0] == "copy":
        copyCmd(fields)
    elif fields[0] == "where":
        whereCmd(fields)
    elif fields[0] == "up":
        upCmd(fields)
    elif fields[0] == "down":
        downCmd(fields)
    elif fields[0] == "finish":
        finishCmd(fields)
    else:
        RunCmd(fields)


