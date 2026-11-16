from kauma.rc4 import RC4


def test_generate_keystream():
    """https://datatracker.ietf.org/doc/html/rfc6229#section-2"""

    rc4 = RC4(bytes.fromhex("0102030405"))
    keystream = rc4.next_keystream(4096 + 16)

    assert keystream[0:16] == bytes.fromhex(
        "b2 39 63 05  f0 3d c0 27   cc c3 52 4a  0a 11 18 a8"
    )
    assert keystream[16:32] == bytes.fromhex(
        "69 82 94 4f  18 fc 82 d5   89 c4 03 a4  7a 0d 09 19"
    )
    assert keystream[240:256] == bytes.fromhex(
        "28 cb 11 32  c9 6c e2 86   42 1d ca ad  b8 b6 9e ae"
    )
    assert keystream[4096 : 4096 + 16] == bytes.fromhex(
        "ff 25 b5 89  95 99 67 07   e5 1f bd f0  8b 34 d8 75"
    )

    rc4 = RC4(bytes.fromhex("0102030405060708090a0b0c0d0e0f10"))
    keystream = rc4.next_keystream(4096 + 16)

    assert keystream[0:16] == bytes.fromhex(
        "9a c7 cc 9a  60 9d 1e f7   b2 93 28 99  cd e4 1b 97"
    )
    assert keystream[4096 : 4096 + 16] == bytes.fromhex(
        "a3 6a 4c 30  1a e8 ac 13   61 0c cb c1  22 56 ca cc"
    )
