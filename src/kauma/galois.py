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
    highest_bit = irreducable_polynomial.bit_length() - 1

    while b:
        if b & 1:
            result ^= a

        a <<= 1
        b >>= 1

        if a >> highest_bit:
            a ^= irreducable_polynomial

    return result


def bytes_to_polynomial(data: bytes, mode: Mode) -> int:
    match mode:
        case "XEX":
            return int.from_bytes(data, byteorder="little")
        case "GCM":
            value = int.from_bytes(data, byteorder="big")
            return int(f"{value:0128b}"[::-1], 2)
        case _:
            raise ValueError("invalid mode")


def polynomial_to_bytes(polynomial: int, mode: Mode) -> bytes:
    match mode:
        case "XEX":
            return polynomial.to_bytes(length=16, byteorder="little")
        case "GCM":
            return int(f"{polynomial:0128b}"[::-1], 2).to_bytes(16, byteorder="big")
        case _:
            raise ValueError("invalid mode")
