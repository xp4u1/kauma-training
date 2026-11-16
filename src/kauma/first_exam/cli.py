import os
import sys


def main() -> None:
    if len(sys.argv) != 6:
        print(
            f"usage: {sys.argv[0]} <read/write> <hostname> <key> <offset> <length/data>"
        )
        sys.exit(1)

    operation = sys.argv[1]
    hostname = sys.argv[2]
    key = bytes.fromhex(sys.argv[3])

    match operation:
        case "read":
            offset = int(sys.argv[4])
            length = int(sys.argv[5])

            raise NotImplementedError()  # todo: arbitrary read
        case "write":
            raise NotImplementedError()
        case _:
            print("invalid mode. supported: read, write")
            sys.exit(1)


if __name__ == "__main__":
    main()
