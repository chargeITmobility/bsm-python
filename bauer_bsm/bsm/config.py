# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..crypto.curves import SECP256r1
from hashlib import sha256


# TODO: What about making the encoding a configurable property of the SunSpec
# device?
PYSUNSPEC_STRING_ENCODING = 'iso-8859-1'


BSM_CURVE = SECP256r1
BSM_CURVE_NAME = 'secp256r1'
BSM_CURVE_ALIASES = [BSM_CURVE_NAME, 'secp256v1', 'NIST256p']
BSM_MESSAGE_DIGEST = sha256


BSM_MODEL_ALIAS = 'sm'
BSM_PUBLIC_KEY_BYTES_DATA_POINT_ID = 'BPK'
BSM_PUBLIC_KEY_REGS_DATA_POINT_ID = 'NPK'


OCMF_DATA_DATA_POINT_ID = 'O'
OCMF_STATUS_DATA_POINT_ID = 'St'


SNAPSHOT_SIGNATURE_REGS_DATA_POINT_ID = 'NSig'
SNAPSHOT_STATUS_DATA_POINT_ID = 'St'
SNAPSHOT_STATUS_UPDATING_SYMBOL_ID = 'UPDATING'
SNAPSHOT_STATUS_VALID_SYMBOL_ID = 'VALID'
