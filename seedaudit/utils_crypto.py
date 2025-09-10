from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


def encrypt_bytes(key: bytes, plaintext: bytes) -> bytes:
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext, None)
    return nonce + ct


def decrypt_bytes(key: bytes, blob: bytes) -> bytes:
    nonce = blob[:12]
    ct = blob[12:]
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None)
