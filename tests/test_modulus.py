import random
import pytest

from cpu.modulus import mod_multiply, mod_exp, fermat_inverse


P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF


@pytest.mark.parametrize("a,b,p", [
    (2, 3, 17),
    (4, 5, 17),
    (16, 16, 17),
    (0, 999, P),
    (P - 1, P - 1, P),
])
def test_modular_multiplication(a, b, p):
    assert mod_multiply(a, b, p) == (a * b) % p


@pytest.mark.parametrize("a,exp,p", [
    (2, 3, 17),
    (3, 4, 17),
    (5, 0, 17),
    (3, 13, 17),
    (P - 1, 2, P),
])
def test_modular_exponentiation(a, exp, p):
    assert mod_exp(a, exp, p) == pow(a, exp, p)


@pytest.mark.parametrize("a,p", [
    (1, 17),
    (2, 17),
    (3, 17),
    (4, 17),
    (5, 17),
    (P - 1, P),
])
def test_fermat_inverse(a, p):
    inv = fermat_inverse(a, p)

    assert inv == pow(a, -1, p)
    assert mod_multiply(a, inv, p) == 1


def test_fermat_inverse_zero_raises_error():
    with pytest.raises(ValueError):
        fermat_inverse(0, P)


def test_random_values_against_python():
    for _ in range(100):
        a = random.randint(1, P - 1)
        b = random.randint(0, P - 1)
        exp = random.randint(0, 2**32)

        assert mod_multiply(a, b, P) == (a * b) % P
        assert mod_exp(a, exp, P) == pow(a, exp, P)
        assert mod_multiply(a, fermat_inverse(a, P), P) == 1