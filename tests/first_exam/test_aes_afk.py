from kauma.first_exam.aes_afk import derive_keypair, generate_block_polynomials


def test_p_map_length():
    p_map = generate_block_polynomials()
    assert len(p_map) == 32


def test_derive_keypair():
    key = bytes.fromhex("7385243f5fe7c26689488ff904e701c7")
    assert derive_keypair(key) == (
        bytes.fromhex("48bb0b1889cd4c24e4dde1d6dac62634"),
        bytes.fromhex("b463b0ca528e71c878a3e99ac7af5987"),
    )


# def test_decrypt(): # fails
#     key = bytes.fromhex("7385243f5fe7c26689488ff904e701c7")
#     plaintext = decrypt(
#         bytes.fromhex(
#             "aac57ed4c86560f6812919c497d53ff5beab576297ba713c5cf3d18c4ad566bc5338f063063b9c1ff1d51f170c82385a0fe09056821ed89ad8da8d4c8b9f33a77a3cf0d361703fe841497afcc0bd68404477e101fc5ec394c06827a9186295dfe0608e24d5d62fe1b7c4326e5404997a205d6fe8b19f360f25ae9a6a5967e3312998e15a3f7edf79695589eba2e1362d73bb71c55d9495728a58f7f9a52ea61b85ff948cce9418f8c6b1774f9c79ea67daff9ddb4890ac09faeb19a3699aaa745c8b9f0b22000daaf77a52b0046a5219e688c404211ab4799859bbb501e623cc81ae151799ec05d530c88d040e72454b94a10bafff7a6c495bbcb311024a3caf91259cdd7eec15c6c414b545dfdbb2fa4904b4a5144631d3c57c353d61f977692c1871fca9bd1ccf3365d57b9c224666f8d5d007e0ab1d6de95c7198e36aba5e2c4d834bc8b97f04aba5422480e51f40ca58f3521f2f5baf422e6a719f1c093e057153e08b2ac1b66c301d20115cd0c9af333aef27d8aa5074f9b7a913f869e5169716133bebfd71f8d34aa29083e0713759ecb3f6f2f27fcf1feb19b3a3182ec94f0b14f6f48038717be1f79856a94d1e4f2ea23741188133d9b8c4143fc2acfdff1a4d07192dffbfdf60228d9d83009cb580763ab889595b5ab1f7fcbd2554e36950a879e35c6c15487017410088a444448146aa90bbc44a60678ce00a3b77",
#         ),
#         key,
#         0,
#     )
#     assert plaintext == bytes(512)
