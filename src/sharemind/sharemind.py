from __future__ import annotations
import random
import math
from typing import Iterable, Optional

DEFAULT_SIZE = 32


class SharemindSecret:
    def __init__(self, value: Optional[int] = None, shares: Optional[Iterable] = None, size: int = DEFAULT_SIZE):
        self.size = size
        self.mod = 2 ** size

        if value is not None:
            assert 0 <= value < self.mod, 'Number provided is out of bounds'
            self.shares = self.generate_shares(value, size)
        elif shares is not None:
            shares = tuple(shares)
            assert all(0 <= v < self.mod for v in shares), 'Not all shares provided are within the necessary bounds'
            assert len(shares) == 3, 'Exactly 3 shares must be provided'
            self.shares = shares
        else:
            raise ValueError('Either shares or a numeric value must be provided')

    def __repr__(self):
        return f'{self.numeric_value}'

    @property
    def numeric_value(self):
        return sum(self.shares) % self.mod

    @staticmethod
    def generate_shares(value: int, size: int = DEFAULT_SIZE) -> tuple[int, int, int]:
        mod = 2 ** size
        a, b = (random.randint(0, mod - 1) for _ in range(2))
        c = (value - a - b) % mod
        return a, b, c

    def re_share(self):
        u1, u2, u3 = self.shares

        r1, r2, r3 = (random.randint(0, self.mod - 1) for _ in range(3))

        w1 = (u1 + r3 - r1) % self.mod
        w2 = (u2 + r1 - r2) % self.mod
        w3 = (u3 + r2 - r3) % self.mod

        self.shares = (w1, w2, w3)

    @classmethod
    def from_binary_shares(cls, shares: Iterable, size: int = DEFAULT_SIZE) -> SharemindSecret:
        u = SharemindSecret(shares=shares, size=size)
        mod = 2 ** size

        # Round 1
        r12, r13, s12, s13 = (random.randint(0, mod - 1) for _ in range(4))
        s1 = r12 * r13 - s12 - s13
        r23, r21, s23, s21 = (random.randint(0, mod - 1) for _ in range(4))
        s2 = r23 * r21 - s23 - s21
        r31, r32, s31, s32 = (random.randint(0, mod - 1) for _ in range(4))
        s3 = r31 * r32 - s31 - s32

        # Round 2
        u1, u2, u3 = u.shares
        b12 = r31 + u1
        b13 = r21 + u1
        b23 = r12 + u2
        b21 = r32 + u2
        b31 = r23 + u3
        b32 = r13 + u3

        c = SharemindSecret(value=u3, size=size)

        # Round 3
        ab1 = s31 - r31 * b21
        ab2 = b12 * b21 + s32 - b12 * r32
        ab3 = s3
        ab = SharemindSecret(shares=(ab1 % mod, ab2 % mod, ab3 % mod), size=size)

        ac1 = b31 * b13 + s21 - b31 * r21
        ac2 = s2
        ac3 = s23 - r23 * b13
        ac = SharemindSecret(shares=(ac1 % mod, ac2 % mod, ac3 % mod), size=size)

        bc1 = s1
        bc2 = s12 - r12 * b32
        bc3 = b23 * b32 + s13 - b23 * r13
        bc = SharemindSecret(shares=(bc1 % mod, bc2 % mod, bc3 % mod), size=size)

        abc = ab * c

        # Round 4
        w = u - ab * 2 - ac * 2 - bc * 2 + abc * 4
        w.re_share()
        return w

    @classmethod
    def generate_random_number_and_bits(cls, size: int = DEFAULT_SIZE) -> tuple[SharemindSecret, list[SharemindSecret]]:
        # Round 1
        r_bits = [cls.from_binary_shares(shares=(random.randint(0, 1) for _ in range(3)), size=size)
                  for _ in range(size)]

        # Round 2
        r = SharemindSecret(value=0, size=size)
        for i, bit in enumerate(r_bits):
            r += bit * (2 ** i)

        return r, r_bits

    @staticmethod
    def bitwise_addition(u_bits: list[SharemindSecret], v_bits: list[SharemindSecret]) -> list[SharemindSecret]:
        """
        This is the bitwise addition in the carry look-ahead method that's described in the origin article.
        It's a bit more complex than the naive carry calculation, but should be better for parallelization.
        """
        size = u_bits[0].size
        assert len(u_bits) == len(v_bits) == size, 'Vector lengths do not match each other or share size'
        assert all(u.size == size and v.size == size for u, v in zip(u_bits, v_bits)), \
            'Not all values have the same size'

        # Round 1
        s_flags = [u * v for u, v in zip(u_bits, v_bits)]
        p_flags = [u + v - s * 2 for u, v, s in zip(u_bits, v_bits, s_flags)]
        # In the original paper it's written twice in contradictory ways, but THIS is the correct base case.

        # Round 2 ... log_2(n) + 1
        for k in range(0, int(math.log(size, 2))):
            for l in range(0, 2**k):
                for m in range(0, size // (2**(k+1))):  # In the paper there's a typo, the "k+1" brackets are missing.
                    i1 = 2**k + l + 2**(k+1) * m
                    i2 = 2**k + 2**(k+1) * m - 1
                    s_flags[i1] = s_flags[i1] + p_flags[i1] * s_flags[i2]
                    p_flags[i1] = p_flags[i1] * p_flags[i2]

        w_bits = ([u_bits[0] + v_bits[0] - s_flags[0] * 2] +
                  [u_bits[i] + v_bits[i] + s_flags[i-1] - s_flags[i] * 2 for i in range(1, size)])

        return w_bits

    def extract_bits(self) -> list[SharemindSecret]:
        # Round 1 & 2
        r, r_bits = self.generate_random_number_and_bits(size=self.size)

        a = self - r

        # Round 2
        a_raw_value = a.numeric_value
        a_raw_bits = [a_raw_value // (2 ** i) % 2 for i in range(self.size)]

        a_bits = [self.from_binary_shares(shares=(raw_bit, 0, 0), size=self.size) for raw_bit in a_raw_bits]

        d_bits = self.bitwise_addition(a_bits, r_bits)
        return d_bits

    def __add__(self, other: SharemindSecret) -> SharemindSecret:
        assert self.size == other.size, 'Cannot perform addition with different sizes'
        w = SharemindSecret(shares=((u + v) % self.mod for u, v in zip(self.shares, other.shares)), size=self.size)
        w.re_share()
        return w

    def __sub__(self, other: SharemindSecret) -> SharemindSecret:
        assert self.size == other.size, 'Cannot perform subtraction with different sizes'
        w = SharemindSecret(shares=((u - v) % self.mod for u, v in zip(self.shares, other.shares)), size=self.size)
        w.re_share()
        return w

    def __mul__(self, other: int | SharemindSecret) -> SharemindSecret:
        if isinstance(other, int):
            w = SharemindSecret(shares=((u * other) % self.mod for u in self.shares), size=self.size)
            w.re_share()
            return w

        assert self.size == other.size, 'Cannot perform multiplication with different sizes'

        u1, u2, u3 = self.shares
        v1, v2, v3 = other.shares

        # Round 1
        r12, r13, s12, s13 = (random.randint(0, self.mod - 1) for _ in range(4))
        r23, r21, s23, s21 = (random.randint(0, self.mod - 1) for _ in range(4))
        r31, r32, s31, s32 = (random.randint(0, self.mod - 1) for _ in range(4))

        # Round 2
        a12 = u1 + r31
        b12 = v1 + s31
        a13 = u1 + r21
        b13 = v1 + s21
        a23 = u2 + r12
        b23 = v2 + s12
        a21 = u2 + r32
        b21 = v2 + s32
        a31 = u3 + r23
        b31 = v3 + s23
        a32 = u3 + r13
        b32 = v3 + s13

        # Round 3
        c1 = u1 * b21 + u1 * b31 + v1 * a21 + v1 * a31 - a12 * b21 - b12 * a21 + r12 * s13 + s12 * r13
        w1 = (c1 + u1 * v1) % self.mod
        c2 = u2 * b32 + u2 * b12 + v2 * a32 + v2 * a12 - a23 * b32 - b23 * a32 + r23 * s21 + s23 * r21
        w2 = (c2 + u2 * v2) % self.mod
        c3 = u3 * b13 + u3 * b23 + v3 * a13 + v3 * a23 - a31 * b13 - b31 * a13 + r31 * s32 + s31 * r32
        w3 = (c3 + u3 * v3) % self.mod

        w = SharemindSecret(shares=(w1, w2, w3), size=self.size)
        w.re_share()
        return w

    def __ge__(self, other: SharemindSecret) -> SharemindSecret:
        assert self.size == other.size, 'Cannot perform greater-than-equals comparison between different sizes'

        d = self - other
        d_bits = d.extract_bits()

        w = SharemindSecret(value=1, size=self.size) - d_bits[-1]
        return w

    def __bool__(self) -> bool:
        return bool(self.numeric_value)
