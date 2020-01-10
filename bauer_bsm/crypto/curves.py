from ecdsa import ellipticcurve
from ecdsa.curves import Curve


# Curve parameters of secp256r1 from 'SEC 2:  Recommended Elliptic Curve Domain
# Parameters' (https://www.secg.org/sec2-v2.pdf), section 2.4.2 'Recommended
# Parameters secp256r1'.
P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
R = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

CURVE_SECP256R1 = ellipticcurve.CurveFp(P, A, B)
GENERATOR_SECP256R1 = ellipticcurve.Point(CURVE_SECP256R1, GX, GY, R)

# Curve secp256r1. The Python ecdsa package does not ship it for whatever
# reason. OID from http://oid-info.com/get/1.2.840.10045.3.1.7.
SECP256r1 = Curve("SECP256r1", CURVE_SECP256R1, GENERATOR_SECP256R1, (1, 2, 840, 10045, 3, 1, 7), "secp256r1")
