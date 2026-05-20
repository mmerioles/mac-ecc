"""
mod_arithmetic.py
=================
Core modular arithmetic engine over the NIST P-256 prime field.

Member 1 — ECE268: Security of Embedded Systems

Implements:
    mod_add  : (a + b) mod p
    mod_sub  : (a - b) mod p
    mod_mul  : (a * b) mod p
    mod_exp  : a^e mod p  via square-and-multiply

All functions accept an optional prime p (default: NIST P-256 prime).
This allows reuse with any prime field, not just P-256.
"""

from src.constants import P


# ── Modular addition ───────────────────────────────────────────────────────

def mod_add(a, b, p=P):
    """
    Compute (a + b) mod p.

    Args:
        a (int): First operand. Must satisfy 0 <= a < p.
        b (int): Second operand. Must satisfy 0 <= b < p.
        p (int): Prime modulus. Defaults to NIST P-256 prime.

    Returns:
        int: (a + b) mod p, in range [0, p-1].

    Example:
        >>> mod_add(3, 5, 7)
        1
        >>> mod_add(P - 1, 1)   # wrap-around
        0
    """
    return (a + b) % p


# ── Modular subtraction ────────────────────────────────────────────────────

def mod_sub(a, b, p=P):
    """
    Compute (a - b) mod p.

    Python's % operator correctly handles negative intermediate
    results, so no explicit correction is needed.

    Args:
        a (int): Minuend.
        b (int): Subtrahend.
        p (int): Prime modulus. Defaults to NIST P-256 prime.

    Returns:
        int: (a - b) mod p, in range [0, p-1].

    Example:
        >>> mod_sub(3, 5, 7)    # -2 mod 7 = 5
        5
        >>> mod_sub(0, 1)       # wraps to P - 1
        P - 1
    """
    return (a - b) % p


# ── Modular multiplication ─────────────────────────────────────────────────

def mod_mul(a, b, p=P):
    """
    Compute (a * b) mod p.

    Args:
        a (int): First operand.
        b (int): Second operand.
        p (int): Prime modulus. Defaults to NIST P-256 prime.

    Returns:
        int: (a * b) mod p, in range [0, p-1].

    Example:
        >>> mod_mul(3, 4, 7)    # 12 mod 7 = 5
        5
        >>> mod_mul(P - 1, P - 1)   # (-1) * (-1) = 1
        1
    """
    return (a * b) % p


# ── Modular exponentiation ─────────────────────────────────────────────────

def mod_exp(base, exp, p=P):
    """
    Compute base^exp mod p using the square-and-multiply algorithm.

    Algorithm:
        Process the exponent bit-by-bit from LSB to MSB.
        On every step: square the base.
        When the current bit is 1: also multiply result by base.

    Complexity: O(log exp) multiplications — feasible for 256-bit exponents
    where naive repeated multiplication would require up to 2^256 steps.

    Args:
        base (int): Base value.
        exp  (int): Exponent. Must be >= 0.
        p    (int): Prime modulus. Defaults to NIST P-256 prime.

    Returns:
        int: base^exp mod p, in range [0, p-1].

    Example:
        >>> mod_exp(2, 10, P) == pow(2, 10, P)
        True
        >>> mod_exp(any, 0, P)  # a^0 = 1
        1
        >>> mod_exp(0, any, P)  # 0^n = 0
        0
    """
    result = 1
    base   = base % p

    while exp > 0:
        if exp % 2 == 1:                    # current LSB is 1 → multiply
            result = mod_mul(result, base, p)
        exp  >>= 1                          # shift to next bit
        base   = mod_mul(base, base, p)     # square

    return result