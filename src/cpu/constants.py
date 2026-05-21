"""
constants.py
============
Shared NIST P-256 curve parameters used by all modules.

Curve equation:  y² ≡ x³ + A_COEF·x + B_COEF  (mod P)

Source: FIPS 186-4, NIST SP 800-186
"""

# ── Prime field modulus (256-bit prime) ────────────────────────────────────
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

# ── Curve coefficients ─────────────────────────────────────────────────────
A_COEF = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
B_COEF = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B

# ── Generator point G ──────────────────────────────────────────────────────
Gx = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
Gy = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
G  = (Gx, Gy)

# ── Curve order (smallest n such that n·G = point at infinity) ─────────────
N  = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# ── Identity element of the elliptic curve group ───────────────────────────
POINT_AT_INFINITY = None