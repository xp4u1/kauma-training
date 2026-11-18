from kauma.aes_gcm import _encrypt_block, encrypt
from kauma.gcm_crack import auth_key_candidates, forge_message

KEY = bytes.fromhex("1a9c1a8435c4bc2a65f302314cba27ac")
NONCE = bytes.fromhex("a8c72a26b9e7211f068a9262")
AUTH_KEY = _encrypt_block(bytes(16), KEY)


def test_forge_message():
    message_a = encrypt(b"lorem ipsum", KEY, NONCE, b"data")
    message_b = encrypt(b"dolor sit amet", KEY, NONCE, bytes())
    message_c = encrypt(b"consetetur sadipscing elitr", KEY, NONCE, bytes([1] * 16))

    original_message = encrypt(b"test123", KEY, NONCE, b"some additional data")
    forged_message = forge_message(
        (message_a, message_b, message_c),
        original_message.ciphertext,
        original_message.associated_data,
    )

    assert forged_message == original_message


def test_auth_key_candidates():
    message_a = encrypt(b"lorem ipsum", KEY, NONCE, b"data")
    message_b = encrypt(b"dolor sit amet", KEY, NONCE, bytes())

    candidates = auth_key_candidates(message_a, message_b)

    assert len(candidates) > 0
    assert AUTH_KEY in candidates
