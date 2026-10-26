import math
from dataclasses import dataclass
from itertools import zip_longest

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from kauma.galois import (
    bytes_to_polynomial,
    galois_add,
    galois_multiply,
    polynomial_to_bytes,
)


@dataclass
class EncryptedMessage:
    ciphertext: bytes
    nonce: bytes
    associated_data: bytes
    auth_tag: bytes


def encrypt(
    plaintext: bytes, key: bytes, nonce: bytes, associated_data: bytes
) -> EncryptedMessage:
    ciphertext = _plain_encrypt(plaintext, key, nonce)
    auth_tag = _calculate_auth_tag(ciphertext, key, nonce, associated_data)

    return EncryptedMessage(ciphertext, nonce, associated_data, auth_tag)


def decrypt(encrypted_message: EncryptedMessage, key: bytes) -> bytes:
    plaintext = _plain_decrypt(
        encrypted_message.ciphertext, key, encrypted_message.nonce
    )
    auth_tag = _calculate_auth_tag(
        encrypted_message.ciphertext,
        key,
        encrypted_message.nonce,
        encrypted_message.associated_data,
    )

    if encrypted_message.auth_tag != auth_tag:
        raise ValueError("invalid auth tag")

    return plaintext


def _y_block(nonce: bytes, counter: int) -> bytes:
    if len(nonce) != 12:
        raise ValueError("invalid nonce length")

    return nonce + counter.to_bytes(length=4)


def _calculate_auth_tag(
    ciphertext: bytes, key: bytes, nonce: bytes, associated_data: bytes
) -> bytes:
    auth_key = _encrypt_block(bytes(16), key)

    return _xor(
        _encrypt_block(_y_block(nonce, 1), key),
        _ghash(auth_key, associated_data, ciphertext),
    )


def _encrypt_block(plaintext: bytes, key: bytes) -> bytes:
    if len(plaintext) != 16:
        raise ValueError("invalid block size")

    cipher = Cipher(algorithms.AES128(key), modes.ECB())
    encryptor = cipher.encryptor()

    return encryptor.update(plaintext) + encryptor.finalize()


def _plain_encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    if len(nonce) != 12:
        raise ValueError("invalid nonce length")

    required_stream_block_count = math.ceil(len(plaintext) / 16)
    key_stream = b"".join(
        _encrypt_block(_y_block(nonce, i + 2), key)
        for i in range(0, required_stream_block_count)
    )

    return _xor(plaintext, key_stream)[: len(plaintext)]


def _plain_decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    return _plain_encrypt(ciphertext, key, nonce)


def _xor(a: bytes, b: bytes) -> bytes:
    """
    Padding goes on the *right* if a and b are not the same length
    """
    return bytes(x ^ y for x, y in zip_longest(a, b, fillvalue=0))


def _ghash(
    authentication_key: bytes, associated_data: bytes, ciphertext: bytes
) -> bytes:
    l_block = _bit_length_bytes(associated_data) + _bit_length_bytes(ciphertext)
    blocks = _chunk_and_pad(associated_data) + _chunk_and_pad(ciphertext) + [l_block]

    result = 0
    authentication_key_polynomial = bytes_to_polynomial(authentication_key, "GCM")
    for block in blocks:
        result = galois_add(result, bytes_to_polynomial(block, "GCM"))
        result = galois_multiply(result, authentication_key_polynomial)

    return polynomial_to_bytes(result, "GCM")


def _bit_length_bytes(data: bytes) -> bytes:
    """
    Big-endian encoded 64-bit counters of the bit length
    of a given input bytes object
    """
    return (len(data) * 8).to_bytes(length=8, byteorder="big")


def _chunk_and_pad(data: bytes, chunk_size=16) -> list[bytes]:
    """
    Chunks a byte object into smaller byte objects. Pads zeros on the right
    if a chunk doesn't match the full `chunk_size`
    """
    return [
        data[i : i + chunk_size].ljust(chunk_size, b"\0")
        for i in range(0, len(data), chunk_size)
    ]
