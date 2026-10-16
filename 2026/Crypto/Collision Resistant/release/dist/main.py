#!/usr/bin/env python3

import binascii
import os
import secrets
import signal


FLAG = "gctf26{fake_flag}"
BLOCK_SIZE = 32
STATE_BITS = 256
ROUNDS = 20
MAX_MESSAGE_SIZE = 4096


def xor(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def sbox(state):
    output = 0
    for shift in range(0, STATE_BITS, 8):
        byte = (state >> shift) & 0xFF
        output |= (((byte << 3) | (byte >> 5)) & 0xFF) << shift
    return output


def permute(state):
    output = 0
    for source in range(STATE_BITS):
        if (state >> source) & 1:
            output |= 1 << ((13 * source + 7) % STATE_BITS)
    return output


def linear_transform(block):
    state = int.from_bytes(block, "big")
    for _ in range(ROUNDS):
        state = permute(sbox(state))
    return state.to_bytes(BLOCK_SIZE, "big")


def encrypt_block(block, key):
    state = int.from_bytes(block, "big")
    round_key = int.from_bytes(key, "big")
    for _ in range(ROUNDS):
        state = permute(sbox(state ^ round_key))
    return state.to_bytes(BLOCK_SIZE, "big")


def pad(message):
    length = BLOCK_SIZE - len(message) % BLOCK_SIZE
    return message + bytes([length]) * length


def hash_message(message, master_key):
    key = master_key[:BLOCK_SIZE]
    final_key = master_key[BLOCK_SIZE:]
    padded = pad(message)
    state = bytes(BLOCK_SIZE)

    for offset in range(0, len(padded), BLOCK_SIZE):
        block = padded[offset : offset + BLOCK_SIZE]
        value = xor(state, block)
        if offset + BLOCK_SIZE == len(padded):
            value = xor(value, final_key)
        state = encrypt_block(value, key)
    return state


def read_message(prompt):
    text = input(prompt).strip().encode()
    if len(text) > 2 * MAX_MESSAGE_SIZE:
        raise ValueError("message is too long")
    if len(text) % 2:
        raise ValueError("hex input must have an even length")
    try:
        return binascii.unhexlify(text)
    except binascii.Error as error:
        raise ValueError("message is not valid hexadecimal") from error


def main():
    signal.alarm(180)
    master_key = os.urandom(2 * BLOCK_SIZE)

    print("=== Collision Resistant Hash Function ===")
    print("Find two distinct messages with the same hash.")

    while True:
        print("\n1) Hash a message")
        print("2) Submit a collision")
        print("3) Quit")

        try:
            choice = input("> ").strip()
        except EOFError:
            return

        if choice == "1":
            try:
                message = read_message("Message (hex): ")
                print(f"Hash: {hash_message(message, master_key).hex()}")
            except ValueError as error:
                print(f"Invalid input: {error}")

        elif choice == "2":
            try:
                first = read_message("First message (hex): ")
                second = read_message("Second message (hex): ")
            except ValueError as error:
                print(f"Invalid input: {error}")
                return

            if first == second:
                print("The messages must be distinct.")
            elif secrets.compare_digest(
                hash_message(first, master_key), hash_message(second, master_key)
            ):
                print(f"Flag: {FLAG}")
            else:
                print("The messages do not collide.")
            return

        elif choice == "3":
            return

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
