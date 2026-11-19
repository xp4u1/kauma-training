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
