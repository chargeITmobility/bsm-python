# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from aenum import IntEnum


# An incomplete enum of DLMS unit encoding.
#
# TODO: This enum contains only the units used in BSM snapshots by now.
class DlmsUnits(IntEnum):
    MINUTES = 6
    SECONDS = 7
    WATTS = 27
    WATT_HOURS = 30
    UNITLESS = 255


DLMS_UNITS_BY_SYMBOLS = {
        'W': DlmsUnits.WATTS,
        'Wh': DlmsUnits.WATT_HOURS,
        'min': DlmsUnits.MINUTES,
        's': DlmsUnits.SECONDS,
        None: DlmsUnits.UNITLESS,
    }


def dlms_unit_for_symbol(symbol):
    # Let's have an exception in case of an unknown symbol.
    return DLMS_UNITS_BY_SYMBOLS[symbol]
