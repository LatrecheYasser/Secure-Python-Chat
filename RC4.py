import binascii
class RC4():
    def __init__(self):
        self.state = list(range(256))

    def shuffle(self, key):
       
        j = 0
        for i in range(256):
            j = (j + self.state[i] + ord(key[i % len(key)])) % 256
            self.state[i], self.state[j] = self.state[j], self.state[i]
        
       
    def Crypt(self, text):
        
        output = list()
        i = j = 0
        for x in range(len(text)):
            i = (i+1) % 256
            j = (self.state[i]+j) % 256
            self.state[i], self.state[j] = self.state[j], self.state[i]
            output.append(
                chr(ord(text[x]) ^ self.state[(self.state[i]+self.state[j]) % 256]))
        x = ''.join(output)
       
        

        return x




if __name__ == "__main__":
    rc4 = RC4()
    key = input('your key sir : ')
    rc4.shuffle(key)
    rc41 = RC4()
    rc41.shuffle(key)
    while 1:
        message = input('your message : ')
        print(rc4.state)
        E = rc4.Crypt(message)
        
        print('Crypted message is ', E)
        M = rc41.Crypt(E)
        print('your first message is : ', M)
