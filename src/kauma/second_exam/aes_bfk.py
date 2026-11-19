from kauma.second_exam.bfk_galois import (
    bytes_to_polynomial,
    galois_inverse,
    galois_multiply,
    polynomial_to_bytes,
)
from kauma.second_exam.helper import aes128_dec, aes128_enc, xorblk


class AuthenticationError(Exception):
    pass


def derive_keys(key: bytes) -> tuple[bytes, bytes, bytes]:
    s = aes128_enc(key=key, plaintext=bytes([0xFF] * 16))
    t = aes128_enc(key=key, plaintext=bytes([0xAA] * 16))
    u = aes128_enc(key=key, plaintext=bytes([0x55] * 16))

    return (s, t, u)


def generate_tweak(sector_number: int) -> bytes:
    return sector_number.to_bytes(length=16, byteorder="little")


def generate_block_polynomials() -> list[tuple[int, int]]:
    """
    Returns:
        list of tuples (Rn, Qn)
    """

    r = []
    q = []

    accumulator = 1 << 127
    for i in range(32):
        r.append(1 << (i + 1))
        q.append(accumulator)
        accumulator = galois_multiply(accumulator, accumulator)

    return list(zip(r, q))


def generate_auth_tag(sector_number: int, key: bytes, ciphertext_data: bytes) -> bytes:
    s, _t, u = derive_keys(key)
    ciphertext_chunks = chunk_bytes(ciphertext_data)
    encrypted_tweak = aes128_dec(s, generate_tweak(sector_number))
    encrypted_tweak = aes128_dec(s, generate_tweak(sector_number))
    block_polynomials = generate_block_polynomials()
    r32 = block_polynomials[31][0]

    if len(ciphertext_chunks) != 31:
        raise ValueError(
            "invalid ciphertext length. provide the ciphertext without auth tag block"
        )

    auth_accumulator = bytes_to_polynomial(
        xorblk(encrypted_tweak, polynomial_to_bytes(r32))
    )

    for chunk in ciphertext_chunks:
        auth_accumulator = bytes_to_polynomial(
            aes128_enc(s, polynomial_to_bytes(auth_accumulator))
        )
        auth_accumulator = galois_multiply(auth_accumulator, bytes_to_polynomial(chunk))

    auth_tag = aes128_dec(u, polynomial_to_bytes(auth_accumulator))

    return auth_tag


def encrypt_sector(sector_number: int, key: bytes, plaintext: bytes) -> bytes:
    if len(plaintext) != 496:
        raise ValueError("plaintext length != 496")

    s, t, u = derive_keys(key)
    plaintext_chunks = chunk_bytes(plaintext)
    encrypted_tweak = aes128_dec(s, generate_tweak(sector_number))
    block_polynomials = generate_block_polynomials()

    ciphertext_bytes = []

    r32 = block_polynomials[31][0]
    auth_accumulator = bytes_to_polynomial(
        xorblk(encrypted_tweak, polynomial_to_bytes(r32))
    )

    for index, chunk in enumerate(plaintext_chunks):
        r, q = block_polynomials[index]
        stream = aes128_enc(t, xorblk(encrypted_tweak, polynomial_to_bytes(r)))

        chunk = xorblk(chunk, stream)
        chunk = aes128_dec(s, chunk)
        chunk = polynomial_to_bytes(galois_multiply(bytes_to_polynomial(chunk), q))

        ciphertext_bytes.append(chunk)

        auth_accumulator = bytes_to_polynomial(
            aes128_enc(s, polynomial_to_bytes(auth_accumulator))
        )
        auth_accumulator = galois_multiply(auth_accumulator, bytes_to_polynomial(chunk))

    auth_tag = aes128_dec(u, polynomial_to_bytes(auth_accumulator))
    ciphertext_bytes += [auth_tag]

    return b"".join(ciphertext_bytes)


def decrypt_sector(
    sector_number: int, key: bytes, ciphertext: bytes, check_auth_tag=True
) -> bytes:
    if len(ciphertext) != 512:
        raise ValueError("ciphertext length != 512")

    s, t, _u = derive_keys(key)
    ciphertext_data = ciphertext[:496]
    auth_tag = ciphertext[496:]
    ciphertext_chunks = chunk_bytes(ciphertext_data)
    encrypted_tweak = aes128_dec(s, generate_tweak(sector_number))
    block_polynomials = generate_block_polynomials()

    plaintext_bytes = []

    for index, chunk in enumerate(ciphertext_chunks):
        r, q = block_polynomials[index]
        stream = aes128_enc(t, xorblk(encrypted_tweak, polynomial_to_bytes(r)))

        chunk = polynomial_to_bytes(
            galois_multiply(bytes_to_polynomial(chunk), galois_inverse(q))
        )
        chunk = aes128_enc(s, chunk)
        chunk = xorblk(chunk, stream)

        plaintext_bytes.append(chunk)

    if check_auth_tag:
        if generate_auth_tag(sector_number, key, ciphertext_data) != auth_tag:
            raise AuthenticationError("invalid auth tag")

    return b"".join(plaintext_bytes)


def chunk_bytes(data: bytes, chunk_size=16) -> list[bytes]:
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


if __name__ == "__main__":
    key = bytes.fromhex("5442d887b5345eaead347ab5d1e73624")
    message = bytes.fromhex(
        "cbb1ce4d98b3be6e32bc7e92cf2767e9a010dddc080dc6074b1f0e5c6b8651b7ac6c9d281ce97866d7d9f651c70fbbdc2128f98d2086c5b1cef832147551e0e5b9bf49e56f2a99032fb28e42755f1e8d8c039b2f2f3485b8c73740ba5c91c6147f412e3dbfc8670bb6f3b50e71313a9dab4a645f9930ca5c12976d46c5ef5fcbdccc49f6aa217453fa7956cd639f8b29147b404d7bdb58a00fe1ca05a57ecf4edbc7c5de604633ebd5471b48bcd1489ef7a2269bee750dcc04a388b16822de800dd3052a6d247b7f4c21da1ccdd8ae71dcdd347d61c89e750d97b8ac445c68910336d290a35f277995e1c5815b2b9c50d9367551eae723fe0777bd1ca0f58f8e87e6a25e450722c50ab89681d0045e8c8be7f9db9e8a9fffcfc9c8b2aba80e62a0e42aae464eb8dc8a8c037e045b0ebca01683d51dfa2f051923688ce06605425ba4462cb5f4520683c37f3ec8816eb8db93f029094687262aa0cdea3a08ab7f4828d072fb7fffd5578b36faf85d0ad275b6b207f5a550cf53a17dc1ea9b48e1397e790cdbd45e56054a52ae5c029c72cf4a7de64c1a640dde4338bff4f33a949fe8f5453c0d47b0ed9cda0dacf11c975b738c5f2f5ee6ac5339f4a86de8cc953ade322fd07e108e3743aa28c069436706093a032bf57a53dd510c8ebd61b0ee45411ffaf8a1ac362ac2178cea80db9e0e5889019c5dc2f0c570e0b20a645588"
    )
    print(decrypt_sector(2024, key, message).decode())
