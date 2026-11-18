import random

from kauma.polynomial import Polynomial

ONE = Polynomial([1])
X = Polynomial([0, 1])
Q = 1 << 128  # number of elements in F_(2^128)


def factorize(polynomial: Polynomial) -> list[Polynomial]:
    factors = []

    for square_free_polynomial, multiplicity in square_free_factorization(polynomial):
        for distinct_degree_polynomial, degree in distinct_degree_factorization(
            square_free_polynomial
        ):
            for equal_degree_polynomial in equal_degree_factorization(
                distinct_degree_polynomial, degree
            ):
                factors.extend([equal_degree_polynomial] * multiplicity)

    return factors


def square_free_factorization(polynomial: Polynomial) -> list[tuple[Polynomial, int]]:
    """
    https://dhbw.johannes-bauer.com/lectures/2026_10_kauma/week04 (slide 25)
    """

    f = Polynomial(list(polynomial.coefficients))
    f.make_monic()

    c = Polynomial.gcd(f, f.differentiate())
    f = f // c
    results = []
    exponent = 1

    while f != ONE:
        y = Polynomial.gcd(f, c)
        if f != y:
            results.append((f // y, exponent))

        f = y
        c = c // y
        exponent += 1

    if c != ONE:
        for fstar, estar in square_free_factorization(c.sqrt()):
            results.append((fstar, estar * 2))

    return results


def distinct_degree_factorization(
    polynomial: Polynomial,
) -> list[tuple[Polynomial, int]]:
    """
    https://dhbw.johannes-bauer.com/lectures/2026_10_kauma/week04 (slide 40)
    """

    fstar = Polynomial(list(polynomial.coefficients))
    fstar.make_monic()
    results = []

    d = 1
    while fstar.degree() >= 2 * d:
        h = X.powmod(Q**d, fstar) + X  # X^(q^d) - X
        g = Polynomial.gcd(h, fstar)
        if g != ONE:
            results.append((g, d))
            fstar = fstar // g
        d += 1

    if fstar != ONE:
        results.append((fstar, fstar.degree()))

    return results


def _random_polynomial(max_degree: int) -> Polynomial:
    return Polynomial([random.getrandbits(128) for _ in range(max_degree)])


def equal_degree_factorization(polynomial: Polynomial, degree: int) -> list[Polynomial]:
    """
    Cantor-Zassenhaus:
    https://dhbw.johannes-bauer.com/lectures/2026_10_kauma/week04 (slide 47)
    """

    f = Polynomial(list(polynomial.coefficients))
    f.make_monic()

    n = f.degree() // degree
    results = [f]

    while len(results) < n:
        h = _random_polynomial(f.degree())
        g = h.powmod((Q**degree - 1) // 3, f) + ONE

        next_results = []
        for u in results:
            j = Polynomial.gcd(u, g) if u.degree() > degree else ONE
            if j != ONE and j != u:
                next_results += [j, u // j]
            else:
                next_results.append(u)
        results = next_results

    return results
