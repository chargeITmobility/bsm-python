# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from . import dlms
from . import config
from . import md
from . import util as butil
from ..crypto import util as cutil
from ..sunspec.core import client as sclient
from ..sunspec.core import device as sdevice
from ..sunspec.core import suns
from ..sunspec.core.modbus import client as smodbus
from collections import OrderedDict, namedtuple
from enum import IntEnum
import json
import uuid


_BsmModelInstanceInfo = namedtuple('_BsmModelInstanceInfo', 'id, label, is_snapshot, aliases')


BSM_DEFAULT_BAUDRATE = 19200
BSM_DEFAULT_PARITY = sclient.PARITY_EVEN
BSM_DEFAULT_SLAVE_ID = 42
BSM_DEFAULT_TIMEOUT = 10

SUNSPEC_ID_REGS = 2
SUNSPEC_HEADER_REGS = 2


_BSM_BASE_OFFSET = 40000
_BSM_MODEL_INSTANCES = [
        _BsmModelInstanceInfo(1,        'Common',                               False,  ['common', 'cb']),
        _BsmModelInstanceInfo(10,       'Serial Interface Header',              False,  ['serial_interface_header', 'sih']),
        _BsmModelInstanceInfo(17,       'Serial Interface',                     False,  ['serial_interface', 'si']),
        _BsmModelInstanceInfo(203,      'AC Meter',                             False,  ['ac_meter', 'tpm']),
        _BsmModelInstanceInfo(64900,    'Signing Meter',                        False,  ['bs_meter', 'bsm', 'sm']),
        _BsmModelInstanceInfo(64902,    'Communication Module Firmware Hash',   False,  ['cm_firmware_hash', 'cfwh']),
        _BsmModelInstanceInfo(64901,    'Signed Current Snapshot',              True,   ['signed_current_snapshot', 'scs']),
        _BsmModelInstanceInfo(64901,    'Signed Turn-On Snapshot',              True,   ['signed_turn_on_snapshot', 'stons']),
        _BsmModelInstanceInfo(64901,    'Signed Turn-Off Snapshot',             True,   ['signed_turn_off_snapshot', 'stoffs']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Current Snapshot',         False,   ['ocmf_signed_current_snapshot', 'oscs']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Turn-On Snapshot',         False,   ['ocmf_signed_turn_on_snapshot', 'ostons']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Turn-Off Snapshot',        False,   ['ocmf_signed_turn_off_snapshot', 'ostoffs']),
    ]


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




def _blob_point_value(point):
    value_base = point.value_base

    # Fixup invalid/unimpmlemented uint16 value 0xffff which gets converted to
    # None by pySunSpec. When dealing with blob data we'd like to have the real
    # bits.
    if value_base == None:
        value_base = suns.SUNS_UNIMPL_UINT16

    return point.point_type.to_data(value_base, 2 * point.point_type.len)


class _BlobProxy:
    """
    Proxy for exposing BLOB data from a SunSpecClientDevice convenience
    wrapper.

    This proxy does not read model data. This needs to be done beforehand
    through the model object.
    """
    def __init__(self, device):
        self.device = device


    def __getattr__(self, name):
        model = getattr(self.device, name, None)
        blob = None

        if model != None:
             core_model = model.model
             blob = core_model.device.repeating_blocks_blob(core_model)

        return blob


# TODO: What about initializing the value from the actual model symbols?
class SnapshotType(IntEnum):
    CURRENT = 0
    TURN_ON = 1
    TURN_OFF = 2


# TODO: What about initializing the value from the actual model symbols?
class SnapshotStatus(IntEnum):
    VALID = 0
    INVALID = 1
    UPDATING = 2
    FAILED_GENERAL = 3
    FAILED_NOT_ENABLED = 4
    FAILED_FEEDBACK = 5


class BsmClientDevice(sclient.ClientDevice):
    """
    Attributes:

        aliases_list
            All aliases for the model instnace from models_list at the
            corresponding index.

        model_aliases
            Dictionary mapping model instance aliases to the instances from
            models_list. This includes BSM snapshots.

        snapshots_aliases
            Dictionary mapping model instance aliases of snapshots to the
            instances from models list.
    """
    def __init__(self, device_type=sclient.RTU, slave_id=BSM_DEFAULT_SLAVE_ID,
            name=None, pathlist=None, baudrate=BSM_DEFAULT_BAUDRATE,
            parity=BSM_DEFAULT_PARITY, ipaddr=None,
            ipport=None, timeout=BSM_DEFAULT_TIMEOUT, trace=False,
            max_count=smodbus.REQ_COUNT_MAX):
        super().__init__(device_type, slave_id=slave_id, name=name,
            pathlist=pathlist, baudrate=baudrate, parity=parity,
            ipaddr=ipaddr, ipport=ipport, timeout=timeout, trace=trace,
            max_count=max_count)
        self.aliases_list = []
        self.model_aliases = {}
        self.snapshot_aliases = {}

        self._init_bsm_models()


    def _fixup_curve_name(self, name):
        """
        Returns our canonical curve name in case of an alias. Let's don't
        bother users with this variety.
        """
        if name in config.BSM_CURVE_ALIASES:
            name = config.BSM_CURVE_NAME

        return name


    def _generate_chargy_data(self, read_data=True):
        data = None

        # TODO: Provided constants for model aliases.
        common = self.model_aliases[config.COMMON_INSTANCE_ALIAS]
        bsm = self.model_aliases[config.BSM_INSTANCE_ALIAS]
        stons = self.model_aliases['signed_turn_on_snapshot']
        stoffs = self.model_aliases['signed_turn_off_snapshot']

        if read_data:
            common.read_points()
            bsm.read_points()
            stons.read_points()
            stoffs.read_points()

        stons_data = self._generate_chargy_snapshot_data(common, bsm, stons)
        stoffs_data = self._generate_chargy_snapshot_data(common, bsm, stoffs)

        if stons_data and stoffs_data:
            data = OrderedDict()

            data['@context'] = 'https://www.chargeit-mobility.com/contexts/charging-station-json-v0'
            # The BSM Python support has no natural unique identifier for a
            # charging process. Let's use an UUID then.
            data['@id'] = str(uuid.uuid4())
            data['placeInfo'] = self._generate_chargy_place_info_data()
            data['signedMeterValues'] = [stons_data, stoffs_data]

        return data


    def _generate_chargy_place_info_data(self):
        info = OrderedDict()

        # Provide some dummy information for testing.
        info['geoLocation'] = {'lat': 48.03552, 'lon': 10.50669}
        info['address'] = {'street': 'Breitenbergstr. 2', 'town': 'Mindelheim', 'zipCode': '87719'}
        info['evseId'] = 'DE*BDO*E8025334492*2'

        return info


    def _generate_chargy_snapshot_data(self, common, bsm, snapshot):
        data = None

        snapshot_status = snapshot.points[config.SNAPSHOT_STATUS_DATA_POINT_ID].value

        if snapshot_status == SnapshotStatus.VALID:
            data = OrderedDict()

            meter_id = bsm.points[config.BSM_METER_ADDRESS_1_DATA_POINT_ID].value
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
                    'publicKey': self.get_public_key(read_data=False).hex(),
                    'meterId': meter_id,
                    'manufacturer': common.points[config.COMMON_MANUFACTURER_DATA_POINT_ID].value,
                    'type': common.points[config.COMMON_MODEL_DATA_POINT_ID].value,
                }

            # Metadata field 1 is expected to hold contract information similar
            # to OCMF.
            data['contract'] = {
                    'id': snapshot.points[config.SNAPSHOT_META1_DATA_POINT_ID].value,
                    'type': 'UNDEFINED',
                }

            data['measurementId'] = response_counter
            data['value'] = self._generate_chargy_snapshot_value_data(snapshot.points[config.SNAPSHOT_REFERENCE_CUMULATIVE_REGISTER_DATA_POINT_ID])

            # Provide snapshot data points except status and signature "in
            # order of their appearance" which is the order for computing the
            # message digest for signing.
            additional_values = []
            for point_id, point in snapshot.points.items():
                if not point_id in _CHARGY_IGNORED_SNAPSHOT_DATA_POINT_IDS:
                    additional_values.append(self._generate_chargy_snapshot_value_data(point))
            data['additionalValues'] = additional_values

            data['signature'] = snapshot.device.repeating_blocks_blob(snapshot).hex()

        return data


    def _generate_chargy_snapshot_value_data(self, point):

        measurand = OrderedDict()
        # Provide OBIS ID where available.
        measurand_id = _CHARGY_MEASURAND_ID_BY_SNAPSHOT_DATA_POINT_ID.get(point.point_type.id, None)
        if measurand_id != None:
            measurand['id'] = measurand_id
        measurand['name'] = point.point_type.id

        value = OrderedDict()
        # Provide a scale factor. Either the one explicity given by an
        # associated scale factor data point. Or the default value 10^0 == 1
        # which the device uses when computing the message digtst for singing.
        scale = None
        if point.sf_point:
            scale = point.sf_point.value_base
        elif point.point_type.type in _CHARGY_NUMERIC_DATA_POINT_TYPES:
            scale = 0
        # Provide a unit. Either the unit explicitly specified by the model or
        # "unitless" indicated by DLMS code 255 (and a JSON null here). The
        # device uses the latter for numeric values which have no explicitly
        # assigned unit when computing the message digest for signing.
        value_unit_name = None
        value_unit_encoded = dlms.DlmsUnits.UNITLESS
        if point.point_type.units != None:
            value_unit_name = _CHARGY_UNIT_NAME_BY_SUNSPEC_UNIT[point.point_type.units]
            value_unit_encoded = dlms.dlms_unit_for_symbol(point.point_type.units)
        value_value = point.value_base
        # SunSpec defines zero as 'not accumulated'/invalid value for
        # accumulators and pySunSpec returns them as None. Let's have a numeric
        # output in this case.
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


    def _init_bsm_models(self):
        """
        Initializes BSM models for the known layout for this device. This saves
        the time for scanning the device.
        """
        address = _BSM_BASE_OFFSET + SUNSPEC_ID_REGS + SUNSPEC_HEADER_REGS

        for info in _BSM_MODEL_INSTANCES:
            model = sclient.ClientModel(self, info.id, addr=address, mlen=0)
            model.load()

            self.add_model(model)
            self.aliases_list.append(info.aliases)

            # Provide model instances as well by name. The BSM snapshots use
            # all the same model and a name comes in quite handy for referring
            # to them.
            self._register_aliases(self.model_aliases, info.aliases, model)
            if info.is_snapshot:
                self._register_aliases(self.snapshot_aliases, info.aliases, model)

            address += model.len + SUNSPEC_HEADER_REGS


    def _register_aliases(self, dictionary, aliases, model):
        for alias in aliases:
            dictionary[alias] = model


    def create_snapshot(self, alias):
        snapshot = self.snapshot_aliases[alias]
        status = snapshot.points[config.SNAPSHOT_STATUS_DATA_POINT_ID]

        status.value = SnapshotStatus.UPDATING
        status.write()


    def generate_chargy_json(self, read_data=True):
        """
        Generates a chargeIT mobility JSON document from signed turn-on and
        turn-off snapshots.

        The JSON document will be UTF-8 encoded. In case that one of the
        snapshots is not valid, None will be returned.
        """
        data = self._generate_chargy_data(read_data=read_data)
        if data != None:
            data = json.dumps(data, indent=2).encode('utf-8')
        return data


    def generate_ocmf_xml(self, read_data=True):
        """
        Generates an OCMF XML document from signed turn-on and turn-off
        snapshots.

        The XML document gets returned as byte data for declaring and using
        identical encoding. In case that one of the snapshots is not valid,
        None will be returned.
        """
        bsm = self.model_aliases['bs_meter']
        ostons = self.model_aliases['ocmf_signed_turn_on_snapshot']
        ostoffs = self.model_aliases['ocmf_signed_turn_off_snapshot']
        result = None

        if read_data:
            bsm.read_points()
            ostons.read_points()
            ostoffs.read_points()

        ostons_status = ostons.points[config.OCMF_STATUS_DATA_POINT_ID].value
        ostons_data = ostons.points[config.OCMF_DATA_DATA_POINT_ID].value
        ostoffs_status = ostoffs.points[config.OCMF_STATUS_DATA_POINT_ID].value
        ostoffs_data = ostoffs.points[config.OCMF_DATA_DATA_POINT_ID].value

        if ostons_status == SnapshotStatus.VALID \
            and ostoffs_status == SnapshotStatus.VALID:

            # Don't read BSM model instance containing the public key data
            # again. If requested, this has been done above.
            der = self.get_public_key(read_data=False).hex()

            template = \
                '<?xml version="1.0" encoding="{encoding}" standalone="yes"?>\n' \
                '<values>\n' \
                '  <value transactionId="1" context="Transaction.Begin">\n' \
                '    <signedData format="OCMF" encoding="plain">{ostons}</signedData>\n' \
                '    <publicKey encoding="plain">{pk}</publicKey>\n' \
                '  </value>\n' \
                '  <value transactionId="1" context="Transaction.End">\n' \
                '    <signedData format="OCMF" encoding="plain">{ostoffs}</signedData>\n' \
                '    <publicKey encoding="plain">{pk}</publicKey>\n' \
                '  </value>\n' \
                '</values>\n'

            values = {
                    # XML seems to define encoding names to be upper-case.
                    'encoding': config.PYSUNSPEC_STRING_ENCODING.upper(),
                    'pk': der,
                    'ostons': ostons_data,
                    'ostoffs': ostoffs_data,
                }

            # Generate data in the same encoding as pySunSpec's fixed one as
            # string data got set and signed in this one.
            result = template.format(**values).encode(config.PYSUNSPEC_STRING_ENCODING)

        return result


    def get_public_key(self, read_data=True, output_format='der'):
        bsm = self.model_aliases[config.BSM_INSTANCE_ALIAS]
        result = None

        if read_data:
            bsm.read_points()

        if self.has_repeating_blocks_blob_layout(bsm):
            public_key = self.repeating_blocks_blob(bsm)
            result = cutil.public_key_data_from_blob(public_key, config.BSM_MESSAGE_DIGEST, output_format=output_format)

        return result


    def get_snapshot(self, alias):
        snapshot = self.snapshot_aliases[alias]
        status = snapshot.points[config.SNAPSHOT_STATUS_DATA_POINT_ID]

        self.create_snapshot(alias)

        snapshot.read_points()
        while status.value == SnapshotStatus.UPDATING:
            snapshot.read_points()

        if status.value == SnapshotStatus.VALID:
            return snapshot
        else:
            return None


    def has_repeating_blocks_blob_layout(self, model):
        """
        Returns whether the repeating blocks of the given model are likely to
        contain BLOB data.
        """
        result = False

        # The repeating blocks are likely to contain a BLOB if they contain a
        # single uint16 element without unit symbol and scale factor.
        if len(model.blocks) > 1:
            first_repeating = model.blocks[1]
            if len(first_repeating.points_list) == 1:
                repeating_point = first_repeating.points_list[0]
                repeating_type = repeating_point.point_type

                result = repeating_type.type == suns.SUNS_TYPE_UINT16 \
                    and repeating_type.units == None \
                    and repeating_type.sf == None

        return result


    def lookup_model(self, name):
        """
        Case-insensitively looks up a model by the given name or alias.
        """
        model = next(filter(lambda x: x.model_type.name.lower() == name.lower(),
            self.models_list), None)

        if not model:
            model = butil.dict_get_case_insensitive(self.model_aliases, name)

        return model


    def lookup_model_and_point(self, model_name, point_id):
        """
        Case-insensitively looks up a data point along with its model by the
        given point name and model name or alias.
        """
        model = self.lookup_model(model_name)
        point = None

        if model:
            point = self.lookup_point_in_model(model, point_id)

        return (model, point)


    def lookup_point_in_model(self, model, point_id):
        """
        Case-insensitively looks up a data point by its name in the given
        model.
        """
        return next(filter(lambda x: x.point_type.id.lower() == point_id.lower(),
            model.points_list), None)


    def lookup_snapshot(self, name):
        """
        Case-insensitively looks up a snapshot model by the given name or
        alias.
        """
        return dict_get_case_insensitive(self.snapshot_aliases, name)


    def model_instance_label(self, model):
        """
        Returns a label for the given model instance.
        """
        for index, current_model in enumerate(self.models_list):
            if model == current_model:
                return _BSM_MODEL_INSTANCES[index].label


    # I did not find a mechanism for conveniently reading BLOB data from
    # repeating blocks in pySunSpec.
    #
    # TODO: If BLOBs provided via repeated blocks is the default mechanism for
    # binary data, What about integrating this support into Model or
    # DeviceModel?
    def repeating_blocks_blob(self, model):
        """
        Collects BLOB data from the repeating blocks of the given model.

        The same result could be achieved by just reading the data directly from
        the client device by ClientDevice.read. This functions collects already
        read data (scattered in the individual data points) to avoid the more
        time-consuming read from the client device.

        Returns:
            The BLOB data as byte string or None, if there is no BLOB data.
        """
        result = None

        if self.has_repeating_blocks_blob_layout(model):
            repeating = model.blocks[1:]
            points = map(lambda b: b.points_list[0], repeating)
            data = map(_blob_point_value, points)
            result = b''.join(data)

        # Trim blob data if an explicit length is given by the model.
        blob_bytes = self.repeating_blocks_blob_explicit_length_bytes(model)
        if blob_bytes != None:
            result = result[:blob_bytes]

        return result


    def repeating_blocks_blob_explicit_length_bytes(self, model):
        """
        Returns the explicit BLOB data length (in bytes) if a model has an
        appropriate data point. This needs to be an uint16 data point named
        'Bx' when the repeating block data point is named 'x'.
        """
        result = None

        blob_id = self.repeating_blocks_blob_id(model)
        bytes_id = 'B' + blob_id
        bytes_point = model.blocks[0].points.get(bytes_id, None)

        if bytes_point:
            bytes_type = bytes_point.point_type

            if bytes_point and bytes_type.type == suns.SUNS_TYPE_UINT16 \
                and bytes_type.units == None \
                and bytes_type.sf == None:
                result = bytes_point.value

        return result


    def repeating_blocks_blob_id(self, model):
        """
        Returns the BLOB data point ID from the repeating blocks of the given
        model.

        Returns:
            The data point ID or None, if there is no BLOB data.
        """
        result = None

        if self.has_repeating_blocks_blob_layout(model):
            result =  model.blocks[1].points_list[0].point_type.id

        return result


    def verify_snapshot(self, alias, read_data=True, trace=None):
        """
        Verifies snapshot data for the given alias.

        By default both, the BSM model containing the public key and the
        snapshot are read before verification.
        """
        result = False

        bsm = self.model_aliases[config.BSM_INSTANCE_ALIAS]
        snapshot = self.snapshot_aliases[alias]

        if read_data:
            bsm.read_points()
            snapshot.read_points()

        public_key_data = self.get_public_key(read_data=False)
        public_key = cutil.public_key_from_blob(public_key_data, config.BSM_MESSAGE_DIGEST)
        curve_name = self._fixup_curve_name(public_key.curve.name)
        signature_regs = snapshot.points[config.SNAPSHOT_SIGNATURE_REGS_DATA_POINT_ID].value
        assert len(snapshot.blocks) == signature_regs + 1
        signature = snapshot.device.repeating_blocks_blob(snapshot)

        if trace:
            trace('Verifying {} ...'.format(snapshot.model_type.id))
            trace('Curve: {}'.format(curve_name))
            trace('Public key: {}'.format(public_key_data.hex()))
            trace('Signature: {}'.format(signature.hex()))

        if len(public_key_data) == 0:
            if trace:
                trace('Failed. Device has no public key.')
            result = False
        elif len(signature) == 0:
            if trace:
                trace('Failed. Snapshot contains no signature.')
            result = False
        else:
            assert curve_name == config.BSM_CURVE_NAME

            if trace:
                trace('Computing SHA-256 digest for snapshot data:')
            digest = md.md_for_snapshot_data(snapshot, trace=trace)
            if trace:
                trace('Snapshot data SHA-256 digest: {}'.format(digest.hex()))

            if cutil.verify_signed_digest(public_key_data, config.BSM_MESSAGE_DIGEST, signature, digest):
                if trace:
                    trace('Success.')
                result = True
            else:
                if trace:
                    trace('Failed.')
                result = False

        return result




class SunSpecBsmClientDevice(sclient.SunSpecClientDeviceBase):
    """
    BsmClientDevice convenience wrapper for scripting, unit testing, and many
    more.

    In addition to the model attributes from SunSpecClientDeviceBase, it also
    provides attributes for the model instance aliases from BsmClientDevice.
    """
    def __init__(self, device_type=sclient.RTU, slave_id=BSM_DEFAULT_SLAVE_ID, name=None,
            pathlist = None, baudrate=BSM_DEFAULT_BAUDRATE,
            parity=BSM_DEFAULT_PARITY, ipaddr=None, ipport=None,
            timeout=BSM_DEFAULT_TIMEOUT, trace=False, scan_progress=None,
            scan_delay=None, max_count=smodbus.REQ_COUNT_MAX):
        device = BsmClientDevice(device_type, slave_id, name, pathlist,
            baudrate, parity, ipaddr, ipport, timeout, trace, max_count)
        super(self.__class__, self).__init__(device)

        # Also provide attributes for model aliases.
        self._add_alias_attributes()

        # Also provide convenient access to BLOBs (from models and aliases).
        setattr(self, 'blobs', _BlobProxy(self))


    def _snapshot_alias(self, snapshot):
        alias = None

        for a, m in self.device.snapshot_aliases.items():
            if m is snapshot.model:
                alias = a
                break

        return alias


    def _add_alias_attributes(self):
        """
        Registers the attribute model instances under the aliases given by the
        client as well.
        """
        for index, model in enumerate(self.device.models_list):
            aliases = self.device.aliases_list[index]
            if aliases:
                attribute_model = self._get_attribute_model(model)
                for alias in aliases:
                    setattr(self, alias, attribute_model)


    def _get_attribute_model(self, model):
        """
        "Scrapes" corresponding attribute model instance from this object's
        attributes. This is done because there is no list of them (by now).
        """
        models = getattr(self, model.model_type.name)
        result = None

        if  type(models) is list:
            # Pick the corresponding attribute model instance from the list in
            # case of multiple instances of the same model.
            result = next(filter(lambda x: x != None and x.model == model, models), None)
        else:
            result = models

        return result


    def create_snapshot(self, snapshot):
        alias = self._snapshot_alias(snapshot)
        self.device.create_snapshot(alias)


    def generate_chargy_json(self, read_data=True):
        return self.device.generate_chargy_json(read_data=read_data)


    def generate_ocmf_xml(self, read_data=True):
        return self.device.generate_ocmf_xml(read_data=read_data)


    def get_public_key(self, output_format='der'):
        return self.device.get_public_key(output_format=output_format)


    def get_snapshot(self, snapshot):
        alias = self._snapshot_alias(snapshot)
        result = None

        if self.device.get_snapshot(alias) != None:
            # If the wrapped device returs something we were successful. Return
            # the wrapped snapshot model whose underlying model has been
            # updated.
            result = snapshot

        return result


    def verify_snapshot(self, snapshot, read_data=True, trace=None):
        """
        Verifies snapshot data for the given SunSpecClientModelBase instance.

        By default both, the BSM model containing the public key and the
        snapshot are read before verification.
        """
        alias = self._snapshot_alias(snapshot)
        result = False

        if alias != None:
            result = self.device.verify_snapshot(alias, read_data=read_data, trace=trace)

        return result
