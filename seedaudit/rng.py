import secrets
import hashlib

def secure_random_bytes(n=32):
    """Genera bytes aleatorios seguros"""
    return secrets.token_bytes(n)

def mnemonic_from_entropy(entropy: bytes) -> str:
    """Crea un mnemonic simple desde entropía (ejemplo educativo)."""
    h = hashlib.sha256(entropy).hexdigest()
    words = [h[i:i+4] for i in range(0, len(h), 4)]
    return " ".join(words[:12])  # 12 palabras
