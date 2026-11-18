from kauma.first_exam.afk_galois import (
    IRREDUCIBLE_POLYNOMIAL,
    bytes_to_polynomial,
    polynomial_to_bytes,
)
from kauma.first_exam.helper import aes128_dec, aes128_enc, gfmul, xorblk


def derive_keypair(key: bytes) -> tuple[bytes, bytes]:
    s = aes128_enc(key, bytes(16))
    s_polynomial = bytes_to_polynomial(s)
    t = polynomial_to_bytes(gfmul(s_polynomial, s_polynomial, IRREDUCIBLE_POLYNOMIAL))

    return (s, t)


def generate_block_polynomials() -> list[int]:
    polynomials = []
    accumulator = 1 << 127
    for _ in range(32):
        polynomials.append(accumulator)
        accumulator = gfmul(accumulator, accumulator, IRREDUCIBLE_POLYNOMIAL)

    return polynomials


def encrypted_tweak(sector: int, s_key: bytes) -> bytes:
    return aes128_enc(s_key, sector.to_bytes(length=16, byteorder="little"))


def chunk(data: bytes, chunk_size=16) -> list[bytes]:
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def decrypt(ciphertext: bytes, key: bytes, sector: int) -> bytes:
    raw_chunks = chunk(ciphertext, 16)
    s, t = derive_keypair(key)
    tweak_bytes = encrypted_tweak(sector, s)
    tweak_polynomial = bytes_to_polynomial(tweak_bytes)
    block_polynomials = generate_block_polynomials()

    if len(raw_chunks) != len(block_polynomials):
        raise ValueError("invalid number of chunks")

    plaintext = []
    for block_polynomial, raw_chunk in zip(block_polynomials, raw_chunks):
        stream = aes128_enc(
            t,
            polynomial_to_bytes(
                gfmul(
                    tweak_polynomial,
                    block_polynomial,
                    IRREDUCIBLE_POLYNOMIAL,
                )
            ),
        )
        plaintext.append(xorblk(aes128_dec(s, raw_chunk), stream))

    return b"".join(plaintext)


if __name__ == "__main__":
    # print({i: b.hex() for i, b in p_map.items()})
    # print(p_map[1].hex())
    # print(p_map[31].hex())

    k = bytes.fromhex("e70e8593324aae130b86596fdb669114")
    s, t = derive_keypair(k)
    print(f"s={s.hex()}, t={t.hex()}")
