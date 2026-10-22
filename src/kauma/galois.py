from typing import Literal

# x^128 + x^7 + x^2 + x + 1
IRREDUCABLE_POLYNOMIAL = 0x100000000000000000000000000000087

Mode = Literal["XEX", "GCM"]


def galois_add(a: int, b: int) -> int:
    return a ^ b


def galois_multiply(
    a: int, b: int, irreducable_polynomial=IRREDUCABLE_POLYNOMIAL
) -> int:
    result = 0
    accumulator = a

    highest_bit = irreducable_polynomial.bit_length() - 1

    while b:
        if b & 1 == 1:
            result ^= accumulator

        accumulator <<= 1
        b >>= 1

        if accumulator >> highest_bit:
            accumulator ^= irreducable_polynomial

    return result
