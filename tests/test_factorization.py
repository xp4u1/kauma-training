import random

import pytest

from kauma.factorization import (
    distinct_degree_factorization,
    equal_degree_factorization,
    factorize,
    square_free_factorization,
)
from kauma.polynomial import Polynomial

# Irreducible over GF(2^128): X^2 + X + a
Q1 = Polynomial([0xE443DF789558867F5BA91FAF7A024204, 1, 1])
Q2 = Polynomial([0x23A7711A8133287637EBDCD9E87A1613, 1, 1])


def as_set(factors: list[tuple[Polynomial, int]]) -> set[tuple[tuple[int, ...], int]]:
    return {(tuple(p.coefficients), e) for p, e in factors}


def test_constant_has_no_factors():
    assert square_free_factorization(Polynomial([1])) == []


def test_square_free_polynomial():
    # (X + 1)(X + 2)
    f = Polynomial([1, 1]) * Polynomial([2, 1])

    assert as_set(square_free_factorization(f)) == {((2, 3, 1), 1)}


def test_repeated_factor():
    # (X + 1)^2 (X + 2)
    f = Polynomial([1, 1]) * Polynomial([1, 1]) * Polynomial([2, 1])

    assert as_set(square_free_factorization(f)) == {((1, 1), 2), ((2, 1), 1)}


def test_fourth_power():
    # (X + 1)^4
    f = Polynomial([1, 1]) ** 4

    assert as_set(square_free_factorization(f)) == {((1, 1), 4)}


def test_triple_factor():
    # (X + 1)^3 (X + 2)
    f = Polynomial([1, 1]) ** 3 * Polynomial([2, 1])

    assert as_set(square_free_factorization(f)) == {((1, 1), 3), ((2, 1), 1)}


def test_zero_polynomial_raises():
    with pytest.raises(ValueError):
        square_free_factorization(Polynomial([0]))


def test_ddf_constant_has_no_factors():
    assert distinct_degree_factorization(Polynomial([1])) == []


def test_ddf_linear_factors():
    # (X + 1)(X + 2)(X + 3) only has degree-1 irreducibles
    f = Polynomial([1, 1]) * Polynomial([2, 1]) * Polynomial([3, 1])

    assert as_set(distinct_degree_factorization(f)) == {(tuple(f.coefficients), 1)}


def test_ddf_single_irreducible_quadratic():
    assert as_set(distinct_degree_factorization(Q1)) == {(tuple(Q1.coefficients), 2)}


def test_ddf_two_irreducible_quadratics_are_grouped():
    f = Q1 * Q2

    assert as_set(distinct_degree_factorization(f)) == {(tuple(f.coefficients), 2)}


def test_ddf_mixed_degrees():
    # (X + 1) * Q1
    f = Polynomial([1, 1]) * Q1

    assert as_set(distinct_degree_factorization(f)) == {
        ((1, 1), 1),
        (tuple(Q1.coefficients), 2),
    }


def test_ddf_input_is_not_mutated():
    f = Polynomial([2, 2])
    before = list(f.coefficients)

    distinct_degree_factorization(f)

    assert f.coefficients == before


def test_ddf_zero_polynomial_raises():
    with pytest.raises(ValueError):
        distinct_degree_factorization(Polynomial([0]))


def test_edf_single_factor_returns_input():
    result = equal_degree_factorization(Q1, 2)

    assert [tuple(p.coefficients) for p in result] == [tuple(Q1.coefficients)]


def test_edf_two_quadratics():
    random.seed(0)

    result = equal_degree_factorization(Q1 * Q2, 2)

    assert {tuple(p.coefficients) for p in result} == {
        tuple(Q1.coefficients),
        tuple(Q2.coefficients),
    }


def test_edf_linear_factors():
    random.seed(0)
    f = Polynomial([1, 1]) * Polynomial([2, 1]) * Polynomial([3, 1])

    result = equal_degree_factorization(f, 1)

    assert {tuple(p.coefficients) for p in result} == {(1, 1), (2, 1), (3, 1)}


def test_edf_zero_polynomial_raises():
    with pytest.raises(ValueError):
        equal_degree_factorization(Polynomial([0]), 1)


def test_factorize_constant_has_no_factors():
    assert factorize(Polynomial([1])) == []


def test_factorize_repeated_factor():
    # (X + 1)^2 (X + 2)
    f = Polynomial([1, 1]) * Polynomial([1, 1]) * Polynomial([2, 1])

    result = factorize(f)

    assert sorted(tuple(p.coefficients) for p in result) == [(1, 1), (1, 1), (2, 1)]


def test_factorize_triple_factor():
    # (X + 1)^3
    result = factorize(Polynomial([1, 1]) ** 3)

    assert [tuple(p.coefficients) for p in result] == [(1, 1), (1, 1), (1, 1)]


def test_factorize_irreducible_quadratics():
    random.seed(0)

    result = factorize(Q1 * Q2)

    assert sorted(tuple(p.coefficients) for p in result) == sorted(
        [tuple(Q1.coefficients), tuple(Q2.coefficients)]
    )


def test_factorize_repeated_irreducible_quadratic():
    # (X + 1) * Q1^2
    random.seed(0)
    f = Polynomial([1, 1]) * Q1 * Q1

    result = factorize(f)

    assert sorted(tuple(p.coefficients) for p in result) == sorted(
        [(1, 1), tuple(Q1.coefficients), tuple(Q1.coefficients)]
    )
