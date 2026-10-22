from kauma.galois import (
    bytes_to_polynomial,
    galois_add,
    galois_multiply,
    polynomial_to_bytes,
)


def test_galois_add():
    assert galois_add(0b01, 0b01) == 0b00
    assert galois_add(0b00, 0b00) == 0b00
    assert galois_add(0b01, 0b00) == 0b01
    assert galois_add(0b01, 0b10) == 0b11


def test_galois_multiply():
    assert galois_multiply(0b01, 0b01) == 0b01
    assert galois_multiply(0b00, 0b01) == 0b00
    assert galois_multiply(0b10, 0b01) == 0b10
    assert galois_multiply(0b10, 0b10) == 0b100

    # https://dhbw.johannes-bauer.com/lectures/2026_10_kauma/week03
    # Folie 54
    assert galois_multiply(0b11000100, 0b10000101, 0x14D) == 0b10111000


def test_bytes_to_polynomial_xex():
    assert (
        bytes_to_polynomial(bytes.fromhex("80" + "00" * 15), "XEX") == 1 << 7
    )  # 10000000 00000000 ...
    assert bytes_to_polynomial(bytes.fromhex("01" + "00" * 15), "XEX") == 1 << 0
    assert bytes_to_polynomial(bytes.fromhex("0001" + "00" * 14), "XEX") == 1 << 8
    assert bytes_to_polynomial(bytes.fromhex("0011" + "00" * 14), "XEX") == (1 << 8) | (
        1 << 12
    )
    assert bytes_to_polynomial(bytes.fromhex("00" * 15 + "80"), "XEX") == 1 << 127


def test_bytes_to_polynomial_gcm():
    assert bytes_to_polynomial(bytes.fromhex("80" + "00" * 15), "GCM") == 1
    assert bytes_to_polynomial(bytes.fromhex("01" + "00" * 15), "GCM") == 1 << 7
    assert bytes_to_polynomial(bytes.fromhex("0001" + "00" * 14), "GCM") == 1 << 15
    assert bytes_to_polynomial(bytes.fromhex("0011" + "00" * 14), "GCM") == (
        1 << 15
    ) | (1 << 11)
    assert bytes_to_polynomial(bytes.fromhex("00" * 15 + "80"), "GCM") == 1 << 120


def test_polynomial_to_bytes_xex():
    assert polynomial_to_bytes(1 << 7, "XEX") == bytes.fromhex("80" + "00" * 15)
    assert polynomial_to_bytes(1 << 0, "XEX") == bytes.fromhex("01" + "00" * 15)
    assert polynomial_to_bytes(1 << 8, "XEX") == bytes.fromhex("0001" + "00" * 14)
    assert polynomial_to_bytes((1 << 8) | (1 << 12), "XEX") == bytes.fromhex(
        "0011" + "00" * 14
    )
    assert polynomial_to_bytes(1 << 127, "XEX") == bytes.fromhex("00" * 15 + "80")


def test_polynomial_to_bytes_gcm():
    assert polynomial_to_bytes(1, "GCM") == bytes.fromhex("80" + "00" * 15)
    assert polynomial_to_bytes(1 << 7, "GCM") == bytes.fromhex("01" + "00" * 15)
    assert polynomial_to_bytes(1 << 15, "GCM") == bytes.fromhex("0001" + "00" * 14)
    assert polynomial_to_bytes((1 << 15) | (1 << 11), "GCM") == bytes.fromhex(
        "0011" + "00" * 14
    )
    assert polynomial_to_bytes(1 << 120, "GCM") == bytes.fromhex("00" * 15 + "80")
