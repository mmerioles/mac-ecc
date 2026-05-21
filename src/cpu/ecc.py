from cpu.constants import P, A_COEF, B_COEF, G, N, POINT_AT_INFINITY
from cpu.modulus import mod_multiply, fermat_inverse


def point_add(P1, P2):
    """Add two points on the elliptic curve."""
    if P1 is POINT_AT_INFINITY:
        return P2
    if P2 is POINT_AT_INFINITY:
        return P1

    x1, y1 = P1
    x2, y2 = P2

    if x1 == x2:
        if y1 != y2:
            return POINT_AT_INFINITY
        return point_double(P1)

    slope = ((y2 - y1) * fermat_inverse((x2 - x1) % P, P)) % P

    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P

    return (x3, y3)


def point_double(P1):
    """Double a point on the elliptic curve."""
    if P1 is POINT_AT_INFINITY:
        return POINT_AT_INFINITY

    x1, y1 = P1

    slope = ((3 * x1 * x1 + A_COEF) * fermat_inverse((2 * y1) % P, P)) % P

    x3 = (slope * slope - 2 * x1) % P
    y3 = (slope * (x1 - x3) - y1) % P

    return (x3, y3)


def scalar_multiply(k, point):
    """Compute k times a point using double-and-add."""
    result = POINT_AT_INFINITY
    addend = point

    while k > 0:
        if k & 1:
            result = point_add(result, addend)

        addend = point_double(addend)
        k >>= 1

    return result


def is_on_curve(point):
    """Check if a point is on the elliptic curve."""
    if point is POINT_AT_INFINITY:
        return True

    x, y = point

    left = (y * y) % P
    right = (x**3 + A_COEF * x + B_COEF) % P

    return left == right


def ecdh_shared_secret(private_key, peer_public_key):
    """Compute an ECDH shared secret point."""
    if not is_on_curve(peer_public_key):
        raise ValueError("Peer public key is not on the curve")

    return scalar_multiply(private_key, peer_public_key)