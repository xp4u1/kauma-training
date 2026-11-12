def generate_keystream(key: bytes, length: int) -> bytes:
    sbox = _generate_sbox(key)

    i, j = 0, 0
    keystream: list[int] = []

    for _ in range(length):
        i = (i + 1) % 256
        j = (j + sbox[i]) % 256
        sbox[i], sbox[j] = (sbox[j], sbox[i])
        keybyte = sbox[(sbox[i] + sbox[j]) % 256]

        keystream.append(keybyte)

    return bytes(keystream)


def _generate_sbox(key: bytes) -> list[int]:
    j = 0
    sbox = list(range(256))
    for i in range(256):
        j = (j + sbox[i] + key[i % len(key)]) % 256
        sbox[i], sbox[j] = (sbox[j], sbox[i])

    return sbox
