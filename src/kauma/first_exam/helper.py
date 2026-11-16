"""
Provided helper functions from "Helper.py"
"""

import socket
import struct

import cryptography.hazmat.primitives.ciphers


class VirtualHardDisk:
    """Abstrahiert die virtuelle Festplatte. Benutzung:

    with VirtualHardDisk("theta.cs.dhbw-mannheim.de") as vdd:
            print(vdd.read(offset = 123, length = 100))		# Lese 100 Bytes ab Byteoffset 123
            vdd.write(offset = 9, data = b"foobar!")		# Schreibe b'foobar!' an Byteoffset 9
    """

    READ_WRITE_CMD = struct.Struct("< B Q H")

    def __init__(self, hostname: str):
        assert isinstance(hostname, str)
        self._hostname = hostname
        self._port = 8712
        self._conn = None

    def read(self, offset: int, length: int):
        """Maximale Lesemenge dieses Kommandos betrÃ¤gt 1024 Bytes."""
        assert isinstance(offset, int)
        assert isinstance(length, int)
        assert length > 0
        assert length <= 1024
        cmd = self.READ_WRITE_CMD.pack(1, offset, length)
        self._conn.sendall(cmd)
        recvd = bytearray()
        remaining = length
        while remaining > 0:
            chunk = self._conn.recv(remaining)
            if len(chunk) == 0:
                raise ValueError(
                    f"Server closed connection. Received so far: {len(recvd)} of {length} bytes {recvd.hex()}"
                )
            recvd += chunk
            remaining = length - len(recvd)
        return recvd

    def write(self, offset: int, data: bytes):
        """Maximale Schreibmenge dieses Kommandos betrÃ¤gt 1024 Bytes."""
        assert isinstance(offset, int)
        assert len(data) <= 1024
        cmd = self.READ_WRITE_CMD.pack(2, offset, len(data)) + data
        self._conn.sendall(cmd)

    def __enter__(self):
        self._conn = socket.create_connection((self._hostname, self._port))
        return self

    def __exit__(self, *args):
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def aes128_enc(key: bytes, plaintext: bytes):
    """AES-128 ECB encryption of a single block"""
    assert isinstance(key, bytes)
    assert isinstance(plaintext, (bytes, bytearray))
    assert len(key) == 16
    assert len(plaintext) == 16
    encryptor = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES128(key),
        cryptography.hazmat.primitives.ciphers.modes.ECB(),
    ).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext


def aes128_dec(key: bytes, ciphertext: bytes):
    """AES-128 ECB decryption of a single block"""
    assert isinstance(key, bytes)
    assert isinstance(ciphertext, (bytes, bytearray))
    assert len(key) == 16
    assert len(ciphertext) == 16
    decryptor = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES128(key),
        cryptography.hazmat.primitives.ciphers.modes.ECB(),
    ).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext


def gfmul(a: int, b: int, poly: int):
    """Compute A * B MOD poly in GF(2^m)"""
    assert isinstance(a, int)
    assert isinstance(b, int)
    assert isinstance(poly, int)
    m = poly.bit_length() - 1
    result = 0
    accu = a
    for bit in range(b.bit_length()):
        if (b >> bit) & 1:
            result = result ^ accu
        accu = accu << 1
        if (accu >> m) & 1:
            accu ^= poly
    return result


def xorblk(a: bytes, b: bytes):
    assert isinstance(a, (bytes, bytearray))
    assert isinstance(b, (bytes, bytearray))
    assert len(a) == len(b)
    return bytes(x ^ y for (x, y) in zip(a, b))


assert gfmul(0xE2, 0x85, 0x14D) == 0x78
assert aes128_enc(
    key=bytes.fromhex("4b9095c3ac00563054b1cd6438bc9b96"),
    plaintext=bytes.fromhex("3167488cf3820f9f927c9cf99b950449"),
) == bytes.fromhex("1d 4b a9 f1 07 40 16 84  4e 83 08 0c e7 9b cf 33")
assert aes128_dec(
    key=bytes.fromhex("4b9095c3ac00563054b1cd6438bc9b96"),
    ciphertext=aes128_enc(
        key=bytes.fromhex("4b9095c3ac00563054b1cd6438bc9b96"),
        plaintext=bytes.fromhex("3167488cf3820f9f927c9cf99b950449"),
    ),
) == bytes.fromhex("3167488cf3820f9f927c9cf99b950449")
