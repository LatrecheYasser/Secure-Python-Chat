import socket
import sys
import threading
import random
import string
from RSA import RSA
from RC4 import RC4
import time


HOST = '127.0.0.1'
PORT = 50007
Globalvariable = {"RSA_Recieved": False,
                  "RSA_Sent": False,
                  "OtherRsaN": 0,
                  "OtherRsaE": 0,
                  "n": 0,
                  "e": 0,
                  "d": 0,
                  "RC4Key": "",
                  "EncRC4Key": "",
                  "RC4_sent": False,
                  "OtherRC4": ""}

# 1) create a socket
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2) send a connection request to server
try:
    mySocket.connect((HOST, PORT))
except socket.error:
    print("Client can't connect")
    sys.exit()
print("Trying to connect.... ")


class ThreadReceive(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn	     
        
    def run(self):
        global Globalvariable
        
        while 1:
            message_recu = self.connexion.recv(1024).decode("Utf8")
            if message_recu[0:14] == "##Rsapubkeyis#":
                if not Globalvariable['RSA_Recieved']:
                    message = message_recu[14:].split("#")
                    Globalvariable['OtherRsaE'], Globalvariable['OtherRsaN'] = int(message[0]), int(message[1])
                    self.connexion.send("##YesRsa".encode("Utf8"))
                    Rsa = RSA()
                    Globalvariable["EncRC4Key"] = Rsa.crypt(Globalvariable["OtherRsaE"],Globalvariable["OtherRsaN"],Globalvariable["RC4Key"])
                    Globalvariable['RSA_Recieved'] = True
                else:
                    self.connexion.send("##YesRsa".encode("Utf8"))
            elif message_recu == "##YesRsa":
                Globalvariable['RSA_Sent'] = True
            elif  message_recu[:6] == "##RC4#":
                if  Globalvariable["OtherRC4"] == "" :
                    Rsa = RSA()
                    Globalvariable["OtherRC4"] = Rsa.decrypt(Globalvariable["d"],Globalvariable["n"],int(message_recu[6:]))     
                    self.connexion.send("##YesRC4".encode("Utf8"))
                else :
                    self.connexion.send("##YesRC4".encode("Utf8"))
            elif message_recu == "##YesRC4":
                    if not  Globalvariable["RC4_sent"]: 
                        Globalvariable["RC4_sent"] = True
                        
            elif Globalvariable['RSA_Sent'] and Globalvariable['RSA_Recieved'] and message_recu[0:14] != "##Rsapubkeyis#" and message_recu != "##YesRsa" and message_recu != "##YesRC4":
                Rc44 = RC4()
                
                Rc44.shuffle(str(Globalvariable["OtherRC4"]))
                
                message = Rc44.Crypt(message_recu)
                print("---->>> " +message)
            


class Threadsend(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn	     
        
    def run(self):
        global Globalvariable
        count = 0
        while 1:
            if not Globalvariable["RSA_Sent"]:
                self.connexion.send(str(
                    "##Rsapubkeyis#"+str(Globalvariable['e'])+"#"+str(Globalvariable['n'])).encode("Utf8"))
                time.sleep(1)
            
            elif Globalvariable["RSA_Sent"] and  Globalvariable["RSA_Recieved"] and not Globalvariable["RC4_sent"]:
                self.connexion.send(str("##RC4#"+str(Globalvariable['EncRC4Key'])).encode("Utf8"))
                time.sleep(1)

            elif Globalvariable["RC4_sent"]:
                if count == 0:
                    print("##### You are connected")
                    count = count + 1
                message_emis = input()
                Rc4 = RC4()
                Rc4.shuffle(Globalvariable["RC4Key"])
                
                
                m = Rc4.Crypt(message_emis)
               
                self.connexion.send(m.encode("Utf8"))


Rsa = RSA()
Globalvariable["d"], (Globalvariable["n"],Globalvariable["e"]) = Rsa.get_keys(512)
Globalvariable["RC4Key"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


th_R = ThreadReceive(mySocket)
th_E = Threadsend(mySocket)

th_E.start()
th_R.start()
