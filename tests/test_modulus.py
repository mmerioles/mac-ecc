import pytest

from cpu.modulus import mod_multiply, mod_exp, fermat_inverse

@pytest.mark.parametrize("a,b,p,expected", [
    (2, 3, 17, 6),
    (4, 5, 17, 3),
    (16, 16, 17, 1)
])
def test_modular_multiplication(a, b, p, expected):
    assert mod_multiply(a, b, p) == expected


@pytest.mark.parametrize("a,b,p,expected", [
    (2, 3, 17, 8),
    (3, 4, 17, 13),
    (5, 0, 17, 1),
])
def test_modular_exponentiation(a, b, p, expected):
    assert mod_exp(a, b, p) == expected


@pytest.mark.parametrize("a,p,expected", [
    (1, 17, 1),
    (2, 17, 9),
    (3, 17, 6),
    (4, 17, 13),
    (5, 17, 7),
])
def test_modular_inverse(a, p, expected):
    assert fermat_inverse(a, p) == expected
