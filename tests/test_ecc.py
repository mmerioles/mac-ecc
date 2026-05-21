import pytest

from cpu.ecc import (
    P,
    A_COEF,
    B_COEF,
    G,
    N,
    POINT_AT_INFINITY,
    point_add,
    point_double,
    scalar_multiply,
)


def is_on_curve(point):
    if point is POINT_AT_INFINITY:
        return True

    x, y = point
    left = (y * y) % P
    right = (x**3 + A_COEF * x + B_COEF) % P

    return left == right


def test_generator_is_on_curve():
    assert is_on_curve(G)


def test_zero_times_g_is_infinity():
    assert scalar_multiply(0, G) is POINT_AT_INFINITY


def test_one_times_g_is_g():
    assert scalar_multiply(1, G) == G


def test_two_times_g_matches_point_double():
    assert scalar_multiply(2, G) == point_double(G)


def test_two_times_g_matches_point_add():
    assert scalar_multiply(2, G) == point_add(G, G)


def test_n_times_g_is_infinity():
    assert scalar_multiply(N, G) is POINT_AT_INFINITY


def test_n_plus_one_times_g_is_g():
    assert scalar_multiply(N + 1, G) == G


@pytest.mark.parametrize("k", [1, 2, 3, 5, 10, 20])
def test_scalar_multiply_result_is_on_curve(k):
    point = scalar_multiply(k, G)

    assert is_on_curve(point)


def test_point_add_commutative():
    p1 = scalar_multiply(3, G)
    p2 = scalar_multiply(7, G)

    assert point_add(p1, p2) == point_add(p2, p1)


@pytest.mark.parametrize("k1,k2", [
    (2, 3),
    (5, 7),
    (10, 20),
])
def test_scalar_addition_property(k1, k2):
    p1 = scalar_multiply(k1, G)
    p2 = scalar_multiply(k2, G)

    left = point_add(p1, p2)
    right = scalar_multiply(k1 + k2, G)

    assert left == right