# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from . import config
from . import md
from . import util as butil
from ..crypto import util as cutil
from ..sunspec.core import client as sclient
from ..sunspec.core import device as sdevice
from ..sunspec.core import suns
from ..sunspec.core.modbus import client as smodbus
from collections import namedtuple
from enum import IntEnum


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
        _BsmModelInstanceInfo(64901,    'Signed Start Snapshot',                True,   ['signed_start_snapshot', 'sss']),
        _BsmModelInstanceInfo(64901,    'Signed End Snapshot',                  True,   ['signed_end_snapshot', 'ses']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Current Snapshot',         False,  ['ocmf_signed_current_snapshot', 'oscs']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Turn-On Snapshot',         False,  ['ocmf_signed_turn_on_snapshot', 'ostons']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Turn-Off Snapshot',        False,  ['ocmf_signed_turn_off_snapshot', 'ostoffs']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed Start Snapshot',           False,  ['ocmf_signed_start_snapshot', 'osss']),
        _BsmModelInstanceInfo(64903,    'OCMF Signed End Snapshot',             False,  ['ocmf_signed_end_snapshot', 'oses']),
    ]




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

        public_key_regs = bsm.points[config.BSM_PUBLIC_KEY_REGS_DATA_POINT_ID].value
        assert len(bsm.blocks) == public_key_regs + 1
        public_key_data = bsm.device.repeating_blocks_blob(bsm)
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
