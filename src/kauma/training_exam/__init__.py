import sys

from kauma.training_exam.attack import use_padding_oracle
from kauma.training_exam.client import Client


def main() -> None:
    if len(sys.argv) != 4:
        print(f"usage: {sys.argv[0]} <host> <port> <iv+ciphertext>")
        sys.exit(1)

    client = Client(sys.argv[1], int(sys.argv[2]))
    ciphertext = bytes.fromhex(sys.argv[3])

    print(use_padding_oracle(client, ciphertext))
