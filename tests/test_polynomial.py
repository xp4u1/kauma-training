import pytest

from kauma.galois import galois_divide
from kauma.polynomial import Polynomial


def test_init_rejects_empty_coefficients():
    with pytest.raises(ValueError):
        Polynomial([])


def test_init_normalizes():
    assert Polynomial([3, 0, 0]).coefficients == [3]
    assert Polynomial([0, 0]).coefficients == [0]
    assert Polynomial([1, 0, 7]).coefficients == [1, 0, 7]


def test_make_normalized():
    p = Polynomial([1, 0, 0])
    p.make_normalized()
    assert p.coefficients == [1]

    p = Polynomial([0])
    p.make_normalized()
    assert p.coefficients == [0]


def test_make_monic():
    p = Polynomial([0b10, 0b10])
    p.make_monic()
    assert p.coefficients == [1, 1]

    p = Polynomial([1, 0b10, 0b100])
    p.make_monic()
    assert p.coefficients[-1] == 1
    assert p.coefficients[1] == galois_divide(0b10, 0b100)


def test_add():
    assert (Polynomial([1, 2]) + Polynomial([4, 0, 8])).coefficients == [5, 2, 8]
    assert (Polynomial([4, 0, 8]) + Polynomial([1, 2])).coefficients == [5, 2, 8]
    assert (Polynomial([3, 5]) + Polynomial([3, 5])).coefficients == [0]
    assert (Polynomial([1, 0, 7]) + Polynomial([0, 0, 7])).coefficients == [1]


def test_mul():
    assert (Polynomial([1, 1]) * Polynomial([1, 1])).coefficients == [1, 0, 1]
    assert (Polynomial([2, 1]) * Polynomial([2, 1])).coefficients == [4, 0, 1]
    assert (Polynomial([0b10]) * Polynomial([0b10])).coefficients == [0b100]
    assert (Polynomial([0]) * Polynomial([5, 3])).coefficients == [0]


def test_divmod():
    q, r = divmod(Polynomial([1, 0, 1]), Polynomial([1, 1]))
    assert q.coefficients == [1, 1]
    assert r.coefficients == [0]

    q, r = divmod(Polynomial([1, 0, 1]), Polynomial([0, 1]))
    assert q.coefficients == [0, 1]
    assert r.coefficients == [1]

    q, r = divmod(Polynomial([3]), Polynomial([0, 1]))
    assert q.coefficients == [0]
    assert r.coefficients == [3]

    # X^2 + X + 1 = (X + 1) * X + 1
    q, r = divmod(Polynomial([1, 1, 1]), Polynomial([1, 1]))
    assert q.coefficients == [0, 1]
    assert r.coefficients == [1]


def test_divmod_identity():
    a = Polynomial([5, 7, 0, 9])
    b = Polynomial([3, 1, 2])

    q, r = divmod(a, b)

    assert q * b + r == a
    assert r < b


def test_gcd():
    # (X + 1)(X + 2) and (X + 1)(X + 3), where 2 != 3 so X + 2 and X + 3 are coprime
    a = Polynomial([1, 1]) * Polynomial([2, 1])
    b = Polynomial([1, 1]) * Polynomial([3, 1])

    assert Polynomial.gcd(a, b) == Polynomial([1, 1])
    assert Polynomial.gcd(b, a) == Polynomial([1, 1])


def test_gcd_with_zero():
    assert Polynomial.gcd(Polynomial([0b10]), Polynomial([0])) == Polynomial([1])


def test_eq():
    assert Polynomial([1, 0]) == Polynomial([1])
    assert Polynomial([1]) != Polynomial([2])


def test_lt_by_degree():
    assert Polynomial([5]) < Polynomial([1, 1])
    assert not Polynomial([1, 1]) < Polynomial([5])


def test_lt_by_coefficients_from_highest_power():
    assert Polynomial([9, 0, 3]) < Polynomial([0, 0, 4])
    assert Polynomial([1, 2, 7]) < Polynomial([0, 3, 7])
    assert not Polynomial([1, 2, 7]) < Polynomial([1, 2, 7])


def test_ordering_via_total_ordering():
    assert Polynomial([0, 3, 7]) > Polynomial([1, 2, 7])
    assert Polynomial([1, 2, 7]) <= Polynomial([1, 2, 7])
    assert Polynomial([1, 2, 7]) >= Polynomial([1, 2, 7])


def test_sorted():
    polynomials = [
        Polynomial([0, 0, 1]),
        Polynomial([7]),
        Polynomial([0, 5, 1]),
        Polynomial([3, 0, 0, 0]),
        Polynomial([0, 4, 1, 0]),
    ]

    assert [p.coefficients for p in sorted(polynomials)] == [
        [3],
        [7],
        [0, 0, 1],
        [0, 4, 1],
        [0, 5, 1],
    ]


def test_pow_zero_exponent():
    assert Polynomial([2, 1]) ** 0 == Polynomial([1])
    assert Polynomial([0]) ** 0 == Polynomial([1])


def test_pow_one_exponent():
    assert Polynomial([2, 1, 5]) ** 1 == Polynomial([2, 1, 5])


def test_pow_negative_exponent_raises():
    with pytest.raises(ValueError):
        Polynomial([1, 1]) ** -1


def test_pow_zero_base():
    assert Polynomial([0]) ** 5 == Polynomial([0])


def test_pow_small_cases():
    # (X + 1)^2 = X^2 + 1, (X + 1)^3 = X^3 + X^2 + X + 1, (X + 1)^4 = X^4 + 1 in char 2
    assert Polynomial([1, 1]) ** 2 == Polynomial([1, 0, 1])
    assert Polynomial([1, 1]) ** 3 == Polynomial([1, 1, 1, 1])
    assert Polynomial([1, 1]) ** 4 == Polynomial([1, 0, 0, 0, 1])

    # (2)^3 = 8 in the field, since 2 * 4 = 8 has no reduction below degree 128
    assert Polynomial([0b10]) ** 3 == Polynomial([0b1000])


def test_pow_matches_repeated_multiplication():
    base = Polynomial([2, 1, 5])
    expected = Polynomial([1])

    for exponent in range(8):
        assert base**exponent == expected
        expected = expected * base


def test_differentiate():
    # d/dX (c0 + c1 X + c2 X^2 + c3 X^3) = c1 + c3 X^2 in characteristic 2
    assert Polynomial([5, 7, 9, 11]).differentiate() == Polynomial([7, 0, 11])
    assert Polynomial([1, 1]).differentiate() == Polynomial([1])
    assert Polynomial([1, 0, 1]).differentiate() == Polynomial([0])


def test_differentiate_constant():
    assert Polynomial([9]).differentiate() == Polynomial([0])


def test_differentiate_product_rule():
    # (f * g)' = f' * g + f * g'
    f = Polynomial([3, 1, 2])
    g = Polynomial([5, 0, 1, 4])

    assert (f * g).differentiate() == f.differentiate() * g + f * g.differentiate()


def test_powmod_small_cases():
    # modulo X^2 + 1, so X^2 == 1 and X^3 == X
    modulo = Polynomial([1, 0, 1])

    assert Polynomial([1, 1]).powmod(2, modulo) == Polynomial([0])
    assert Polynomial([0, 1]).powmod(2, modulo) == Polynomial([1])
    assert Polynomial([0, 1]).powmod(3, modulo) == Polynomial([0, 1])


def test_powmod_zero_exponent():
    assert Polynomial([5, 1]).powmod(0, Polynomial([1, 1])) == Polynomial([1])
    assert Polynomial([5, 1]).powmod(0, Polynomial([3])) == Polynomial([0])


def test_powmod_matches_pow_then_divmod():
    base = Polynomial([2, 1, 5])
    modulo = Polynomial([3, 1, 2])

    for exponent in range(8):
        _, expected = divmod(base**exponent, modulo)
        assert base.powmod(exponent, modulo) == expected


def test_powmod_negative_exponent_raises():
    with pytest.raises(ValueError):
        Polynomial([1, 1]).powmod(-1, Polynomial([1, 0, 1]))


def test_powmod_zero_modulo_raises():
    with pytest.raises(ValueError):
        Polynomial([1, 1]).powmod(2, Polynomial([0]))


def test_mul_adds_degrees():
    product = Polynomial([1, 2, 3]) * Polynomial([4, 0, 0, 5])

    assert len(product.coefficients) - 1 == 2 + 3


def test_mul_distributes_over_add_with_large_coefficients():
    f = Polynomial([1 << 127, 0x1234, 3])
    g = Polynomial([0xDEADBEEF, 1 << 100])
    h = Polynomial([7, 1 << 64, 1])

    assert f * (g + h) == f * g + f * h


def test_mul_by_zero_and_one():
    f = Polynomial([1 << 100, 5, 9])

    assert f * Polynomial([0]) == Polynomial([0])
    assert f * Polynomial([1]) == f


def test_divmod_smaller_dividend():
    q, r = divmod(Polynomial([3, 1]), Polynomial([1, 0, 1]))

    assert q == Polynomial([0])
    assert r == Polynomial([3, 1])


def test_make_monic_result_has_leading_one():
    p = Polynomial([5, 7, 1 << 90])
    p.make_monic()

    assert p.coefficients[-1] == 1


def test_make_monic_zero_polynomial_raises():
    with pytest.raises(ValueError):
        Polynomial([0]).make_monic()


def test_differentiate_zero():
    assert Polynomial([0]).differentiate() == Polynomial([0])


def test_gcd_of_scaled_inputs_is_monic_common_factor():
    # (X + c)(X + d) and 2 * (X + c)(X + e), with c, d, e distinct
    c = 1 << 100
    f = Polynomial([c, 1]) * Polynomial([5, 1])
    g = Polynomial([c, 1]) * Polynomial([7, 1]) * Polynomial([2])

    assert Polynomial.gcd(f, g) == Polynomial([c, 1])


def test_gcd_of_coprime_polynomials_is_one():
    f = Polynomial([1, 1])
    g = Polynomial([2, 1])

    assert Polynomial.gcd(f, g) == Polynomial([1])


def test_gcd_both_zero_raises():
    with pytest.raises(ValueError):
        Polynomial.gcd(Polynomial([0]), Polynomial([0]))


def test_equal_polynomials_sort_as_equal():
    a = Polynomial([1, 2, 0])
    b = Polynomial([1, 2])

    assert a == b
    assert not a < b
    assert not b < a


def test_sqrt_known_values():
    # sqrt(4) = 2 in the field, since 2 * 2 = 4
    assert Polynomial([4]).sqrt() == Polynomial([2])
    assert Polynomial([1]).sqrt() == Polynomial([1])
    assert Polynomial([0, 0, 1]).sqrt() == Polynomial([0, 1])
    assert Polynomial([0]).sqrt() == Polynomial([0])


def test_sqrt_inverts_square():
    r = Polynomial([3, 5, 1 << 90])

    assert (r * r).sqrt() == r


def test_sqrt_inverts_square_large_coefficients():
    r = Polynomial([0xDEADBEEF << 64, 1 << 127, 0x1234])

    assert (r * r).sqrt() == r


def test_sqrt_of_field_element_squared_back():
    a = 0x0123456789ABCDEF_FEDCBA9876543210
    root = Polynomial([a]).sqrt()

    assert (root * root) == Polynomial([a])


def test_sqrt_odd_coefficient_raises():
    with pytest.raises(ValueError):
        Polynomial([1, 1]).sqrt()

    with pytest.raises(ValueError):
        Polynomial([4, 0, 4, 2]).sqrt()


def test_degree():
    assert Polynomial([5]).degree() == 0
    assert Polynomial([1, 1]).degree() == 1
    assert Polynomial([1, 0, 7]).degree() == 2
    assert Polynomial([3, 0, 0]).degree() == 0
    assert Polynomial([0]).degree() == 0


def test_floordiv():
    # X^2 + X + 1 = (X + 1) * X + 1
    assert Polynomial([1, 1, 1]) // Polynomial([1, 1]) == Polynomial([0, 1])
    assert Polynomial([1, 0, 1]) // Polynomial([1, 1]) == Polynomial([1, 1])
    assert Polynomial([3]) // Polynomial([0, 1]) == Polynomial([0])


def test_floordiv_matches_divmod_quotient():
    a = Polynomial([5, 7, 0, 9])
    b = Polynomial([3, 1, 2])

    assert a // b == divmod(a, b)[0]
