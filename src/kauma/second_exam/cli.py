import sys

from kauma.second_exam.aes_bfk import AuthenticationError
from kauma.second_exam.disk import read_sector, write_sector
from kauma.second_exam.helper import VirtualHardDisk


def print_help_and_exit():
    print(f"usage: {sys.argv[0]} <read/write> <hostname> <key> <sector_number> [data]")
    sys.exit(1)


def main() -> None:
    if not len(sys.argv) in [5, 6]:
        print_help_and_exit()

    operation = sys.argv[1]
    hostname = sys.argv[2]
    key = bytes.fromhex(sys.argv[3])
    sector_number = int(sys.argv[4])

    if len(key) != 16:
        raise ValueError("invalid key length (should be 16 bytes)")

    match operation:
        case "read":
            if len(sys.argv) != 5:
                print_help_and_exit()

            with VirtualHardDisk(hostname) as vdd:
                try:
                    print(read_sector(vdd, sector_number, key).hex())
                except AuthenticationError:
                    print("ERR")
                    sys.exit(1)
        case "write":
            if len(sys.argv) != 6:
                print_help_and_exit()

            data = bytes.fromhex(sys.argv[5])

            if len(data) > 496:
                print("data must be 496 bytes or less")
                sys.exit(1)

            with VirtualHardDisk(hostname) as vdd:
                write_sector(vdd, sector_number, key, data)

            print(f"wrote {len(data)} bytes data at sector {sector_number}")
        case _:
            print_help_and_exit()
