import pbkdf2
import hashlib
import os

print('AQUI')

def makeKey(password):
    print('password')
    hash = pbkdf2.PBKDF2(hashlib.sha256, password, os.urandom(32), 32000, 16)
    print(hash)

makeKey('batata')
