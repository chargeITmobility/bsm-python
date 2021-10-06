# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..bsm import config
from ..bsm import dlms
from ..bsm.client import BsmClientDevice, SnapshotStatus, SunSpecBsmClientDevice
from ..sunspec.core import suns
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
import json
import uuid




_CHARGY_IGNORED_SNAPSHOT_DATA_POINT_IDS = {'St', 'NSig', 'BSig', 'Sig'}

_CHARGY_MEASURAND_ID_BY_SNAPSHOT_DATA_POINT_ID = {
        'MA1': '1-0:0.0.0*255',
        'RCR': '1-0:1.8.0*198',
        'TotWhImp': '1-0:1.8.0*255',
        'W': '1-0:1.7.0*255',
    }

_CHARGY_NUMERIC_DATA_POINT_TYPES = {
        suns.SUNS_TYPE_ACC32,
        suns.SUNS_TYPE_BITFIELD32,
        suns.SUNS_TYPE_ENUM16,
        suns.SUNS_TYPE_INT16,
        suns.SUNS_TYPE_INT32,
        suns.SUNS_TYPE_UINT16,
        suns.SUNS_TYPE_UINT32,
    }

_CHARGY_UNIT_NAME_BY_SUNSPEC_UNIT = {
        'W': 'WATT',
        'Wh': 'WATT_HOUR',
        'min': 'MINUTE',
        's': 'SECOND',
    }

_CHARGY_VALUE_TYPE_BY_SUNSPEC_TYPE = {
        suns.SUNS_TYPE_ACC32: 'UnsignedInteger32',
        suns.SUNS_TYPE_BITFIELD32: 'UnsignedInteger32',
        suns.SUNS_TYPE_ENUM16: 'UnsignedInteger32',
        suns.SUNS_TYPE_INT16: 'Integer32',
        suns.SUNS_TYPE_INT32: 'Integer32',
        suns.SUNS_TYPE_STRING: 'String',
        suns.SUNS_TYPE_UINT16: 'UnsignedInteger32',
        suns.SUNS_TYPE_UINT32: 'UnsignedInteger32',
    }

_SNAPSHOT_METADATA_POINT_IDS = [
        config.SNAPSHOT_META1_DATA_POINT_ID,
        config.SNAPSHOT_META2_DATA_POINT_ID,
        config.SNAPSHOT_META3_DATA_POINT_ID,
    ]


_KNOWN_ID_TYPE_SCHEMES = ['rfid', 'sms']




def _generate_chargy_contract_information(snapshot):
    contract = _tagged_snapshot_metadata(snapshot, 'contract-id')
    result = {}

    if contract is not None and any(map(lambda s: contract.startswith(s + ':'), _KNOWN_ID_TYPE_SCHEMES)):
        (type_, id_) = contract.split(':', 1)
        result['id'] = id_
        result['type'] = type_
    else:
        result['id'] = contract

    return result



def _generate_chargy_data(client, start_alias, end_alias, read_data=True, station_serial_number=None, station_compliance_info=None):
    data = None

    common = client.model_aliases[config.COMMON_INSTANCE_ALIAS]
    bsm = client.model_aliases[config.BSM_INSTANCE_ALIAS]
    start = client.model_aliases[start_alias]
    end = client.model_aliases[end_alias]

    if read_data:
        common.read_points()
        bsm.read_points()
        start.read_points()
        end.read_points()

    start_data = _generate_chargy_snapshot_data(client, common, bsm, start)
    end_data = _generate_chargy_snapshot_data(client, common, bsm, end)

    if start_data and end_data:
        data = OrderedDict()

        data['@context'] = 'https://www.chargeit-mobility.com/contexts/charging-station-json-v1'
        # The BSM Python support has no natural unique identifier for a
        # charging process. Let's use an UUID then.
        data['@id'] = str(uuid.uuid4())
        data['chargePointInfo'] = _generate_chargy_point_info_data(client,
            start, end)
        data['chargingStationInfo'] = _generate_chargy_station_info_data(
            client,
            start,
            end,
            serial_number=station_serial_number,
            compliance_info=station_compliance_info)
        data['signedMeterValues'] = [start_data, end_data]

    return data


def _generate_chargy_place_info_data(client):
    info = OrderedDict()

    # Provide some dummy information for testing.
    info['geoLocation'] = {'lat': 48.03552, 'lon': 10.50669}
    info['address'] = {'street': 'Breitenbergstr. 2', 'town': 'Mindelheim', 'zipCode': '87719'}

    return info


def _generate_chargy_point_info_data(client, start, end):
    data = OrderedDict()

    data['placeInfo'] = _generate_chargy_place_info_data(client)
    data['evseId'] = _tagged_snapshots_metadata(start, end, 'evse-id')

    return data


def _generate_chargy_snapshot_data(client, common, bsm, snapshot):
    data = None

    snapshot_status = snapshot.points[config.SNAPSHOT_STATUS_DATA_POINT_ID].value

    if snapshot_status == SnapshotStatus.VALID:
        data = OrderedDict()

        meter_id = snapshot.points[config.SNAPSHOT_METER_ADDRESS_1_DATA_POINT_ID].value
        response_counter = snapshot.points[config.SNAPSHOT_RESPONSE_COUNTER_DATA_POINT_ID].value

        data['@context'] = 'https://www.chargeit-mobility.com/contexts/bsm-ws36a-json-v1'
        # Device ID and response counter give a unique ID for a snapshot.
        data['@id'] = '{}-{}'.format(meter_id, response_counter)

        # The point in time of this measurement in ISO 8601 representation of
        # epoch time and timezone offset. The latter are given in their native
        # representation in 'additionalValues' to facilitate snapshot hash
        # computation.
        epoch_seconds = snapshot.points[config.SNAPSHOT_EPOCH_TIME_DATA_POINT_ID].value
        timezone_offset_minutes = snapshot.points[config.SNAPSHOT_TIMEZONE_OFFSET_DATA_POINT_ID].value
        when = None
        if epoch_seconds is not None and timezone_offset_minutes is not None:
            timezone_ = timezone(timedelta(minutes=timezone_offset_minutes))
            when = datetime.fromtimestamp(epoch_seconds, timezone_)
        if when is not None:
            data['time'] = when.isoformat()

        # Provide a combined firmware information string for meter and
        # communication module.
        firmware_version = '{}, {}'.format(
            bsm.points[config.BSM_SOFTWARE_VERSION_METER_DATA_POINT_ID].value,
            bsm.points[config.BSM_SOFTWARE_VERSION_COMMUNICATION_MODULE_DATA_POINT_ID].value)
        data['meterInfo'] = {
                'firmwareVersion': firmware_version,
                'publicKey': client.get_public_key(read_data=False).hex(),
                'meterId': meter_id,
                'manufacturer': common.points[config.COMMON_MANUFACTURER_DATA_POINT_ID].value,
                'type': common.points[config.COMMON_MODEL_DATA_POINT_ID].value,
            }

        data['contract'] = _generate_chargy_contract_information(snapshot)
        data['measurementId'] = response_counter
        data['value'] = _generate_chargy_snapshot_value_data(client, snapshot.points[config.SNAPSHOT_REFERENCE_CUMULATIVE_REGISTER_DATA_POINT_ID])

        # Provide snapshot data points except status and signature "in order of
        # their appearance" which is the order for computing the message digest
        # for signing.
        additional_values = []
        for point_id, point in snapshot.points.items():
            if point_id not in _CHARGY_IGNORED_SNAPSHOT_DATA_POINT_IDS:
                additional_values.append(_generate_chargy_snapshot_value_data(client, point))
        data['additionalValues'] = additional_values

        data['signature'] = snapshot.device.repeating_blocks_blob(snapshot).hex()

    return data


def _generate_chargy_snapshot_value_data(client, point):
    measurand = OrderedDict()
    # Provide OBIS ID where available.
    measurand_id = _CHARGY_MEASURAND_ID_BY_SNAPSHOT_DATA_POINT_ID.get(point.point_type.id, None)
    _put_non_null(measurand, 'id', measurand_id)
    _put_non_null(measurand, 'name', point.point_type.id)

    value = OrderedDict()
    point_type = point.point_type.type
    # Provide a scale factor. Either the one explicity given by an associated
    # scale factor data point. Or the default value 10^0 == 1 which the device
    # uses when computing the message digtst for singing.
    scale = None
    if point.sf_point:
        scale = point.sf_point.value_base
    elif point_type in _CHARGY_NUMERIC_DATA_POINT_TYPES:
        scale = 0
    # Provide a unit. Either the unit explicitly specified by the model or
    # "unitless" indicated by DLMS code 255 (and a JSON null here). The device
    # uses the latter for numeric values which have no explicitly assigned unit
    # when computing the message digest for signing.
    value_unit_name = None
    value_unit_encoded = None
    if point.point_type.units is not None:
        value_unit_name = _CHARGY_UNIT_NAME_BY_SUNSPEC_UNIT[point.point_type.units]
        value_unit_encoded = dlms.dlms_unit_for_symbol(point.point_type.units)
    elif point_type in _CHARGY_NUMERIC_DATA_POINT_TYPES:
        value_unit_encoded = dlms.DlmsUnits.UNITLESS
    value_value = point.value_base
    # SunSpec defines zero as 'not accumulated'/invalid value for accumulators
    # and pySunSpec returns them as None. Let's have a numeric output in this
    # case.
    if point_type == suns.SUNS_TYPE_ACC32 and point.value_base is None:
        value_value = 0
    # Provide the encoding for string values at the time of hashing. The
    # pySunSpec stack used by the BSM TOOL uses Latin 1/ISO-8859-1. If no
    # encoding is given, UTF-8 will be assumed.
    encoding = None
    if point_type is suns.SUNS_TYPE_STRING:
        encoding = 'ISO-8859-1'
    _put_non_null(value, 'scale', scale)
    _put_non_null(value, 'unit', value_unit_name)
    _put_non_null(value, 'unitEncoded', value_unit_encoded)
    _put_non_null(value, 'value', value_value)
    _put_non_null(value, 'valueType', _CHARGY_VALUE_TYPE_BY_SUNSPEC_TYPE[point.point_type.type])
    _put_non_null(value, 'valueEncoding', encoding)

    data = OrderedDict()
    data['measurand'] = measurand
    data['measuredValue'] = value
    return data


def _generate_chargy_station_info_data(client, start, end, serial_number=None, compliance_info=None):
    data = OrderedDict()

    data['manufacturer'] = 'chargeIT mobility GmbH'
    data['type'] = 'CIT Ladesäule online'
    _put_non_null(data, 'serialNumber', serial_number)
    _put_non_null(data, 'controllerSoftwareVersion', _tagged_snapshots_metadata(start, end, 'csc-sw-version'))
    _put_non_null(data, 'compliance', compliance_info)

    return data


def _put_non_null(dict_, key, value):
    if value is not None:
        dict_[key] = value


def _tagged_snapshot_metadata(snapshot, tag):
    prefix = tag + ': '
    result = None

    for id_ in _SNAPSHOT_METADATA_POINT_IDS:
        value = snapshot.points[id_].value
        if value is not None and value.startswith(prefix):
            result = value[len(prefix):]

    return result


def _tagged_snapshots_metadata(start, end, tag):
    start_value = _tagged_snapshot_metadata(start, tag)
    end_value = _tagged_snapshot_metadata(end, tag)

    assert start_value == end_value

    return start_value


def generate_chargy_json(client, start_alias, end_alias, read_data=True, station_serial_number=None, station_compliance_info=None):
    """
    Generates a chargeIT mobility JSON document from signed turn-on and
    turn-off snapshots.

    The JSON document will be UTF-8 encoded. In case that one of the
    snapshots is not valid, None will be returned.
    """
    # Allow passing both types of BSM clients.
    if isinstance(client, SunSpecBsmClientDevice):
        client = client.device
    assert isinstance(client, BsmClientDevice)

    data = _generate_chargy_data(client,
        start_alias=start_alias,
        end_alias=end_alias,
        read_data=read_data,
        station_serial_number=station_serial_number,
        station_compliance_info=station_compliance_info)
    if data is not None:
        data = json.dumps(data, indent=2).encode('utf-8')
    return data
