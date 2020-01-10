from ecdsa import BadSignatureError
from ecdsa import VerifyingKey
from ecdsa import ellipticcurve
from ecdsa import util




SEC1_UNCOMPRESSED_POINT_MARKER = 0x04




def public_key_from_sec1_point_data(curve, md, data):
    assert len(data) > 1
    assert len(data) % 2 == 1
    assert data[0] == SEC1_UNCOMPRESSED_POINT_MARKER

    # Extract coordinates from 'Standards for EfficientCryptography 1 (SEC 1)'
    # point coordinates.
    length = (len(data) - 1) // 2
    x = int.from_bytes(data[1:1 + length], 'big')
    y = int.from_bytes(data[1 + length:1 + 2 * length], 'big')

    point = ellipticcurve.Point(curve.curve, x, y)
    return VerifyingKey.from_public_point(point, curve=curve, hashfunc=md)


def verify_signed_digest(curve, md, pubkey_data, signature_data, digest, sigdecode=util.sigdecode_der):
    result = False

    pubkey = public_key_from_sec1_point_data(curve, md, pubkey_data)
    try:
        result = pubkey.verify_digest(signature_data, digest, sigdecode=sigdecode)
    except BadSignatureError:
        result = False

    return result
