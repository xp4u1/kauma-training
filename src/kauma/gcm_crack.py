"""
Attack AES-GCM encrypted messages that reuse the same nonce.
https://dhbw.johannes-bauer.com/lectures/2026_10_kauma/week03 (slide 34-40)
"""

from kauma.aes_gcm import (
    EncryptedMessage,
    _bit_length_bytes,
    _chunk_and_pad,
    _ghash,
    _xor,
)
from kauma.factorization import factorize
from kauma.galois import bytes_to_polynomial, polynomial_to_bytes
from kauma.polynomial import Polynomial


def forge_message(
    messages: tuple[EncryptedMessage, EncryptedMessage, EncryptedMessage],
    ciphertext: bytes,
    associated_data: bytes,
) -> EncryptedMessage:
    message_a, message_b, message_c = messages
    auth_key, mask = recover_auth_key_and_mask(message_a, message_b, message_c)
    auth_tag = _xor(_ghash(auth_key, associated_data, ciphertext), mask)

    return EncryptedMessage(ciphertext, message_a.nonce, associated_data, auth_tag)


def recover_auth_key_and_mask(
    message_a: EncryptedMessage,
    message_b: EncryptedMessage,
    message_c: EncryptedMessage,
) -> tuple[bytes, bytes]:
    for key in auth_key_candidates(message_a, message_b):
        mask = _xor(
            _ghash(key, message_a.associated_data, message_a.ciphertext),
            message_a.auth_tag,
        )
        expected_tag = _xor(
            _ghash(key, message_c.associated_data, message_c.ciphertext), mask
        )
        if expected_tag == message_c.auth_tag:
            return key, mask

    raise ValueError("no auth key candidate authenticates message_c")


def auth_key_candidates(
    u: EncryptedMessage,
    v: EncryptedMessage,
) -> list[bytes]:
    if u.nonce != v.nonce:
        raise ValueError("messages have to reuse a nonce")

    u_coefficients = ghash_coefficients(u)
    u_tag = bytes_to_polynomial(u.auth_tag, "GCM")

    v_coefficients = ghash_coefficients(v)
    v_tag = bytes_to_polynomial(v.auth_tag, "GCM")

    u_polynomial = Polynomial([u_tag] + list(reversed(u_coefficients)))
    v_polynomial = Polynomial([v_tag] + list(reversed(v_coefficients)))

    factors = factorize(u_polynomial + v_polynomial)

    candidate_polynomials = [
        factor.coefficients[0] for factor in factors if factor.degree() == 1
    ]
    candidate_bytes = [
        polynomial_to_bytes(polynomial, "GCM") for polynomial in candidate_polynomials
    ]

    return candidate_bytes


def ghash_coefficients(message: EncryptedMessage) -> list[int]:
    l_block = _bit_length_bytes(message.associated_data) + _bit_length_bytes(
        message.ciphertext
    )
    blocks = (
        _chunk_and_pad(message.associated_data)
        + _chunk_and_pad(message.ciphertext)
        + [l_block]
    )
    coefficients = [bytes_to_polynomial(block, "GCM") for block in blocks]

    return coefficients
