import hashlib
import secrets
import signal

from Crypto.Cipher import AES


FLAG = "gctf26{fake_flag}"
KEY = secrets.token_bytes(16)
MAX_LENGTH = 1024


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def digest(ciphertext):
    length = len(ciphertext).to_bytes(16, "big")
    return hashlib.sha3_256(ciphertext + length).digest()[:16]


def make_tag(ciphertext, nonce):
    first_counter = AES.new(KEY, AES.MODE_ECB).encrypt(nonce + bytes(4))
    return xor(digest(ciphertext), first_counter)


def crypt(data, nonce):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=nonce, initial_value=1)
    return cipher.encrypt(data)


def encrypt(plaintext, nonce):
    ciphertext = crypt(plaintext, nonce)
    return ciphertext, make_tag(ciphertext, nonce)


def decrypt(ciphertext, tag, nonce):
    if not secrets.compare_digest(tag, make_tag(ciphertext, nonce)):
        raise ValueError("invalid tag")
    return crypt(ciphertext, nonce)


def read_hex(prompt, minimum, maximum):
    try:
        value = bytes.fromhex(input(prompt))
    except ValueError as error:
        raise ValueError("invalid hexadecimal") from error

    if not minimum <= len(value) <= maximum:
        if minimum == maximum:
            raise ValueError(f"input must be exactly {minimum} bytes")
        raise ValueError(f"input must be between {minimum} and {maximum} bytes")
    return value


def main():
    challenge_plaintext = secrets.token_bytes(32)
    challenge_nonce = secrets.token_bytes(12)
    challenge_ciphertext, challenge_tag = encrypt(
        challenge_plaintext, challenge_nonce
    )

    print("=== New AES mode ===")
    print("Recover the random challenge plaintext. All values are hexadecimal.\n")
    print(f"Challenge nonce: {challenge_nonce.hex()}")
    print(f"Challenge ciphertext: {challenge_ciphertext.hex()}")
    print(f"Challenge tag: {challenge_tag.hex()}")

    while True:
        print("\n1) Encrypt")
        print("2) Decrypt")
        print("3) Submit challenge plaintext")
        print("4) Quit")

        try:
            choice = input("> ")

            if choice == "1":
                plaintext = read_hex("Plaintext (hex): ", 1, MAX_LENGTH)
                nonce = secrets.token_bytes(12)
                ciphertext, tag = encrypt(plaintext, nonce)
                print(f"Nonce: {nonce.hex()}")
                print(f"Ciphertext: {ciphertext.hex()}")
                print(f"Tag: {tag.hex()}")

            elif choice == "2":
                nonce = read_hex("Nonce (hex): ", 12, 12)
                ciphertext = read_hex("Ciphertext (hex): ", 1, MAX_LENGTH)
                tag = read_hex("Tag (hex): ", 16, 16)

                plaintext = decrypt(ciphertext, tag, nonce)
                if nonce == challenge_nonce and ciphertext == challenge_ciphertext:
                    print("The challenge ciphertext cannot be decrypted directly.")
                else:
                    print(f"Plaintext: {plaintext.hex()}")

            elif choice == "3":
                answer = read_hex("Challenge plaintext (hex): ", 32, 32)
                if secrets.compare_digest(answer, challenge_plaintext):
                    print("Correct!")
                    print(f"Flag: {FLAG}")
                    return
                print("Incorrect plaintext.")

            elif choice == "4":
                return

            else:
                print("Invalid choice.")

        except ValueError as error:
            print(f"Error: {error}")


def timeout_handler(signum, frame):
    raise TimeoutError


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(180)
    try:
        main()
    except (EOFError, TimeoutError):
        pass
