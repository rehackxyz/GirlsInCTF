#!/usr/bin/env python3

import hashlib

from pwn import args, remote


HOST = args.HOST or "127.0.0.1"
PORT = int(args.PORT or 1337)


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def digest(ciphertext):
    length = len(ciphertext).to_bytes(16, "big")
    return hashlib.sha3_256(ciphertext + length).digest()[:16]


io = remote(HOST, PORT)
io.recvuntil(b"Challenge nonce: ")
nonce = bytes.fromhex(io.recvline().strip().decode())
io.recvuntil(b"Challenge ciphertext: ")
ciphertext = bytes.fromhex(io.recvline().strip().decode())
io.recvuntil(b"Challenge tag: ")
tag = bytes.fromhex(io.recvline().strip().decode())

tag_mask = xor(tag, digest(ciphertext))

forged_ciphertext = bytearray(ciphertext)
forged_ciphertext[0] ^= 1
forged_ciphertext = bytes(forged_ciphertext)
forged_tag = xor(tag_mask, digest(forged_ciphertext))

io.sendlineafter(b"> ", b"2")
io.sendlineafter(b"Nonce (hex): ", nonce.hex().encode())
io.sendlineafter(b"Ciphertext (hex): ", forged_ciphertext.hex().encode())
io.sendlineafter(b"Tag (hex): ", forged_tag.hex().encode())
io.recvuntil(b"Plaintext: ")
plaintext = bytearray.fromhex(io.recvline().strip().decode())
plaintext[0] ^= 1

io.sendlineafter(b"> ", b"3")
io.sendlineafter(b"Challenge plaintext (hex): ", bytes(plaintext).hex().encode())
print(io.recvall().decode(), end="")
