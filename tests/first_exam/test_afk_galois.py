from kauma.first_exam.afk_galois import (
    IRREDUCIBLE_POLYNOMIAL,
    bytes_to_polynomial,
    polynomial_to_bytes,
)
from kauma.first_exam.helper import gfmul


def test_polynomial_bytes_conversion():
    assert (
        polynomial_to_bytes(1 | (1 << 7))
        == b"\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )  # 0001 1000 ...
    assert polynomial_to_bytes(0x7BD7F582A641B4DA44A259C7E46D63CC) == bytes.fromhex(
        "cc36d64e7c952a44ad4b146a285f7db7"
    )

    for i in range(0, 100):
        assert bytes_to_polynomial(polynomial_to_bytes(i)) == i


def test_polynomial_multiplication():
    assert (
        gfmul(
            0xDEADAFFEDEADBEEFDEADC0FFEE,
            0xC0FFEEBABEC0FFEEBABE1337,
            IRREDUCIBLE_POLYNOMIAL,
        )
        == 0x7BD7F582A641B4DA44A259C7E46D63CC
    )
