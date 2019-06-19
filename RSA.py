import rsa
import gmpy2
import struct


class RSA(object):

    def get_p_q(self, bits):
        return rsa.prime.getprime(bits), rsa.prime.getprime(bits)

    def get_e(self, phi):
        return phi-1

    def get_keys(self, bits):
        # firstly we get q and p
        p, q = self.get_p_q(bits)
        n = p*q
        phi = (p-1)*(q-1)
        # anfter that we get e
        e = self.get_e(phi)
        # get the invers of e module phi
        d = int(gmpy2.invert(e, phi).digits())
        return d, (n, e)

    def crypt(self, e, n, message):
        E = int.from_bytes(bytes(message.encode()), byteorder='little')
        return pow(E, e, n)

    def decrypt(self, d, n, message):
        msg = pow(message, d, n).to_bytes((message.bit_length()//8)+1, byteorder='little').strip(b'\x00').decode("utf-8")
        return msg

if __name__ == "__main__":
    bits = int(input('entre the number of bits in te keys : '))
    Rsa = RSA()
    d, (n, e) = Rsa.get_keys(1024)
    message = input('Write your message here : ')
    a = Rsa.crypt(e, n, message)
    print(a)
    b = Rsa.decrypt(d, n, a)
    print('the decripted message is : ', b)
