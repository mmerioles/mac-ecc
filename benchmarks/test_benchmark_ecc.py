from cpu.constants import G, N, POINT_AT_INFINITY
from cpu.ecc import (
    point_add,
    point_double,
    scalar_multiply,
    is_on_curve,
    ecdh_shared_secret,
)


K1 = 123456789123456789
K2 = 987654321987654321


def test_benchmark_point_add(benchmark):
    p1 = scalar_multiply(K1, G)
    p2 = scalar_multiply(K2, G)
    result = benchmark(point_add, p1, p2)
    assert is_on_curve(result)


def test_benchmark_point_double(benchmark):
    p1 = scalar_multiply(K1, G)
    result = benchmark(point_double, p1)
    assert is_on_curve(result)


def test_benchmark_scalar_multiply_small_key(benchmark):
    result = benchmark(scalar_multiply, K1, G)
    assert is_on_curve(result)


def test_benchmark_scalar_multiply_256_bit_key(benchmark):
    key = N - 1
    result = benchmark(scalar_multiply, key, G)
    assert is_on_curve(result)


def test_benchmark_ecdh_shared_secret(benchmark):
    alice_private = K1
    bob_private = K2
    bob_public = scalar_multiply(bob_private, G)
    result = benchmark(ecdh_shared_secret, alice_private, bob_public)
    assert is_on_curve(result)
    assert result is not POINT_AT_INFINITY