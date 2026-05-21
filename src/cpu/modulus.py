def do_something():
    print('doing something')
    return True

def mod_multiply(a: int, b: int, p: int) -> int:
    """
    Computes modular multiplication.

    Returns (a * b) mod p.
    """
    return (a * b) % p

def mod_exp(a: int, exp: int, p: int) -> int:
    """
    Computes modular exponentiation.

    Returns (a^exp) mod p using square-and-multiply.
    """
    result = 1
    base = a % p
    while exp > 0:
        if exp % 2 == 1:
            result = mod_multiply(result, base, p)
        exp >>= 1
        base = mod_multiply(base, base, p)
    return result


def fermat_inverse(a: int, p: int) -> int:
    """
    Computes modular inverse using Fermat's Little Theorem.

    Returns a^(p-2) mod p.
    """
    if a == 0:
        raise ValueError("0 has no modular inverse")

    return mod_exp(a, p - 2, p)
