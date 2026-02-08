import pathlib

import rsa

CWD = pathlib.Path(__file__).parent


with open(CWD / "../public_key.pem", "rb") as f:
    PUBLIC_KEY = rsa.PublicKey.load_pkcs1(f.read())

with open(CWD / "../private_key.pem", "rb") as f:
    PRIVATE_KEY = rsa.PrivateKey.load_pkcs1(f.read())


def encrypt_data(data: str) -> bytes:
    """Encrypts the given data using the RSA public key."""
    data_bytes = data.encode()
    max_len = PUBLIC_KEY.n.bit_length() // 8 - 11  # PKCS#1 v1.5 padding
    chunks = [data_bytes[i : i + max_len] for i in range(0, len(data_bytes), max_len)]
    encrypted_chunks = [rsa.encrypt(chunk, PUBLIC_KEY) for chunk in chunks]
    return b"".join(encrypted_chunks)


def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypts the given encrypted data using the RSA private key."""
    max_len = PRIVATE_KEY.n.bit_length() // 8
    chunks = [
        encrypted_data[i : i + max_len] for i in range(0, len(encrypted_data), max_len)
    ]
    decrypted_chunks = [rsa.decrypt(chunk, PRIVATE_KEY) for chunk in chunks]
    return b"".join(decrypted_chunks).decode()
