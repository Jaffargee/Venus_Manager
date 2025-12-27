"""
Encryption API for Venus File Manager
Handles file encryption and decryption using AES-256
"""

import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import json
import logging

logger = logging.getLogger(__name__)

class EncryptionAPI:
    """API for file encryption/decryption operations"""

    def __init__(self):
        self.backend = default_backend()
        self._setup_keys()

    def _setup_keys(self):
        """Generate or load RSA key pair and AES key"""
        self.temp_dir = self._get_temp_dir()
        self.key_file = os.path.join(self.temp_dir, "encryption_keys.json")

        if os.path.exists(self.key_file):
            self._load_keys()
        else:
            self._generate_keys()
            self._save_keys()

    def _get_temp_dir(self) -> str:
        """Get platform-specific temp directory for keys"""
        if sys.platform == "win32":
            return os.path.join(os.environ.get('TEMP', 'C:\\Temp'), '.venus_keys')
        else:
            return "/tmp/.venus_keys"

    def _generate_keys(self):
        """Generate new RSA key pair and AES key"""
        # Generate RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        self.public_key = self.private_key.public_key()

        # Generate AES key
        self.aes_key = os.urandom(32)  # 256-bit key

        # Encrypt AES key with RSA public key
        self.encrypted_aes_key = self.public_key.encrypt(
            self.aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def _save_keys(self):
        """Save keys to file"""
        os.makedirs(self.temp_dir, exist_ok=True)

        # Serialize private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        keys_data = {
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(self.encrypted_aes_key).decode('utf-8'),
            'aes_key': base64.b64encode(self.aes_key).decode('utf-8')  # For convenience, but should be removed in production
        }

        with open(self.key_file, 'w') as f:
            json.dump(keys_data, f)

    def _load_keys(self):
        """Load keys from file"""
        with open(self.key_file, 'r') as f:
            keys_data = json.load(f)

        # Deserialize private key
        self.private_key = serialization.load_pem_private_key(
            keys_data['private_key'].encode('utf-8'),
            password=None,
            backend=self.backend
        )

        # Deserialize public key
        self.public_key = serialization.load_pem_public_key(
            keys_data['public_key'].encode('utf-8'),
            backend=self.backend
        )

        # Load encrypted AES key
        self.encrypted_aes_key = base64.b64decode(keys_data['encrypted_aes_key'])
        self.aes_key = base64.b64decode(keys_data['aes_key'])

    def encrypt_file(self, file_path: str, password: str = None) -> bool:
        """Encrypt a file using AES-256"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()

            # Generate IV
            iv = os.urandom(16)

            # Create cipher
            cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()

            # Pad data to block size
            block_size = 16
            padding_length = block_size - (len(data) % block_size)
            padded_data = data + bytes([padding_length]) * padding_length

            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            # Write encrypted file
            encrypted_file = file_path + '.encrypted'
            with open(encrypted_file, 'wb') as f:
                f.write(iv + encrypted_data)

            logger.info(f"Encrypted file: {file_path} -> {encrypted_file}")
            return True

        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {e}")
            return False

    def decrypt_file(self, file_path: str, password: str = None) -> bool:
        """Decrypt a file using AES-256"""
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            # Extract IV
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]

            # Create cipher
            cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()

            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            padding_length = padded_data[-1]
            data = padded_data[:-padding_length]

            # Write decrypted file
            decrypted_file = file_path.replace('.encrypted', '_decrypted')
            if decrypted_file == file_path:
                decrypted_file = file_path + '_decrypted'

            with open(decrypted_file, 'wb') as f:
                f.write(data)

            logger.info(f"Decrypted file: {file_path} -> {decrypted_file}")
            return True

        except Exception as e:
            logger.error(f"Error decrypting file {file_path}: {e}")
            return False

    def encrypt_directory(self, dir_path: str) -> bool:
        """Encrypt all files in a directory"""
        success = True
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not self.encrypt_file(file_path):
                    success = False
        return success

    def decrypt_directory(self, dir_path: str) -> bool:
        """Decrypt all encrypted files in a directory"""
        success = True
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.encrypted'):
                    file_path = os.path.join(root, file)
                    if not self.decrypt_file(file_path):
                        success = False
        return success

# Global instance
encryption_api = EncryptionAPI()
# <parameter name="filePath">c:\Users\Tahir General\Downloads\File-Manager\JSIIT-22-NDCS-0024 - JSIIT-22-NDCS-0025\encryption_api.py