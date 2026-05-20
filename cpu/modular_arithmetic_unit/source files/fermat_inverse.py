"""
fermat_inverse.py
=================
Modular inverse over the NIST P-256 prime field via Fermat's Little Theorem.

Member 2 — ECE268: Security of Embedded Systems

Theory:
    Fermat's Little Theorem states that for a prime p and integer a
    where gcd(a, p) = 1:

        a^(p-1) ≡ 1 (mod p)

    Multiplying both sides by a^(-1):

        a^(p-2) ≡ a^(-1) (mod p)

    Finding the modular inverse therefore reduces to a single call
    to mod_exp with exponent (p-2) — no new algorithm is needed.

Why Fermat over Extended Euclidean:
    Fermat's exponent (p-2) has a fixed, known bit-length for any
    given prime p. This means mod_exp always executes the same number
    of iterations regardless of input a, making the operation
    constant-time with respect to a — a critical property for
    side-channel resistance in embedded systems.

    Extended Euclidean has a variable iteration count that depends on
    gcd(a, p), creating a timing side-channel exploitable by power
    analysis or timing attacks on hardware.

Limitation:
    Requires p to be prime. For composite moduli, use Extended
    Euclidean instead. For NIST P-256 this is always satisfied.
"""

from src.constants import P
from src.mod_arithmetic import mod_exp


# ── Modular inverse via Fermat's Little Theorem ────────────────────────────

def fermat_inverse(a, p=P):
    """
    Compute the modular inverse of a mod p using Fermat's Little Theorem.

    Returns x such that (a * x) % p == 1.

    Formula:
        a^(-1) ≡ a^(p-2) (mod p)

    Args:
        a (int): The value to invert. Must satisfy gcd(a, p) = 1,
                 i.e. a must not be divisible by p.
        p (int): A prime modulus. Defaults to NIST P-256 prime.

    Returns:
        int: The modular inverse of a, in range [1, p-1].

    Raises:
        ValueError: If a is divisible by p (no inverse exists).

    Example:
        >>> fermat_inverse(3, 7)    # 3 * 5 = 15 ≡ 1 (mod 7)
        5
        >>> fermat_inverse(1)
        1
        >>> fermat_inverse(P - 1)  # (-1)^(-1) = -1 = P-1
        P - 1
    """
    if a % p == 0:
        raise ValueError(
            f"No modular inverse exists: a={a} is divisible by p={p}. "
            f"Fermat's Little Theorem requires gcd(a, p) = 1."
        )
    return mod_exp(a, p - 2, p)        # ← calls mod_exp from Member 1


# ── Verification helper ────────────────────────────────────────────────────

def verify_inverse(a, p=P):
    """
    Verify that a * fermat_inverse(a) ≡ 1 (mod p).

    Args:
        a (int): Value whose inverse to check.
        p (int): Prime modulus. Defaults to NIST P-256 prime.

    Returns:
        bool: True if the inverse is correct, False otherwise.

    Example:
        >>> verify_inverse(12345)
        True
    """
    inv = fermat_inverse(a, p)
    return (a * inv) % p == 1