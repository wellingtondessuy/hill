import hashlib
import os
import codecs
import sys

KEY_LENGTH = 4

def checkPassword(password, key, salt):
    currentKey = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=KEY_LENGTH)

    return key == currentKey

def generateKey(password):
    salt = os.urandom(KEY_LENGTH)

    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=KEY_LENGTH)
    
    return [key, salt]

def getKey(password, is_ciphering):
    # Caso esteja criptografando, gera a chave a partir da senha definida
    if is_ciphering:
        keyData = generateKey(password)
        key = keyData[0]
        salt = keyData[1]

        keyFile = codecs.open(".key", "wb");
        keyFile.write(key)
        keyFile.close()

        saltFile = codecs.open(".salt", "wb");
        saltFile.write(salt)
        saltFile.close()
    # Caso esteja decriptografando, busca a chave nos arquivos
    else:
        keyFile = codecs.open(".key", "rb");
        saltFile = codecs.open(".salt", "rb");

        key = keyFile.read()
        salt = saltFile.read()

        if not checkPassword(password, key, salt):
            print("Senha inválida!")
            sys.exit(1)

    return key
