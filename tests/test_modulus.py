import pytest

from cpu.modulus import mod_multiply, mod_exp, fermat_inverse

@pytest.fixture
def prime():
    return 17 #change this later to a large prime

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 6),
    (4, 5, 3),
    (16, 16, 1)
])
def test_modular_multiplication(a, b, expected, prime):
    assert mod_multiply(a, b, prime) == expected


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 8),
    (3, 4, 13),
    (5, 0, 1),
])
def test_modular_exponentiation(a, b, expected, prime):
    assert mod_exp(a, b, prime) == expected


@pytest.mark.parametrize("a,expected", [
    (1, 1),
    (2, 9),
    (3, 6),
    (4, 13),
    (5, 7),
])
def test_modular_inverse(a, expected, prime):
    assert fermat_inverse(a, prime) == expected
