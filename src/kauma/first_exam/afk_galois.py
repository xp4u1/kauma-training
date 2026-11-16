from kauma.first_exam.helper import gfmul

IRREDUCIBLE_POLYNOMIAL = (1 << 128) | (1 << 71) | (1 << 10) | (1 << 6) | 1


def polynomial_to_bytes(polynomial: int) -> bytes:
    little_encoded = polynomial.to_bytes(length=16, byteorder="little").hex()

    return bytes.fromhex(
        "".join([little_encoded[i + 1] + little_encoded[i] for i in range(0, 32, 2)])
    )


def bytes_to_polynomial(data: bytes) -> int:
    data_hex = data.hex()

    return int.from_bytes(
        bytes.fromhex(
            "".join([data_hex[i + 1] + data_hex[i] for i in range(0, 32, 2)])
        ),
        byteorder="little",
    )


if __name__ == "__main__":
    # print(polynomial_to_bytes(1).hex())
    # print(polynomial_to_bytes(1 | (1 << 1)).hex())
    # print(polynomial_to_bytes((1 << 10) | (1 << 2) | 1).hex())
    # print(polynomial_to_bytes((1 << 127) | 1).hex())

    # (a^127 + 1) * (a^127 + a^67 + 1)?
    product = gfmul(
        ((1 << 127) | 1), ((1 << 127) | (1 << 67) | 1), IRREDUCIBLE_POLYNOMIAL
    )
    print(polynomial_to_bytes(product).hex())

    factor_1 = bytes_to_polynomial(bytes.fromhex("0102030405060708090a0b0c0d0e0f67"))
    factor_2 = bytes_to_polynomial(bytes.fromhex("112233445566778899aabbccddeeff67"))
    product = gfmul(factor_1, factor_2, IRREDUCIBLE_POLYNOMIAL)
    print(polynomial_to_bytes(product).hex())
