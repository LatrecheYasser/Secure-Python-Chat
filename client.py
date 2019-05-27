import socket, sys,threading , random, string
from RSA import RSA 
import time
#from pydispatch import dispatcher

HOST = '127.0.0.1'
PORT = 50010
Globalvariable = {"RSA_Recieved":False,
                    "RSA_Sent":False,
                    "OtherRsaN":0,
                    "OtherRsaD":0,
                    "n":0,
                    "e":0,
                    "d":0,
                    "RC4Key":"",
                    "RC4_sent":False}

# 1) création du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# 2) envoi d'une requête de connexion au serveur :
try:
    mySocket.connect((HOST, PORT))
except socket.error:
    print("Client can't connect")
    sys.exit()
print("Trying to connect\nHandshake step ..... ")

class ThreadReceive(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn	     # réf. du socket de connexion
       
    def run(self):
        global Globalvariable
        while 1:
            message_recu = self.connexion.recv(1024).decode("Utf8")
            if message_recu[0:14] == "##Rsapubkeyis#":
                if not Globalvariable['RSA_Recieved'] :
                    message = message_recu[14:].split("#")
                    Globalvariable['OtherRsaD'], Globalvariable['OtherRsaN'] = int(message[0]),int(message[1])
                    self.connexion.send("##YesRsa".encode("Utf8"))
                    print("###### RSA WAS SENT FROM THE OTHER CLINET")
                    Globalvariable['RSA_Recieved'] = True
                else :
                    self.connexion.send("##YesRsa".encode("Utf8"))
            
            elif not Globalvariable['RSA_Sent'] and message_recu == "##YesRsa":
                Globalvariable['RSA_Sent'] = True
                print("###### RSA WAS SENT TO THE OTHER CLINET ")

            

            elif  Globalvariable['RSA_Sent'] and Globalvariable['RSA_Recieved'] and  message_recu[0:14] != "##Rsapubkeyis#" and  message_recu != "##YesRsa" :
                print("---->>>" + message_recu)
                #print(Globalvariable)
    


class Threadsend(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn	     # réf. du socket de connexion
        
    def run(self):
        global Globalvariable
        count = 0
        while 1:
            if not Globalvariable["RSA_Sent"]:
                self.connexion.send(str("##Rsapubkeyis#"+str(Globalvariable['d'])+"#"+str(Globalvariable['n'])).encode("Utf8"))
                time.sleep(1)
            elif Globalvariable["RSA_Sent"] and Globalvariable["RSA_Recieved"] and not Globalvariable["RC4_sent"]:
                self.connexion.send(str("##RC4IS#"+str(Globalvariable['EncryptedRC4Key'])).encode("Utf8"))
                time.sleep(1)
            else:
                if count == 0:
                    print("##### You are connected")
                    count = count + 1
                message_emis = input()
                self.connexion.send(message_emis.encode("Utf8"))

Rsa = RSA()
Globalvariable["d"],(Globalvariable["n"],Globalvariable["e"])  = Rsa.get_keys(1024)
Globalvariable["RC4Key"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=128))


th_R = ThreadReceive(mySocket)
th_E = Threadsend(mySocket)

th_E.start()
th_R.start()