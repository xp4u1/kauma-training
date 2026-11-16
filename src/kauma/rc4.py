class RC4:
    def __init__(self, key: bytes):
        self.i, self.j = 0, 0
        self.sbox = list(range(256))

        self.initialize_cipher(key)

    def next_keystream_byte(self) -> int:
        """
        Generate the next keystream byte from the current state.
        """

        self.i = (self.i + 1) % 256
        self.j = (self.j + self.sbox[self.i]) % 256
        self.sbox[self.i], self.sbox[self.j] = (
            self.sbox[self.j],
            self.sbox[self.i],
        )

        return self.sbox[(self.sbox[self.i] + self.sbox[self.j]) % 256]

    def next_keystream(self, length: int) -> bytes:
        """
        Generate n bytes of the keystream from the current state.

        Args:
            length: length of the keystream in bytes
        """

        return bytes([self.next_keystream_byte() for _ in range(length)])

    def initialize_cipher(self, key: bytes):
        """
        Generate the full sbox and set start values for i and j to
        generate keystream bytes.
        """

        self._generate_partial_sbox(key, 256)
        self.i, self.j = 0, 0

    def _generate_partial_sbox(self, key: bytes, stop_after: int):
        """
        Generate (a part of) the sbox. Overrides any existing sbox.
        """

        self.i, self.j = 0, 0
        self.sbox = list(range(256))

        for self.i in range(stop_after):
            self.j = (self.j + self.sbox[self.i] + key[self.i % len(key)]) % 256
            self.sbox[self.i], self.sbox[self.j] = (
                self.sbox[self.j],
                self.sbox[self.i],
            )
