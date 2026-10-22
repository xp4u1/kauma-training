import socket


class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None

    def initialize_ciphertext(self, ciphertext: bytes) -> None:
        if self.socket is not None:
            self.close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.sendall(ciphertext)

    def validate_q_blocks(self, q_blocks: list[bytes]) -> dict:
        if self.socket is None:
            raise RuntimeError("client not connected")

        self.socket.sendall(int(len(q_blocks)).to_bytes(length=2, byteorder="little"))

        for block in q_blocks:
            self.socket.sendall(block)

        answer_bytes = self.socket.recv(len(q_blocks))

        return {i: answer == 1 for i, answer in enumerate(answer_bytes)}

    def close(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None
