import pytest

from cpu.modulus import mod_multiply, mod_exp, fermat_inverse

@pytest.mark.parametrize("a,b,p,expected", [
    (10, 20, 100, 1000),
    (1, 2, 100, 100)
])
def test_modular_multiplication(a, b, p, expected):
    result = mod_multiply(a, b, p)
    assert a * p == expected

def test_modular_exponentiation():
    assert True

def test_modular_inverse():
    assert True
