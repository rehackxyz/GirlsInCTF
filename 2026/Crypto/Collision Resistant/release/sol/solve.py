#!/usr/bin/env python3
"""Reference exploit for Collision Resistant Hash Function."""

from pwn import args, context, remote


BLOCK_SIZE = 32
STATE_BITS = 256
ROUNDS = 20

context.log_level = "info"
HOST = args.HOST or "127.0.0.1"
PORT = int(args.PORT or 1337)


def xor_bytes(*values: bytes) -> bytes:
    result = bytearray(values[0])
    for value in values[1:]:
        for index, byte in enumerate(value):
            result[index] ^= byte
    return bytes(result)


def sbox_layer(state: int) -> int:
    output = 0
    for shift in range(0, STATE_BITS, 8):
        byte = (state >> shift) & 0xFF
        output |= (((byte << 3) | (byte >> 5)) & 0xFF) << shift
    return output


def inverse_sbox_layer(state: int) -> int:
    output = 0
    for shift in range(0, STATE_BITS, 8):
        byte = (state >> shift) & 0xFF
        output |= (((byte >> 3) | (byte << 5)) & 0xFF) << shift
    return output


def permutation_layer(state: int) -> int:
    output = 0
    for source in range(STATE_BITS):
        if (state >> source) & 1:
            output |= 1 << ((13 * source + 7) % STATE_BITS)
    return output


def inverse_permutation_layer(state: int) -> int:
    output = 0
    for source in range(STATE_BITS):
        destination = (13 * source + 7) % STATE_BITS
        if (state >> destination) & 1:
            output |= 1 << source
    return output


def linear_transform(block: bytes) -> bytes:
    state = int.from_bytes(block, "big")
    for _ in range(ROUNDS):
        state = permutation_layer(sbox_layer(state))
    return state.to_bytes(BLOCK_SIZE, "big")


def inverse_linear_transform(block: bytes) -> bytes:
    state = int.from_bytes(block, "big")
    for _ in range(ROUNDS):
        state = inverse_sbox_layer(inverse_permutation_layer(state))
    return state.to_bytes(BLOCK_SIZE, "big")


def query_hash(io, message: bytes) -> bytes:
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"Message (hex): ", message.hex().encode())
    io.recvuntil(b"Hash: ")
    return bytes.fromhex(io.recvline().strip().decode())


io = remote(HOST, PORT)

# The empty message pads to one full 0x20 block. This exposes the combined
# final-input/output mask beta = L(K2) ^ mu.
padding_block = bytes([BLOCK_SIZE]) * BLOCK_SIZE
empty_hash = query_hash(io, b"")
beta = xor_bytes(empty_hash, linear_transform(padding_block))

# A 32-byte message creates two padded blocks. Its first state is E(0)=mu,
# allowing the second query to isolate the SPN's equivalent output mask.
zero_block_hash = query_hash(io, bytes(BLOCK_SIZE))
mu = inverse_linear_transform(
    xor_bytes(zero_block_hash, linear_transform(padding_block), beta)
)


def decrypt_block(block: bytes) -> bytes:
    return inverse_linear_transform(xor_bytes(block, mu))


# X and Y are valid one-byte-padded final blocks. Pick A so E(A)=X^Y.
# Then H(unpad(X)) = H(A || unpad(Y)), independently of the hidden K2.
x_block = b"A" * 31 + b"\x01"
y_block = b"B" * 31 + b"\x01"
first_cbc_block = decrypt_block(xor_bytes(x_block, y_block))

message_one = x_block[:-1]
message_two = first_cbc_block + y_block[:-1]
assert message_one != message_two

io.sendlineafter(b"> ", b"2")
io.sendlineafter(b"First message (hex): ", message_one.hex().encode())
io.sendlineafter(b"Second message (hex): ", message_two.hex().encode())
print(io.recvall().decode(), end="")
