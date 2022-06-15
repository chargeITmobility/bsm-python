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


def md_scaler_for_point(point):
    scaler = point.value_sf

    # Fixup the scaler for our message digests computation. There are values
    # which do have a scaler associated at all and we use zero in this case.
    # And there are cases where the value is 'not implemented' and the actually
    # available scaler is not present in value_sf.
    if scaler is None:
        if point.sf_point is None:
            scaler = 0
        else:
            scaler = point.sf_point.value_base

    return scaler


def md_value_and_scaler_for_point(point):
    type_ = point.point_type.type
    value = point.value_base
    scaler = md_scaler_for_point(point)

    # Fixup value for the 'not implemented' case which gets reported as None by
    # pySunSpec.
    if value is None:
        try:
            value = _MD_UNIMPL_VALUES[type_]
        except KeyError as cause:
            raise TypeError('Unsupported point type \'{}\' cause of {}.'.format(type_, cause))

    return (value, scaler)


def update_md_from_point(md, point, trace=None):
    type_ = point.point_type.type
    dlms_unit = dlms.dlms_unit_for_symbol(point.point_type.units)
    (value, scaler) = md_value_and_scaler_for_point(point)

    data = None
    trace_data_slicer = None

    if type_ in _MD_UNSIGNED_TYPES:
        data = data_for_scaled_uint32(md, value, scaler, dlms_unit)
        trace_data_slicer = scaled_int32_uint32_slicer
    elif type_ in _MD_SIGNED_TYPES:
        data = data_for_scaled_int32(md, value, scaler, dlms_unit)
        trace_data_slicer = scaled_int32_uint32_slicer
    elif type_ == suns.SUNS_TYPE_STRING:
        data = data_for_string(md, value)
        trace_data_slicer = string_slicer
    else:
        raise TypeError('Unsupported point type \'{}\'.'.format(type_))

    md.update(data)

    if trace:
        # Render trace data separated by spaces to improve readability if
        # slicing has been provided.
        if trace_data_slicer:
            rendered = ' '.join(map(lambda x: x.hex(), trace_data_slicer(data)))
        else:
            rendered = data.hex()

        trace('{}:\n    value: {}\n    data:  {}\n'.format(point.point_type.id,
            fmt.format_point_value(point), rendered))


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


def scaled_int32_uint32_slicer(data):
    return [data[:4], data[4:5], data[5:]]


def string_slicer(data):
    return [data[:4], data[4:]]
