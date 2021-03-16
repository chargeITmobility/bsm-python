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




def _generate_chargy_data(client, read_data=True):
    data = None

    # TODO: Provided constants for model aliases.
    common = client.model_aliases[config.COMMON_INSTANCE_ALIAS]
    bsm = client.model_aliases[config.BSM_INSTANCE_ALIAS]
    stons = client.model_aliases['signed_turn_on_snapshot']
    stoffs = client.model_aliases['signed_turn_off_snapshot']

    if read_data:
        common.read_points()
        bsm.read_points()
        stons.read_points()
        stoffs.read_points()

    stons_data = _generate_chargy_snapshot_data(client, common, bsm, stons)
    stoffs_data =_generate_chargy_snapshot_data(client, common, bsm, stoffs)

    if stons_data and stoffs_data:
        data = OrderedDict()

        data['@context'] = 'https://www.chargeit-mobility.com/contexts/charging-station-json-v0'
        # The BSM Python support has no natural unique identifier for a
        # charging process. Let's use an UUID then.
        data['@id'] = str(uuid.uuid4())
        data['placeInfo'] = _generate_chargy_place_info_data(client)
        data['signedMeterValues'] = [stons_data, stoffs_data]

    return data


def _generate_chargy_place_info_data(client):
    info = OrderedDict()

    # Provide some dummy information for testing.
    info['geoLocation'] = {'lat': 48.03552, 'lon': 10.50669}
    info['address'] = {'street': 'Breitenbergstr. 2', 'town': 'Mindelheim', 'zipCode': '87719'}
    info['evseId'] = 'DE*BDO*E8025334492*2'

    return info


def _generate_chargy_snapshot_data(client, common, bsm, snapshot):
    data = None

    snapshot_status = snapshot.points[config.SNAPSHOT_STATUS_DATA_POINT_ID].value

    if snapshot_status == SnapshotStatus.VALID:
        data = OrderedDict()

        meter_id = snapshot.points[config.SNAPSHOT_METER_ADDRESS_1_DATA_POINT_ID].value
        response_counter = snapshot.points[config.SNAPSHOT_RESPONSE_COUNTER_DATA_POINT_ID].value

        data['@context'] = 'https://www.chargeit-mobility.com/contexts/bsm-ws36a-json-v0'
        # Device ID and response counter give a unique ID for a snapshot.
        data['@id'] = '{}-{}'.format(meter_id, response_counter)

        epoch_seconds = snapshot.points[config.SNAPSHOT_EPOCH_TIME_DATA_POINT_ID].value
        timezone_offset_minutes = snapshot.points[config.SNAPSHOT_TIMEZONE_OFFSET_DATA_POINT_ID].value
        local_seconds = None
        if epoch_seconds != None and timezone_offset_minutes != None:
            local_seconds = epoch_seconds + timezone_offset_minutes * 60
        data['timestamp'] = epoch_seconds
        data['timestampLocal'] = {'timestamp': local_seconds, 'localOffset': timezone_offset_minutes}

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

        # Metadata field 1 is expected to hold contract information similar to
        # OCMF.
        data['contract'] = {
                'id': snapshot.points[config.SNAPSHOT_META1_DATA_POINT_ID].value,
                'type': None,
            }

        data['measurementId'] = response_counter
        data['value'] = _generate_chargy_snapshot_value_data(client, snapshot.points[config.SNAPSHOT_REFERENCE_CUMULATIVE_REGISTER_DATA_POINT_ID])

        # Provide snapshot data points except status and signature "in order of
        # their appearance" which is the order for computing the message digest
        # for signing.
        additional_values = []
        for point_id, point in snapshot.points.items():
            if not point_id in _CHARGY_IGNORED_SNAPSHOT_DATA_POINT_IDS:
                additional_values.append(_generate_chargy_snapshot_value_data(client, point))
        data['additionalValues'] = additional_values

        data['signature'] = snapshot.device.repeating_blocks_blob(snapshot).hex()

    return data


def _generate_chargy_snapshot_value_data(client, point):
    measurand = OrderedDict()
    # Provide OBIS ID where available.
    measurand_id = _CHARGY_MEASURAND_ID_BY_SNAPSHOT_DATA_POINT_ID.get(point.point_type.id, None)
    if measurand_id != None:
        measurand['id'] = measurand_id
    measurand['name'] = point.point_type.id

    value = OrderedDict()
    # Provide a scale factor. Either the one explicity given by an associated
    # scale factor data point. Or the default value 10^0 == 1 which the device
    # uses when computing the message digtst for singing.
    scale = None
    if point.sf_point:
        scale = point.sf_point.value_base
    elif point.point_type.type in _CHARGY_NUMERIC_DATA_POINT_TYPES:
        scale = 0
    # Provide a unit. Either the unit explicitly specified by the model or
    # "unitless" indicated by DLMS code 255 (and a JSON null here). The device
    # uses the latter for numeric values which have no explicitly assigned unit
    # when computing the message digest for signing.
    value_unit_name = None
    value_unit_encoded = dlms.DlmsUnits.UNITLESS
    if point.point_type.units != None:
        value_unit_name = _CHARGY_UNIT_NAME_BY_SUNSPEC_UNIT[point.point_type.units]
        value_unit_encoded = dlms.dlms_unit_for_symbol(point.point_type.units)
    value_value = point.value_base
    # SunSpec defines zero as 'not accumulated'/invalid value for accumulators
    # and pySunSpec returns them as None. Let's have a numeric output in this
    # case.
    if point.point_type.type == suns.SUNS_TYPE_ACC32 and point.value_base == None:
        value_value = 0
    value['scale'] = scale
    value['unit'] = value_unit_name
    value['unitEncoded'] = value_unit_encoded
    value['value'] = value_value
    value['valueType'] = _CHARGY_VALUE_TYPE_BY_SUNSPEC_TYPE[point.point_type.type]

    data = OrderedDict()
    data['measurand'] = measurand
    data['measuredValue'] = value
    return data


def generate_chargy_json(client, read_data=True):
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

    data = _generate_chargy_data(client, read_data=read_data)
    if data != None:
        data = json.dumps(data, indent=2).encode('utf-8')
    return data
