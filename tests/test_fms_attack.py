import os

from kauma.fms_attack import AttackVector, invert_sbox, recover_key
from kauma.rc4 import RC4


def test_invert_sbox():
    sbox = RC4(bytes.fromhex("9f1a3db2696b334a49f24c7b87519264")).sbox
    inverted_sbox = invert_sbox(sbox)

    assert len(sbox) == len(inverted_sbox)

    for i in range(len(sbox)):
        assert inverted_sbox[sbox[i]] == i
        assert sbox[inverted_sbox[i]] == i


def generate_attack_vectors(key: bytes, key_position: int) -> list[AttackVector]:
    attack_vectors = []

    for r in range(256):
        nonce = bytes([key_position + 3, 255, r])
        rc4 = RC4(nonce + key)
        attack_vectors.append(
            AttackVector(nonce=nonce, first_keystream_byte=rc4.next_keystream_byte())
        )

    return attack_vectors


def test_attack():
    key = bytes.fromhex("7feb016e2b815da94b3d61640338f118")
    attack_vectors = []
    for a in range(16):
        attack_vectors += generate_attack_vectors(key, a)

    assert recover_key(16, attack_vectors) == key


def try_endless():
    tries = 0
    recovered_key_count = 0
    while True:
        key = os.urandom(16)
        attack_vectors = []
        for a in range(16):
            attack_vectors += generate_attack_vectors(key, a)

        recovered_key = recover_key(16, attack_vectors)
        if recovered_key == key:
            print(f"recovered key: {recovered_key.hex()}")
            recovered_key_count += 1
        else:
            print(f"unable to recover key: {recovered_key.hex()} != {key.hex()}")

        tries += 1
        print(f"recoverable keys: {(recovered_key_count / tries)*100:.02f}%\n")


if __name__ == "__main__":
    try_endless()
