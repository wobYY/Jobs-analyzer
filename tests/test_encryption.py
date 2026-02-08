import pytest

from utils.encryption import decrypt_data, encrypt_data


def test_encrypt_decrypt():
    data = "google.com"

    encrypted_data = encrypt_data(data)
    decrypted_data = decrypt_data(encrypted_data)

    assert decrypted_data == data
