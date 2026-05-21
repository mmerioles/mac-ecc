from cpu.modulus import mod_multiply, mod_exp, fermat_inverse


P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

A = 123456789123456789123456789
B = 987654321987654321987654321
EXP = 2**256 - 1


def test_benchmark_mod_multiply(benchmark):
    result = benchmark(mod_multiply, A, B, P)

    assert result == (A * B) % P


def test_benchmark_mod_exp(benchmark):
    result = benchmark(mod_exp, A, EXP, P)

    assert result == pow(A, EXP, P)


def test_benchmark_fermat_inverse(benchmark):
    result = benchmark(fermat_inverse, A, P)

    assert (A * result) % P == 1