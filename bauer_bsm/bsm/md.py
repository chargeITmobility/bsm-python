# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from . import config
from . import dlms
from . import format as fmt
from ..sunspec.core import suns
from struct import pack


_MD_SIGNED_TYPES = \
    [
        suns.SUNS_TYPE_INT16,
        suns.SUNS_TYPE_INT32,
    ]

_MD_UNSIGNED_TYPES = \
    [
        suns.SUNS_TYPE_ACC32,
        suns.SUNS_TYPE_BITFIELD16,
        suns.SUNS_TYPE_BITFIELD32,
        suns.SUNS_TYPE_ENUM16,
        suns.SUNS_TYPE_ENUM32,
        suns.SUNS_TYPE_UINT16,
        suns.SUNS_TYPE_UINT32,
    ]

_MD_UNIMPL_VALUES = \
    {
        suns.SUNS_TYPE_ACC32:           suns.SUNS_UNIMPL_ACC32,
        suns.SUNS_TYPE_BITFIELD16:      suns.SUNS_UNIMPL_BITFIELD16,
        suns.SUNS_TYPE_BITFIELD32:      suns.SUNS_UNIMPL_BITFIELD32,
        suns.SUNS_TYPE_ENUM16:          suns.SUNS_UNIMPL_ENUM16,
        suns.SUNS_TYPE_ENUM32:          suns.SUNS_UNIMPL_ENUM32,
        suns.SUNS_TYPE_INT16:           suns.SUNS_UNIMPL_INT16,
        suns.SUNS_TYPE_UINT16:          suns.SUNS_UNIMPL_UINT16,
        suns.SUNS_TYPE_UINT32:          suns.SUNS_UNIMPL_UINT32,
        suns.SUNS_TYPE_STRING:          '',
    }


def md_for_snapshot_data(snapshot, trace=None):
    md = config.BSM_MESSAGE_DIGEST()

    update_md_from_point(md, snapshot.points['Typ'], trace=trace)
    update_md_from_point(md, snapshot.points['RCR'], trace=trace)
    update_md_from_point(md, snapshot.points['TotWhImp'], trace=trace)
    update_md_from_point(md, snapshot.points['W'], trace=trace)
    update_md_from_point(md, snapshot.points['MA1'], trace=trace)
    update_md_from_point(md, snapshot.points['RCnt'], trace=trace)
    update_md_from_point(md, snapshot.points['OS'], trace=trace)
    update_md_from_point(md, snapshot.points['Epoch'], trace=trace)
    update_md_from_point(md, snapshot.points['TZO'], trace=trace)
    update_md_from_point(md, snapshot.points['EpochSetCnt'], trace=trace)
    update_md_from_point(md, snapshot.points['EpochSetOS'], trace=trace)
    update_md_from_point(md, snapshot.points['DI'], trace=trace)
    update_md_from_point(md, snapshot.points['DO'], trace=trace)
    update_md_from_point(md, snapshot.points['Meta1'], trace=trace)
    update_md_from_point(md, snapshot.points['Meta2'], trace=trace)
    update_md_from_point(md, snapshot.points['Meta3'], trace=trace)
    update_md_from_point(md, snapshot.points['Evt'], trace=trace)

    return md.digest()


def md_value_and_scaler_for_point(point):
    type_ = point.point_type.type
    value = point.value_base
    scaler = point.value_sf

    # Fixup value an scaler for the 'not implemented' case which gets reported
    # as None by pySunSpec.

    if value is None:
        try:
            value = _MD_UNIMPL_VALUES[type_]
        except KeyError as cause:
            raise TypeError('Unsupported point type \'{}\'.'.format(type_)) from cause

    if scaler is None:
        scaler = 0

    return (value, scaler)


def update_md_from_point(md, point, trace=None):
    type_ = point.point_type.type
    dlms_unit = dlms.dlms_unit_for_symbol(point.point_type.units)
    (value, scaler) = md_value_and_scaler_for_point(point)

    data = None

    if type_ in _MD_UNSIGNED_TYPES:
        data = data_for_scaled_uint32(md, value, scaler, dlms_unit)
    elif type_ in _MD_SIGNED_TYPES:
        data = data_for_scaled_int32(md, value, scaler, dlms_unit)
    elif type_ == suns.SUNS_TYPE_STRING:
        data = data_for_string(md, value)
    else:
        raise TypeError('Unsupported point type \'{}\'.'.format(type_))

    md.update(data)

    if trace:
        trace('{}:\n    value: {}\n    data:  {}\n'.format(point.point_type.id,
            fmt.format_point_value(point), data.hex()))


def data_for_scaled_int32(md, value, scaler, unit):
    return pack('>lbB', value, scaler, unit)


def data_for_scaled_uint32(md, value, scaler, unit):
    return pack('>LbB', value, scaler, unit)


def data_for_string(md, string):
    # This only works for text strigns and get away with it as long as we
    # are not dealing with binary strings.
    #
    # TODO: Latin 1 encoding seems a bit limited for generic metadata. What
    # about switching to UTF-8? This would require making string data
    # interpretation configurable in pySunSpec.
    data = string.encode(config.PYSUNSPEC_STRING_ENCODING)
    length = pack('>L', len(string))

    return length + data
