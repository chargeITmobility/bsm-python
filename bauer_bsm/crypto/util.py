# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ecdsa import BadSignatureError
from ecdsa import VerifyingKey
from ecdsa import ellipticcurve
from ecdsa import util




def der_public_key(public_key):
    """
    Generates a DER represetnation of the given public key.
    """
    return public_key.to_der();


def public_key_data_from_blob(curve, md, blob, output_format):
    """
    Generates a binary representation of the given public key according to the
    specified format.
    """
    renderer = PUBLIC_KEY_RENDERER[output_format]
    public_key = public_key_from_blob(curve, md, blob)
    return renderer(public_key)


def public_key_from_blob(curve, md, blob):
    """
    Generates a verification key from the tiven curve, message digst and binary
    point representation (X || Y).
    """
    (x, y) = util.sigdecode_string(blob, curve.order)
    return public_key_from_coordinates(curve, md, x ,y)


def public_key_from_coordinates(curve, md, x, y):
    """
    Generates a verification key from the given curve, message digest and point
    coordinates.
    """
    point = ellipticcurve.Point(curve.curve, x, y)
    return VerifyingKey.from_public_point(point, curve=curve, hashfunc=md)


def raw_public_key(public_key):
    """
    Generates a raw pepresentation of the public key (r || s).
    """
    return public_key.to_string('raw')


def sec1_compressed_public_key(public_key):
    """
    Generates the compressed point representation (SEC1, section 2.3.3) for the
    given public key.
    """
    return public_key.to_string('compressed')


def sec1_uncompressed_public_key(public_key):
    """
    Generates the copressed point representation (SEC1, section 2.3.3) for the
    given public key.
    """
    return public_key.to_string('uncompressed')


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




PUBLIC_KEY_DEFAULT_FORMAT = 'raw'
PUBLIC_KEY_RENDERER = {
        'der': der_public_key,
        'raw': raw_public_key,
        'sec1-compressed': sec1_compressed_public_key,
        'sec1-uncompressed': sec1_uncompressed_public_key,
    }
