import os
from Crypto.PublicKey import RSA

f = open("protected/crypto/passwords_hs256_main.key", "rb")
PASSWORDS_HS256_MAIN_KEY = f.read()
f.close()