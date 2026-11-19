from kauma.second_exam.helper import gfmul

IRREDUCIBLE_POLYNOMIAL = (1 << 128) | (1 << 71) | (1 << 10) | (1 << 6) | 1


def galois_add(a: int, b: int) -> int:
    return a ^ b


def galois_multiply(a: int, b: int) -> int:
    return gfmul(a, b, IRREDUCIBLE_POLYNOMIAL)


def bytes_to_polynomial(data: bytes) -> int:
    return int.from_bytes(data, byteorder="little")


def polynomial_to_bytes(polynomial: int) -> bytes:
    return polynomial.to_bytes(length=16, byteorder="little")


def galois_power(base: int, exponent: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = galois_multiply(result, base)
        base = galois_multiply(base, base)
        exponent >>= 1

    return result


def galois_inverse(a: int) -> int:
    if a == 0:
        raise ValueError("0 has no inverse")
    degree = IRREDUCIBLE_POLYNOMIAL.bit_length() - 1
    return galois_power(a, (1 << degree) - 2)


if __name__ == "__main__":
    assert polynomial_to_bytes(0x00000000000000000000000000000002) == bytes.fromhex(
        "02000000000000000000000000000000"
    )
    assert polynomial_to_bytes((1 << 88) | (1 << 77)) == bytes.fromhex(
        "00000000000000000020000100000000"
    )
    assert polynomial_to_bytes(1 << 127) == bytes.fromhex(
        "00000000000000000000000000000080"
    )
    assert polynomial_to_bytes(0xF8D0EC7E616039737FA9C69180F67090) == bytes.fromhex(
        "9070f68091c6a97f733960617eecd0f8"
    )

    a = 0x8C5DF50F9586C172B77ACE8B0ABC2588
    b = 0x22BB52F9F857A1C5351056083FC7F318

    assert galois_add(a, b) == 0xAEE6A7F66DD160B7826A9883357BD690
    assert (
        galois_multiply(a, b) == 0xA0259C0D0F13EFF3EDB3C0CBF1697831
    )  # fails? und im encrypt funktioniert es, hä
