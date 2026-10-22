from kauma.training_exam.client import Client

BLOCKSIZE = 16


def generate_block_combinations(position: int) -> list[bytes]:
    """
    Generate all combination for a byte in a block, e.g. 01, 02, 03, ..., ff

    Args:
        position: one-indexed, counted from the back of the block
    """

    return [
        int(i << (position - 1) * 8).to_bytes(length=BLOCKSIZE) for i in range(0, 256)
    ]


def xor(a: bytes, b: bytes) -> bytes:
    """
    XOR Operation on two bytes objects
    """

    return bytes(x ^ y for x, y in zip(a, b))


def calculate_block(
    client: Client, current_block: bytes, previous_block: bytes
) -> bytes:
    """
    Use a padding oracle client to decrypt a block without the key

    Args:
        client: padding oracle client
        current_block: block that should be decrypted
        previous_block: previous ciphertext block to calculate the plaintext
    """

    client.initialize_ciphertext(ciphertext=current_block)

    # reconstructed value of D(ciphertext)
    # before CBC's XOR in the last step
    inner_block = bytearray(BLOCKSIZE)

    for position in range(1, BLOCKSIZE + 1):
        test_block = inner_block.copy()
        for i in range(1, position):
            test_block[-i] ^= position

        blocks = [
            xor(
                block,
                bytes(test_block),
            )
            for block in generate_block_combinations(position)
        ]
        validation_dict = client.validate_q_blocks(
            q_blocks=blocks,
        )

        valid_blocks = [
            blocks[index] for index, valid in validation_dict.items() if valid
        ]
        if len(valid_blocks) != 1:
            raise RuntimeError(
                "invalid number of valid blocks found: ", len(valid_blocks)
            )

        inner_block[-position] = position ^ valid_blocks[0][-position]

    return xor(bytes(inner_block), previous_block)


def use_padding_oracle(client: Client, ciphertext: bytes) -> str:
    """
    Perform a padding oracle attack

    Args:
        client: TCP client to check paddings
        ciphertext: IV & ciphertext to decrypt

    Returns:
        plaintext as hex string
    """

    plaintext = []
    block_count = len(ciphertext) // BLOCKSIZE

    if block_count < 2:
        raise RuntimeError("invalid input, smallest input is iv + one ciphertext block")

    for i in range(1, block_count):
        previous_block = ciphertext[BLOCKSIZE * (i - 1) : BLOCKSIZE * i]
        current_block = ciphertext[BLOCKSIZE * i : BLOCKSIZE * (i + 1)]
        plaintext.append(calculate_block(client, current_block, previous_block))

    return b"".join(plaintext).hex()


if __name__ == "__main__":
    client = Client("serenity.cs.dhbw-mannheim.de", 14239)
    result = use_padding_oracle(
        client,
        bytes.fromhex(
            "38208ee33b121e12c0157761c1076574d5513d32695ecdd7753249867f3ac79473f5c8a076859b3353f4486513b29bc38a3da9dd94f02ab88de52036a09780007482752548809b63f22a728a5f47e7a65c47d73b757b1a77573689aad06bcfd1"
        ),
    )

    print(f"\n\nresult (hex): {result}\nresult (raw): {bytes.fromhex(result)}")
