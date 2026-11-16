from dataclasses import dataclass
from typing import Counter

from kauma.rc4 import RC4


@dataclass
class AttackVector:
    nonce: bytes
    first_keystream_byte: int


def invert_sbox(sbox: list[int]) -> list[int]:
    inverted_sbox = [0] * len(sbox)
    for i in range(len(sbox)):
        inverted_sbox[sbox[i]] = i

    return inverted_sbox


def attack_single_byte(known_key: bytes, attack_vectors: list[AttackVector]) -> bytes:
    key_position = len(known_key)
    relevant_vectors = [
        vector for vector in attack_vectors if vector.nonce[0] == key_position + 3
    ]

    if len(relevant_vectors) < 1:
        raise ValueError(f"no vectors for position {key_position} found")

    key_byte_candidates: list[bytes] = []
    for vector in relevant_vectors:
        rc4 = RC4(vector.nonce)
        rc4._generate_partial_sbox(
            vector.nonce + known_key, stop_after=(key_position + 3)
        )

        inverted_sbox = invert_sbox(rc4.sbox)

        candidate = (
            inverted_sbox[vector.first_keystream_byte]
            - rc4.j
            - rc4.sbox[key_position + 3]
        ) % 256

        key_byte_candidates.append(bytes([candidate]))

    return Counter(key_byte_candidates).most_common(1)[0][0]


def recover_key(key_length: int, attack_vectors: list[AttackVector]) -> bytes:
    """
    Perform an FSM attack on a list of weak IVs

    Args:
        key_length: Length of the key that should be recovered in bytes
        attack_vectors: list of weak nonces with the first ciphertext byte
    """

    key_bytes = bytearray()
    for _a in range(key_length):
        new_byte = attack_single_byte(bytes(key_bytes), attack_vectors)
        key_bytes += new_byte

    return bytes(key_bytes)
