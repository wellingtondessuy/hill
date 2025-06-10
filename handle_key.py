import hashlib
import os

KEY_LENGTH = 4

def checkPassword(password, key, salt):
    currentKey = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=KEY_LENGTH)

    return key == currentKey

def generateKey(password):
    salt = os.urandom(KEY_LENGTH)

    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=KEY_LENGTH)
    
    return [key, salt]