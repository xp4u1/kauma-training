from kauma.galois import galois_add, galois_multiply


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
