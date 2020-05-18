# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ecdsa import BadSignatureError
from ecdsa import VerifyingKey
from ecdsa import ellipticcurve
from ecdsa import util


def public_key_from_coordinates(curve, md, x, y):
    """
    Generates an verification key from the given curve, message digest and
    point coordinates.
    """
    point = ellipticcurve.Point(curve.curve, x, y)
    return VerifyingKey.from_public_point(point, curve=curve, hashfunc=md)


def verify_signed_digest(curve, md, pubkey_data, signature_data, digest,
        keydecode=util.sigdecode_string, sigdecode=util.sigdecode_string):
    """
    Verifies the signature for the given message digest and public key.

    You may explicitly specify a decoder for public key and signature data. By
    default a decoder for catenated binary strings
    (ecdsa.util.sigdecode_string) is used.
    """
    result = False

    (x, y) = keydecode(pubkey_data, curve.order)
    pubkey = public_key_from_coordinates(curve, md, x, y)
    try:
        result = pubkey.verify_digest(signature_data, digest, sigdecode=sigdecode)
    except BadSignatureError:
        result = False

    return result
