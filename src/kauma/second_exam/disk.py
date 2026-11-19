from kauma.second_exam.bfk_aes import decrypt_sector, encrypt_sector
from kauma.second_exam.helper import VirtualHardDisk


def read_sector(disk: VirtualHardDisk, sector: int, key: bytes) -> bytes:
    raw_bytes = bytes(disk.read(offset=512 * sector, length=512))
    return decrypt_sector(sector, key, raw_bytes)


def write_sector(disk: VirtualHardDisk, sector: int, key: bytes, data: bytes) -> None:
    padded_data = data.rjust(496, b"\x00")
    encrypted_data = encrypt_sector(sector, key, padded_data)

    disk.write(offset=512 * sector, data=encrypted_data)
