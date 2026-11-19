from kauma.second_exam.bfk_galois import (
    galois_add,
    galois_multiply,
    polynomial_to_bytes,
)


def test_polynomial_to_bytes_constant_term_x():
    assert polynomial_to_bytes(0x00000000000000000000000000000002) == bytes.fromhex(
        "02000000000000000000000000000000"
    )


def test_polynomial_to_bytes_sparse_bits():
    assert polynomial_to_bytes((1 << 88) | (1 << 77)) == bytes.fromhex(
        "00000000000000000020000100000000"
    )


def test_polynomial_to_bytes_top_bit():
    assert polynomial_to_bytes(1 << 127) == bytes.fromhex(
        "00000000000000000000000000000080"
    )


def test_polynomial_to_bytes_arbitrary_value():
    assert polynomial_to_bytes(0xF8D0EC7E616039737FA9C69180F67090) == bytes.fromhex(
        "9070f68091c6a97f733960617eecd0f8"
    )


def test_galois_add():
    a = 0x8C5DF50F9586C172B77ACE8B0ABC2588
    b = 0x22BB52F9F857A1C5351056083FC7F318
    assert galois_add(a, b) == 0xAEE6A7F66DD160B7826A9883357BD690


# def test_galois_multiply():
#     a = 0x8C5DF50F9586C172B77ACE8B0ABC2588
#     b = 0x22BB52F9F857A1C5351056083FC7F318
#     assert galois_multiply(a, b) == 0xA0259C0D0F13EFF3EDB3C0CBF1697831
