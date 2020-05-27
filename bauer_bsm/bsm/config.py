# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..crypto.curves import SECP256r1
from hashlib import sha256


# TODO: What about making the encoding a configurable property of the SunSpec
# device?
PYSUNSPEC_STRING_ENCODING = 'latin-1'


BSM_CURVE = SECP256r1
BSM_CURVE_NAME = 'secp256r1'
BSM_MESSAGE_DIGEST = sha256


BSM_MODEL_ALIAS = 'sm'
BSM_CURVE_NAME_DATA_POINT_ID = 'Curve'
BSM_PUBLIC_KEY_LENGTH_DATA_POINT_ID = 'NPK'


SNAPSHOT_SIGNATURE_LENGTH_DATA_POINT_ID = 'NSig'
SNAPSHOT_STATUS_DATA_POINT_ID = 'St'
SNAPSHOT_STATUS_UPDATING_SYMBOL_ID = 'UPDATING'
SNAPSHOT_STATUS_VALID_SYMBOL_ID = 'VALID'
