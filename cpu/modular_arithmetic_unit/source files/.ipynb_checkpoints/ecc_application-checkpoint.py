"""
ecc.py
======
Elliptic Curve Cryptography over NIST P-256.

Member 3 — ECE268: Security of Embedded Systems

Curve:
    y² ≡ x³ + A_COEF·x + B_COEF  (mod P)

    NIST P-256 (also known as secp256r1 or prime256v1) is the
    industry-standard 256-bit elliptic curve used in TLS 1.3,
    HTTPS, JWT signatures, and embedded security chips.

Application — ECDH (Elliptic Curve Diffie-Hellman):
    1. Alice picks private key a, computes public key A = a·G
    2. Bob   picks private key b, computes public key B = b·G
    3. Alice computes shared secret: a·B = a·(b·G) = (ab)·G
    4. Bob   computes shared secret: b·A = b·(a·G) = (ab)·G
    5. Both arrive at the same point without revealing private keys.

    Security relies on the Elliptic Curve Discrete Logarithm Problem
    (ECDLP): given G and k·G, finding k requires O(√N) operations
    ≈ 2^128 for P-256 — computationally infeasible.

Dependency on Fermat inverse:
    Point addition and doubling both require one modular inverse per
    call (to compute the slope λ). This is provided by Member 2's
    fermat_inverse, which in turn calls Member 1's mod_exp.

    Call chain:
        scalar_multiply → point_add / point_double
                       → fermat_inverse  (Member 2)
                       → mod_exp         (Member 1)
                       → mod_mul         (Member 1)
"""

from src.constants import P, A_COEF, B_COEF, G, N, POINT_AT_INFINITY
from src.mod_arithmetic import mod_mul, mod_sub
from src.fermat_inverse import fermat_inverse


# ── Point addition ─────────────────────────────────────────────────────────

def point_add(P1, P2):
    """
    Add two points on the NIST P-256 elliptic curve.

    Short Weierstrass addition formula:
        λ  = (y2 - y1) · (x2 - x1)^(-1)  mod p
        x3 = λ² - x1 - x2                 mod p
        y3 = λ·(x1 - x3) - y1             mod p

    Special cases handled:
        - Either input is the identity (point at infinity) → return the other
        - Same x, different y → points are additive inverses → return identity
        - P1 == P2 → delegates to point_double

    Args:
        P1 (tuple | None): First point (x, y) or POINT_AT_INFINITY.
        P2 (tuple | None): Second point (x, y) or POINT_AT_INFINITY.

    Returns:
        tuple | None: Resulting point (x, y) or POINT_AT_INFINITY.

    Example:
        >>> point_add(G, G) == scalar_multiply(2, G)
        True
        >>> point_add(G, POINT_AT_INFINITY) == G
        True
    """
    if P1 is POINT_AT_INFINITY: return P2
    if P2 is POINT_AT_INFINITY: return P1

    x1, y1 = P1
    x2, y2 = P2

    if x1 == x2:
        if y1 != y2:                            # P + (-P) = identity
            return POINT_AT_INFINITY
        return point_double(P1)                 # P + P = 2P

    # General addition
    lam = mod_mul(
        mod_sub(y2, y1),
        fermat_inverse(mod_sub(x2, x1))        # ← Member 2
    )
    x3 = (mod_mul(lam, lam) - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


# ── Point doubling ─────────────────────────────────────────────────────────

def point_double(P1):
    """
    Double a point on the NIST P-256 elliptic curve: compute P1 + P1.

    Tangent line formula:
        λ  = (3·x1² + a) · (2·y1)^(-1)   mod p
        x3 = λ² - 2·x1                    mod p
        y3 = λ·(x1 - x3) - y1             mod p

    Args:
        P1 (tuple | None): Point to double, or POINT_AT_INFINITY.

    Returns:
        tuple | None: Resulting point (x, y) or POINT_AT_INFINITY.

    Example:
        >>> point_double(G) == scalar_multiply(2, G)
        True
    """
    if P1 is POINT_AT_INFINITY:
        return POINT_AT_INFINITY

    x1, y1 = P1
    num = (3 * mod_mul(x1, x1) + A_COEF) % P
    den = (2 * y1) % P
    lam = mod_mul(num, fermat_inverse(den))     # ← Member 2

    x3 = (mod_mul(lam, lam) - 2 * x1) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


# ── Scalar multiplication ──────────────────────────────────────────────────

def scalar_multiply(k, point):
    """
    Compute k * point using the double-and-add algorithm.

    This is the elliptic curve analogue of square-and-multiply:
        - Process each bit of k from LSB to MSB
        - Double the running accumulator on every step
        - Add the current point only when the current bit is 1

    Complexity: O(log k) point operations — ~256 doublings and
    ~128 additions on average for a 256-bit scalar k.

    Args:
        k     (int):         Scalar multiplier. Must satisfy 0 <= k < N.
        point (tuple | None): Base point (x, y) or POINT_AT_INFINITY.

    Returns:
        tuple | None: k * point, or POINT_AT_INFINITY if k = 0.

    Example:
        >>> scalar_multiply(1, G) == G
        True
        >>> scalar_multiply(N, G) is POINT_AT_INFINITY
        True
        >>> scalar_multiply(0, G) is POINT_AT_INFINITY
        True
    """
    result = POINT_AT_INFINITY              # identity element
    addend = point

    while k:
        if k & 1:                           # current bit is 1 → add
            result = point_add(result, addend)
        addend = point_double(addend)       # always double
        k >>= 1

    return result


# ── Curve membership check ─────────────────────────────────────────────────

def on_curve(pt):
    """
    Check whether a point satisfies the P-256 curve equation.

    Verifies:  y² ≡ x³ + A_COEF·x + B_COEF  (mod P)

    Args:
        pt (tuple | None): Point (x, y) or POINT_AT_INFINITY.

    Returns:
        bool: True if pt is on the curve (or is the point at infinity).

    Example:
        >>> on_curve(G)
        True
        >>> on_curve(POINT_AT_INFINITY)
        True
    """
    if pt is POINT_AT_INFINITY:
        return True
    x, y = pt
    lhs = pow(y, 2, P)
    rhs = (pow(x, 3, P) + A_COEF * x + B_COEF) % P
    return lhs == rhs


# ── ECDH key exchange ──────────────────────────────────────────────────────

def ecdh_generate_keypair():
    """
    Generate a random ECDH key pair (private_key, public_key).

    Returns:
        tuple: (private_key (int), public_key (x, y))
               private_key is a random integer in [1, N-1]
               public_key  is private_key * G on P-256
    """
    import random
    private_key = random.randint(1, N - 1)
    public_key  = scalar_multiply(private_key, G)
    return private_key, public_key


def ecdh_shared_secret(private_key, peer_public_key):
    """
    Compute the ECDH shared secret given own private key and peer's public key.

    Both parties compute the same point:
        Alice: alice_priv * bob_pub   = (alice_priv * bob_priv) * G
        Bob:   bob_priv   * alice_pub = (bob_priv * alice_priv) * G

    Args:
        private_key     (int):   Own private key.
        peer_public_key (tuple): Peer's public key point (x, y).

    Returns:
        tuple: Shared secret point (x, y).
               In practice only the x-coordinate is used,
               passed through a KDF to derive symmetric keys.

    Raises:
        ValueError: If peer_public_key is not on the P-256 curve.
    """
    if not on_curve(peer_public_key):
        raise ValueError(
            "Peer public key is not on the P-256 curve. "
            "Possible invalid or malicious key."
        )
    return scalar_multiply(private_key, peer_public_key)