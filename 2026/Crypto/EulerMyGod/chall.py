#!/usr/bin/env python3
import os
from math import prod

from Crypto.Util.number import GCD, bytes_to_long, getPrime, getRandomNBitInteger, inverse


SHAPES = [
    (452, 508, 576),
    (460, 524, 552),
    (468, 492, 576),
    (476, 500, 560),
    (484, 516, 536),
]
D_BITS = 387


def generate():
    moduli = []
    phis = []

    for shape in SHAPES:
        primes = [getPrime(bits) for bits in shape]
        moduli.append(prod(primes))
        phis.append(prod(p - 1 for p in primes))

    while True:
        d = getRandomNBitInteger(D_BITS) | 1
        if all(GCD(d, phi) == 1 for phi in phis):
            break

    exponents = [inverse(d, phi) for phi in phis]
    return list(zip(moduli, exponents))


flag = os.environ["FLAG"].encode()
pub = generate()

m = bytes_to_long(flag)
assert m < pub[0][0]
c = pow(m, pub[0][1], pub[0][0])

print(f"pub = {pub}")
print(f"c = {c}")
