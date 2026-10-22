import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from kauma.aes_gcm import encrypt


def test_encrypt():
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"Hello world!"
    associated_data = b"you can't read the encrypted message!"

    encrypted_message = encrypt(plaintext, key, nonce, associated_data)
    assert encrypted_message.associated_data == associated_data
    assert encrypted_message.nonce == nonce

    encryptor = Cipher(
        algorithm=algorithms.AES128(key), mode=modes.GCM(nonce)
    ).encryptor()

    encryptor.authenticate_additional_data(associated_data)
    lib_ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    lib_auth_tag = encryptor.tag

    assert encrypted_message.ciphertext == lib_ciphertext
    assert encrypted_message.auth_tag == lib_auth_tag
