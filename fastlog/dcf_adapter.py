from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class DCFAdapter:
    def __init__(self, key: bytes = None):
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.cipher = AESGCM(self.key)

    def encrypt(self, plaintext: bytes) -> tuple:
        nonce = os.urandom(12)
        encrypted = self.cipher.encrypt(nonce, plaintext, None)
        # AESGCM outputs ciphertext + 16B auth tag at end
        return encrypted, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes) -> bytes:
        return self.cipher.decrypt(nonce, ciphertext, None)

