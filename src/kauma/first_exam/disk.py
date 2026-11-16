from kauma.first_exam.aes_afk import decrypt, derive_keypair, encrypted_tweak
from kauma.first_exam.helper import VirtualHardDisk


def get_position(offset: int) -> tuple[int, int]:
    """
    Returns (sector, sector_offset)
    """

    return divmod(offset, 512)


def read_sector(disk: VirtualHardDisk, sector: int, key: bytes) -> bytes:
    raw_bytes = bytes(disk.read(offset=512 * sector, length=512))
    return decrypt(raw_bytes, key, sector)


if __name__ == "__main__":
    # with VirtualHardDisk("theta.cs.dhbw-mannheim.de") as vdd:
    #     b = vdd.read(offset=3555771665356, length=10)
    #     print(b.hex())

    print(get_position(12345678))

    key = bytes.fromhex("e70e8593324aae130b86596fdb669114")
    s, t = derive_keypair(key)
    tweak_bytes = encrypted_tweak(12345678, s)
    print(tweak_bytes.hex())

    with VirtualHardDisk("theta.cs.dhbw-mannheim.de") as vdd:
        sector = read_sector(vdd, 24112, key)
        print(sector)
        print(sector.decode(encoding="utf-8"))  # fails, todo: fix this
