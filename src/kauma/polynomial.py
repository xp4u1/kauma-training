from __future__ import annotations

from functools import total_ordering
from itertools import zip_longest

from kauma.galois import galois_add, galois_divide, galois_multiply, galois_power


@total_ordering
class Polynomial:
    """
    Polynomials with coeffiecients in F_(2^128)

    c_0 * X^0 + c_1 * X^1 + ... + 1 * X^n (monic)
    """

    coefficients: list[int]

    def __init__(self, coefficients: list[int]):
        if len(coefficients) == 0:
            raise ValueError("use [0] to represent 0")

        self.coefficients = coefficients
        self.make_normalized()

    def degree(self):
        return len(self.coefficients) - 1

    def make_monic(self) -> None:
        """
        Divide all coefficients by the leading coefficient.
        """

        n = len(self.coefficients) - 1
        leading_coefficient = self.coefficients[n]

        self.coefficients = [
            galois_divide(coefficient, leading_coefficient)
            for coefficient in self.coefficients
        ]

    def make_normalized(self) -> None:
        """
        Drop leading zeros, 0 is represented as [0].
        """

        n = len(self.coefficients)

        while n > 1 and self.coefficients[n - 1] == 0:
            n -= 1

        self.coefficients = self.coefficients[:n]

    def differentiate(self) -> Polynomial:
        """
        Formal derivative: i * c_i X^(i-1). In characteristic 2,
        i * c_i is c_i for odd i and 0 for even i.
        """

        coefficients = [c if i % 2 else 0 for i, c in enumerate(self.coefficients)][1:]
        return Polynomial(coefficients or [0])

    def sqrt(self) -> Polynomial:
        """
        Square root of a polynomial whose nonzero coefficients sit at even powers of X.
        In characteristic 2, (sum r_k X^k)^2 = sum r_k^2 X^(2k), so each root coefficient
        is the field square root a^(2^127) of the matching even coefficient.
        """

        if any(c != 0 for c in self.coefficients[1::2]):
            raise ValueError("not a square: odd-power coefficient is nonzero")

        return Polynomial([galois_power(c, 2**127) for c in self.coefficients[::2]])

    def __add__(self, other: Polynomial):
        coefficients = [
            galois_add(a, b)
            for a, b in zip_longest(self.coefficients, other.coefficients, fillvalue=0)
        ]
        result = Polynomial(coefficients)
        result.make_normalized()

        return result

    def __mul__(self, other: Polynomial):
        coefficients = [0] * (len(self.coefficients) + len(other.coefficients) - 1)

        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                coefficients[i + j] = galois_add(
                    coefficients[i + j], galois_multiply(a, b)
                )

        result = Polynomial(coefficients)
        result.make_normalized()

        return result

    def __pow__(self, exponent: int):
        if exponent < 0:
            raise ValueError("exponent has to be non-negative")

        result = Polynomial([1])
        base = self

        while exponent:
            if exponent & 1:
                result *= base

            base = base * base
            exponent >>= 1

        return result

    def powmod(self, exponent: int, modulo: Polynomial) -> Polynomial:
        if exponent < 0:
            raise ValueError("exponent has to be non-negative")

        _, base = divmod(self, modulo)
        _, result = divmod(Polynomial([1]), modulo)

        while exponent:
            if exponent & 1:
                _, result = divmod(result * base, modulo)

            _, base = divmod(base * base, modulo)
            exponent >>= 1

        return result

    def __divmod__(self, other: Polynomial):
        divisor = other.coefficients
        remainder = list(self.coefficients)
        quotient = [0] * max(len(remainder) - len(divisor) + 1, 1)
        leading = divisor[-1]

        for shift in range(len(remainder) - len(divisor), -1, -1):
            factor = galois_divide(remainder[shift + len(divisor) - 1], leading)
            quotient[shift] = factor
            for i, d in enumerate(divisor):
                remainder[shift + i] = galois_add(
                    remainder[shift + i], galois_multiply(factor, d)
                )

        quotient_polynomial = Polynomial(quotient)
        quotient_polynomial.make_normalized()
        remainder_polynomial = Polynomial(remainder[: len(divisor) - 1] or [0])
        remainder_polynomial.make_normalized()

        return quotient_polynomial, remainder_polynomial

    def __floordiv__(self, other: Polynomial):
        return divmod(self, other)[0]

    @classmethod
    def gcd(cls, a: Polynomial, b: Polynomial):
        zero = Polynomial([0])

        while b != zero:
            _, remainder = divmod(a, b)
            a, b = b, remainder

        result = Polynomial(list(a.coefficients))
        result.make_monic()

        return result

    def _sort_key(self):
        return (len(self.coefficients), tuple(reversed(self.coefficients)))

    def __eq__(self, other):
        return self._sort_key() == other._sort_key()

    def __lt__(self, other):
        return self._sort_key() < other._sort_key()
