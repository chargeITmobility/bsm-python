#!/usr/bin/env python3


from . import version
from ..crypto.curves import SECP256r1
from ..crypto.util import verify_signed_digest
from ..sunspec.client import SunspecClient, SunspecBuilder
from ..sunspec.constants import CommonBlockOffsets, SerialInterfaceOffsets, SunspecModel, SunspecOffsets, SunspecIdentifier, SunspecDefaultValue, SunspecModelPayloadLengths
from argparse import ArgumentParser
from collections import namedtuple
from enum import IntEnum
from hashlib import sha256
from hexdump import hexdump
from operator import attrgetter
from pprint import pprint, pformat
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.register_write_message import WriteMultipleRegistersResponse
from six import iteritems
from struct import pack

import binascii
import os
import pkg_resources
import string
import sys


MODEL_DATA_INDENT = '    '


SunspecModelData = namedtuple('SunspecModelData',
    [
        'model_id',
        'length',
        'payload',
    ])
Timestamp = namedtuple('Timestamp', 'operating_seconds, epoch_time_utc_seconds, local_timezone_offset_minutes')
TimeSetInfo = namedtuple('TimeSetInfo', 'counter operating_seconds')
CommonBlockData = namedtuple('CommonBlockData',
    [
        'manufacturer',
        'model',
        'options',
        'version',
        'serial_number',
        'device_address',
        'padding',
    ])
InterfaceHeaderData = namedtuple('InterfaceHeaderData', 'status control type padding')
SerialInterfaceData = namedtuple('SerialInterfaceData',
    [
        'name',
        'baud_rate',
        'bits',
        'parity',
        'duplex',
        'flow_control',
        'interface_type',
        'protocol'
    ])
ThreePhaseMeterData = namedtuple('ThreePhaseMeterData',
    [
        'current_total',
        'current_l1',
        'current_l2',
        'current_l3',
        'scale_factor_current',
        'voltage',
        'voltage_l1',
        'voltage_l2',
        'voltage_l3',
        'voltage_ll',
        'voltage_l1_l2',
        'voltage_l2_l3',
        'voltage_l3_l1',
        'scale_factor_voltage',
        'frequency',
        'scale_factor_frequency',
        'active_power_total',
        'active_power_l1',
        'active_power_l2',
        'active_power_l3',
        'scale_factor_active_power',
        'apparent_power_total',
        'apparent_power_l1',
        'apparent_power_l2',
        'apparent_power_l3',
        'scale_factor_apparent_power',
        'reactive_power_total',
        'reactive_power_l1',
        'reactive_power_l2',
        'reactive_power_l3',
        'scale_factor_reactive_power',
        'power_factor',
        'power_factor_l1',
        'power_factor_l2',
        'power_factor_l3',
        'scale_factor_power_factor',
        'active_energy_exported_total',
        'active_energy_exported_l1',
        'active_energy_exported_l2',
        'active_energy_exported_l3',
        'active_energy_imported_total',
        'active_energy_imported_l1',
        'active_energy_imported_l2',
        'active_energy_imported_l3',
        'scale_factor_active_energy',
        'apparent_energy_exported_total',
        'apparent_energy_exported_l1',
        'apparent_energy_exported_l2',
        'apparent_energy_exported_l3',
        'apparent_energy_imported_total',
        'apparent_energy_imported_l1',
        'apparent_energy_imported_l2',
        'apparent_energy_imported_l3',
        'scale_factor_apparent_energy',
        'reactive_energy_imported_q1_total',
        'reactive_energy_imported_q1_l1',
        'reactive_energy_imported_q1_l2',
        'reactive_energy_imported_q1_l3',
        'reactive_energy_imported_q2_total',
        'reactive_energy_imported_q2_l1',
        'reactive_energy_imported_q2_l2',
        'reactive_energy_imported_q2_l3',
        'reactive_energy_exported_q3_total',
        'reactive_energy_exported_q3_l1',
        'reactive_energy_exported_q3_l2',
        'reactive_energy_exported_q3_l3',
        'reactive_energy_exported_q4_total',
        'reactive_energy_exported_q4_l1',
        'reactive_energy_exported_q4_l2',
        'reactive_energy_exported_q4_l3',
        'scale_factor_reactive_energy',
        'events',
    ])
SigningMeterData = namedtuple('SigningMeterData',
    [
        'error_code',
        'serial_number_meter',
        'serial_number_communication_module',
        'software_version_meter',
        'software_version_communication_module',
        'meter_address_1',
        'meter_address_2',
        'reference_cumulative_register',
        'scale_factor_reference_cumulative_register',
        'power_down_counter',
        'response_counter',
        'current_time',
        'time_set',
        'di_state',
        'do_state',
        'last_di_modification',
        'last_do_modification',
        'metadata_1',
        'metadata_2',
        'metadata_3',
        'ecdsa_curve_name',
        'ecdsa_public_key',
    ])
SignedStateData = namedtuple('SignedStateData',
    [
        'type',
        'status',
        'active_energy_exported_total',
        'active_energy_exported_total_scale_factor',
        'active_power_total',
        'active_power_total_scale_factor',
        'server_id',
        'response_counter',
        'timestamp',
        'time_set',
        'di_state',
        'do_state',
        'last_di_modification',
        'last_do_modification',
        'metadata_1',
        'metadata_2',
        'metadata_3',
        'signature',
    ])


BlockInfo = namedtuple('BlockInfo', 'name, short_name, model, offset, length, is_snapshot')


class ReadableValue:
    def __init__(self, arg_name, offset, length, parser):
        self.arg_name = arg_name
        self.offset = offset
        self.length = length
        self.parser = parser

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'ReadableValue(\'{}\', {}, {})'.format(self.arg_name, self.offset, self.length)

    def get_arg(self, args):
        result = None

        if hasattr(args, self.arg_name):
            result = getattr(args, self.arg_name)

        return result

    def parse_registers(self, decoder):
        return self.parser(decoder)


class WriteableValue(ReadableValue):
    def __init__(self, arg_name, offset, length, parser, generator):
        super().__init__(arg_name, offset, length, parser)
        self.generator = generator

    def __str__(self):
        return 'WriteableValue(\'{}\', {}, {}, ...)'.format(self.arg_name, self.offset, self.length)

    def generate_registers(self, builder, args):
        return self.generator(builder, getattr(args, self.arg_name))


WriteJob = namedtuple('WriteJob', 'offset registers')



# --------------------------------------------------------------------------- # 
# Signing Meter Common Constants
# --------------------------------------------------------------------------- # 
class SigningMeterOffsets(IntEnum):
    SunSpecId                                = 40000
    CommonBlock                              = 40002
    SerialInterfaceHeaderBlock               = 40070
    SerialInterfaceBlock                     = 40076
    ThreePhaseMeterBlock                     = 40090
    SigningMeterBlock                        = 40197
    SignedCurrentStateBlock                  = 40495
    SignedTurnOnStateBlock                   = 40745
    SignedTurnOffStateBlock                  = 40995
    EndOfSunSpecMapBlock                     = 41245


class SigningMeterModels(IntEnum):
    SigningMeter                             = SunspecModel.VendorPrivateStart + 0
    SignedState                              = SunspecModel.VendorPrivateStart + 1


class SigningMeterModelPayloadLengths(IntEnum):
    SigningMeter                             = 296
    SignedState                              = 248


class SigningMeterLengths(IntEnum):
    CommonBlock                              = SunspecModelPayloadLengths.CommonBlock + SunspecOffsets.HeaderLength
    SerialInterfaceHeaderBlock               = SunspecModelPayloadLengths.InterfaceHeader + SunspecOffsets.HeaderLength
    SerialInterfaceBlock                     = SunspecModelPayloadLengths.SerialInterface + SunspecOffsets.HeaderLength
    ThreePhaseMeterBlock                     = SunspecModelPayloadLengths.ThreePhaseMeter + SunspecOffsets.HeaderLength
    SigningMeterBlock                        = SigningMeterModelPayloadLengths.SigningMeter + SunspecOffsets.HeaderLength
    SignedCurrentStateBlock                  = SigningMeterModelPayloadLengths.SignedState + SunspecOffsets.HeaderLength
    SignedTurnOnStateBlock                   = SigningMeterModelPayloadLengths.SignedState + SunspecOffsets.HeaderLength
    SignedTurnOffStateBlock                  = SigningMeterModelPayloadLengths.SignedState + SunspecOffsets.HeaderLength


class SigningMeterBlockOffsets(IntEnum):
    ErrorCodeLength                          = 4
    SerialNumberMeterLength                  = 8
    SerialNumberCommunicationModuleLength    = 8
    SoftwareVersionMeterLength               = 8
    SoftwareVersionCommunicationModuleLength = 8
    MeterAddress1Length                      = 8
    MeterAddress2Length                      = 8
    EpochTimeUtcSeconds                      = 63
    EpochTimeUtcSecondsLength                = 2
    LocalTimezoneOffsetMinutes               = 65
    LocalTimezoneOffsetMinutesLength         = 1
    TimeSetCounter                           = 66
    TimeSetCounterLength                     = 2
    TimeSetAt                                = 68
    TimeSetAtLength                          = 2
    DigitalInputState                        = 70
    DigitalInputStateLength                  = 1
    DigitalOutputState                       = 71
    DigitalOutputStateLength                 = 1
    Metadata1                                = 82
    Metadata1Length                          = 70
    Metadata2                                = 152
    Metadata2Length                          = 50
    Metadata3                                = 202
    Metadata3Length                          = 50
    EcdsaCurveNameLength                     = 8
    EcdsaPublicKeyLength                     = 37


# TODO: Complete block information. What about splitting into offsets and
# lengths?
class SignedStateBlockOffsets(object):
    Status                                   = 3
    StatusLength                             = 1
    ServerId                                 = 12
    ServerIdLength                           = 8
    Metadata1Length                          = SigningMeterBlockOffsets.Metadata1Length
    Metadata2Length                          = SigningMeterBlockOffsets.Metadata2Length
    Metadata3Length                          = SigningMeterBlockOffsets.Metadata3Length
    SignatureLength                          = 37


class SignedStateBlockStatus(IntEnum):
    VALID = 0
    INVALID = 1
    UPDATING = 2
    FAILED = 3


class DlmsUnits(IntEnum):
    MINUTES = 6
    SECONDS = 7
    WATTS = 27
    WATT_HOURS = 30
    UNITLESS = 255


# --------------------------------------------------------------------------- #
# Block Information
# --------------------------------------------------------------------------- #

BLOCK_INFOS = \
    [
        BlockInfo(
            'Common Block',
            'cb',
            SunspecModel.CommonBlock,
            SigningMeterOffsets.CommonBlock,
            SigningMeterLengths.CommonBlock,
            False),
        BlockInfo(
            'Serial Interface Header',
            'sih',
            SunspecModel.InterfaceHeader,
            SigningMeterOffsets.SerialInterfaceHeaderBlock,
            SigningMeterLengths.SerialInterfaceHeaderBlock,
            False),
        BlockInfo(
            'Serial Interface',
            'si',
            SunspecModel.SerialInterface,
            SigningMeterOffsets.SerialInterfaceBlock,
            SigningMeterLengths.SerialInterfaceBlock,
            False),
        BlockInfo(
            'Three Phase Meter',
            'tpm',
            SunspecModel.ThreePhaseMeter,
            SigningMeterOffsets.ThreePhaseMeterBlock,
            SigningMeterLengths.ThreePhaseMeterBlock,
            False),
        BlockInfo(
            'Signing Meter',
            'sm',
            SigningMeterModels.SigningMeter,
            SigningMeterOffsets.SigningMeterBlock,
            SigningMeterLengths.SigningMeterBlock,
            False),
        BlockInfo(
            'Signed Current State',
            'scs',
            SigningMeterModels.SignedState,
            SigningMeterOffsets.SignedCurrentStateBlock,
            SigningMeterLengths.SignedCurrentStateBlock,
            True),
        BlockInfo(
            'Signed Turn-On State',
            'stons',
            SigningMeterModels.SignedState,
            SigningMeterOffsets.SignedTurnOnStateBlock,
            SigningMeterLengths.SignedTurnOnStateBlock,
            True),
        BlockInfo(
            'Signed Turn-Off State',
            'stoffs',
            SigningMeterModels.SignedState,
            SigningMeterOffsets.SignedTurnOffStateBlock,
            SigningMeterLengths.SignedTurnOffStateBlock,
            True),
    ]


READ_ONLY_VALUES = \
    sorted([
        ReadableValue('time_set_counter',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.TimeSetCounter,
            SigningMeterBlockOffsets.TimeSetCounterLength,
            lambda decoder: decoder.decode_32bit_uint()),
        ReadableValue('time_set_at',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.TimeSetAt,
            SigningMeterBlockOffsets.TimeSetAtLength,
            lambda decoder: decoder.decode_32bit_uint()),
        ReadableValue('digital_input',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.DigitalInputState,
            SigningMeterBlockOffsets.DigitalInputStateLength,
            lambda decoder: decoder.decode_16bit_uint()),
    ], key=attrgetter('offset'))


WRITEABLE_VALUES = \
    sorted([
        WriteableValue('device_address',
            SigningMeterOffsets.CommonBlock + CommonBlockOffsets.DeviceAddress,
            CommonBlockOffsets.DeviceAddressLength,
            lambda decoder: decoder.decode_16bit_uint(),
            lambda builder, arg: builder.add_16bit_uint(arg)),
        WriteableValue('baud_rate',
            SigningMeterOffsets.SerialInterfaceBlock + SerialInterfaceOffsets.BaudRate,
            SerialInterfaceOffsets.BaudRateLength,
            lambda decoder: decoder.decode_32bit_uint(),
            lambda builder, arg: builder.add_32bit_uint(arg)),
        WriteableValue('epoch_time',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.EpochTimeUtcSeconds,
            SigningMeterBlockOffsets.EpochTimeUtcSecondsLength,
            lambda decoder: decoder.decode_32bit_uint(),
            lambda builder, arg: builder.add_32bit_uint(arg)),
        WriteableValue('tz_offset',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.LocalTimezoneOffsetMinutes,
            SigningMeterBlockOffsets.LocalTimezoneOffsetMinutesLength,
            lambda decoder: decoder.decode_16bit_int(),
            lambda builder, arg: builder.add_16bit_int(arg)),
        WriteableValue('digital_output',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.DigitalOutputState,
            SigningMeterBlockOffsets.DigitalOutputStateLength,
            lambda decoder: decoder.decode_16bit_uint(),
            lambda builder, arg: builder.add_16bit_uint(arg)),
        WriteableValue('meta_1',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.Metadata1,
            SigningMeterBlockOffsets.Metadata1Length,
            lambda decoder: decoder.decode_string(2 * SigningMeterBlockOffsets.Metadata1Length),
            lambda builder, arg: builder.add_string(arg, 2 * SigningMeterBlockOffsets.Metadata1Length)),
        WriteableValue('meta_2',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.Metadata2,
            SigningMeterBlockOffsets.Metadata2Length,
            lambda decoder: decoder.decode_string(2 * SigningMeterBlockOffsets.Metadata2Length),
            lambda builder, arg: builder.add_string(arg, 2 * SigningMeterBlockOffsets.Metadata2Length)),
        WriteableValue('meta_3',
            SigningMeterOffsets.SigningMeterBlock + SigningMeterBlockOffsets.Metadata3,
            SigningMeterBlockOffsets.Metadata3Length,
            lambda decoder: decoder.decode_string(2 * SigningMeterBlockOffsets.Metadata3Length),
            lambda builder, arg: builder.add_string(arg, 2 * SigningMeterBlockOffsets.Metadata3Length)),
        WriteableValue('scs_status',
            SigningMeterOffsets.SignedCurrentStateBlock + SignedStateBlockOffsets.Status,
            SignedStateBlockOffsets.StatusLength,
            lambda decoder: decoder.decode_16bit_uint(),
            lambda builder, arg: builder.add_16bit_uint(arg)),
        WriteableValue('stons_status',
            SigningMeterOffsets.SignedTurnOnStateBlock + SignedStateBlockOffsets.Status,
            SignedStateBlockOffsets.StatusLength,
            lambda decoder: decoder.decode_16bit_uint(),
            lambda builder, arg: builder.add_16bit_uint(arg)),
        WriteableValue('stoffs_status',
            SigningMeterOffsets.SignedTurnOffStateBlock + SignedStateBlockOffsets.Status,
            SignedStateBlockOffsets.StatusLength,
            lambda decoder: decoder.decode_16bit_uint(),
            lambda builder, arg: builder.add_16bit_uint(arg)),
    ], key=attrgetter('offset'))


ALL_VALUES = sorted(READ_ONLY_VALUES + WRITEABLE_VALUES, key=attrgetter('offset'))


# --------------------------------------------------------------------------- # 
# Common Functions
# --------------------------------------------------------------------------- # 
def auto_int(x):
    result = None

    if isinstance(x, int):
        # Pass-through integer values.
        result = x
    elif x != None:
        # Parse everything else but 'None' with auto base detection.
        result = int(x, 0)

    return result


def block_info_for_short_name(short_name):
    filtered = filter(lambda x: x.short_name == short_name, BLOCK_INFOS)
    result = next(filtered, None)

    # We expect at most one match.
    assert next(filtered, None) == None

    return result


def check_write_result(result):
    if isinstance(result, WriteMultipleRegistersResponse):
        # Nothing to see here ...
        pass
    else:
        print('Writing registers failed ({}).'.format(result), file=sys.stderr)
        sys.exit(1)


def create_sunspec_sync_client(args):
    """ A quick helper method to create a sunspec
    client.

    :param args: command line arguments parsed by ArgumentParser
    :returns: an initialized SunspecClient
    """
    modbus = ModbusSerialClient(method='rtu', port=args.device, timeout=args.timeout, baudrate=args.baud, parity='E', strict=(not args.relax))
    modbus.connect()
    client = SunspecClient(modbus, unit=args.unit, chunk_size=args.chunk_size)
    # No need for calling client.initialize() as this checks the SunSpec ID and
    # sets up an offset we are not relying on.
    return client


def decode_binary_string(decoder, size):
    length = decoder.decode_16bit_uint()
    string = decoder.decode_binary_string(size=size)

    assert length <= size
    return string[:length]


def decode_block_payload(decoder, model_id, length):
    result = None

    if model_id == SunspecModel.CommonBlock and length == SunspecModelPayloadLengths.CommonBlock:
        result = CommonBlockData(
                manufacturer=decoder.decode_string(size=2 * CommonBlockOffsets.ManufacturerLength),
                model=decoder.decode_string(size=2 * CommonBlockOffsets.ModelLength),
                options=decoder.decode_string(size=2 * CommonBlockOffsets.OptionsLength),
                version=decoder.decode_string(size=2 * CommonBlockOffsets.VersionLength),
                serial_number=decoder.decode_string(size=2 * CommonBlockOffsets.SerialNumberLength),
                device_address=decoder.decode_16bit_uint(),
                padding=decoder.decode_16bit_uint(),
            )
    elif model_id == SunspecModel.InterfaceHeader and length == SunspecModelPayloadLengths.InterfaceHeader:
        result = InterfaceHeaderData(
            status=decoder.decode_16bit_uint(),
            control=decoder.decode_16bit_uint(),
            type=decoder.decode_16bit_uint(),
            padding=decoder.decode_16bit_uint(),
        )
    elif model_id == SunspecModel.SerialInterface and length == SunspecModelPayloadLengths.SerialInterface:
        result = SerialInterfaceData(
            name=decoder.decode_string(size=2 * SerialInterfaceOffsets.NameLength),
            baud_rate=decoder.decode_32bit_uint(),
            bits=decoder.decode_16bit_uint(),
            parity=decoder.decode_16bit_uint(),
            duplex=decoder.decode_16bit_uint(),
            flow_control=decoder.decode_16bit_uint(),
            interface_type=decoder.decode_16bit_uint(),
            protocol=decoder.decode_16bit_uint(),
        )
    elif model_id == SunspecModel.ThreePhaseMeter and length == SunspecModelPayloadLengths.ThreePhaseMeter:
        result = ThreePhaseMeterData(
            # Current.
            current_total=decoder.decode_16bit_int(),
            current_l1=decoder.decode_16bit_int(),
            current_l2=decoder.decode_16bit_int(),
            current_l3=decoder.decode_16bit_int(),
            scale_factor_current=decoder.decode_16bit_int(),
            # Voltage.
            voltage=decoder.decode_16bit_int(),
            voltage_l1=decoder.decode_16bit_int(),
            voltage_l2=decoder.decode_16bit_int(),
            voltage_l3=decoder.decode_16bit_int(),
            voltage_ll=decoder.decode_16bit_int(),
            voltage_l1_l2=decoder.decode_16bit_int(),
            voltage_l2_l3=decoder.decode_16bit_int(),
            voltage_l3_l1=decoder.decode_16bit_int(),
            scale_factor_voltage=decoder.decode_16bit_int(),
            # Frequency.
            frequency=decoder.decode_16bit_int(),
            scale_factor_frequency=decoder.decode_16bit_int(),
            # Active power.
            active_power_total=decoder.decode_16bit_int(),
            active_power_l1=decoder.decode_16bit_int(),
            active_power_l2=decoder.decode_16bit_int(),
            active_power_l3=decoder.decode_16bit_int(),
            scale_factor_active_power=decoder.decode_16bit_int(),
            # Apparent power.
            apparent_power_total=decoder.decode_16bit_int(),
            apparent_power_l1=decoder.decode_16bit_int(),
            apparent_power_l2=decoder.decode_16bit_int(),
            apparent_power_l3=decoder.decode_16bit_int(),
            scale_factor_apparent_power=decoder.decode_16bit_int(),
            # Reactive power.
            reactive_power_total=decoder.decode_16bit_int(),
            reactive_power_l1=decoder.decode_16bit_int(),
            reactive_power_l2=decoder.decode_16bit_int(),
            reactive_power_l3=decoder.decode_16bit_int(),
            scale_factor_reactive_power=decoder.decode_16bit_int(),
            # Power factor.
            power_factor=decoder.decode_16bit_int(),
            power_factor_l1=decoder.decode_16bit_int(),
            power_factor_l2=decoder.decode_16bit_int(),
            power_factor_l3=decoder.decode_16bit_int(),
            scale_factor_power_factor=decoder.decode_16bit_int(),
            # Active energy.
            active_energy_exported_total=decoder.decode_32bit_uint(),
            active_energy_exported_l1=decoder.decode_32bit_uint(),
            active_energy_exported_l2=decoder.decode_32bit_uint(),
            active_energy_exported_l3=decoder.decode_32bit_uint(),
            active_energy_imported_total=decoder.decode_32bit_uint(),
            active_energy_imported_l1=decoder.decode_32bit_uint(),
            active_energy_imported_l2=decoder.decode_32bit_uint(),
            active_energy_imported_l3=decoder.decode_32bit_uint(),
            scale_factor_active_energy=decoder.decode_16bit_int(),
            # Apparent energy.
            apparent_energy_exported_total=decoder.decode_32bit_uint(),
            apparent_energy_exported_l1=decoder.decode_32bit_uint(),
            apparent_energy_exported_l2=decoder.decode_32bit_uint(),
            apparent_energy_exported_l3=decoder.decode_32bit_uint(),
            apparent_energy_imported_total=decoder.decode_32bit_uint(),
            apparent_energy_imported_l1=decoder.decode_32bit_uint(),
            apparent_energy_imported_l2=decoder.decode_32bit_uint(),
            apparent_energy_imported_l3=decoder.decode_32bit_uint(),
            scale_factor_apparent_energy=decoder.decode_16bit_int(),
            # Reactive energy.
            reactive_energy_imported_q1_total=decoder.decode_32bit_uint(),
            reactive_energy_imported_q1_l1=decoder.decode_32bit_uint(),
            reactive_energy_imported_q1_l2=decoder.decode_32bit_uint(),
            reactive_energy_imported_q1_l3=decoder.decode_32bit_uint(),
            reactive_energy_imported_q2_total=decoder.decode_32bit_uint(),
            reactive_energy_imported_q2_l1=decoder.decode_32bit_uint(),
            reactive_energy_imported_q2_l2=decoder.decode_32bit_uint(),
            reactive_energy_imported_q2_l3=decoder.decode_32bit_uint(),
            reactive_energy_exported_q3_total=decoder.decode_32bit_uint(),
            reactive_energy_exported_q3_l1=decoder.decode_32bit_uint(),
            reactive_energy_exported_q3_l2=decoder.decode_32bit_uint(),
            reactive_energy_exported_q3_l3=decoder.decode_32bit_uint(),
            reactive_energy_exported_q4_total=decoder.decode_32bit_uint(),
            reactive_energy_exported_q4_l1=decoder.decode_32bit_uint(),
            reactive_energy_exported_q4_l2=decoder.decode_32bit_uint(),
            reactive_energy_exported_q4_l3=decoder.decode_32bit_uint(),
            scale_factor_reactive_energy=decoder.decode_16bit_int(),
            # Events.
            events=decoder.decode_32bit_uint(),
        )
    elif model_id == SigningMeterModels.SigningMeter and length == SigningMeterModelPayloadLengths.SigningMeter:
        result = SigningMeterData(
            error_code=decoder.decode_string(size=2 * SigningMeterBlockOffsets.ErrorCodeLength),
            serial_number_meter=decoder.decode_string(size=2 * SigningMeterBlockOffsets.SerialNumberMeterLength),
            serial_number_communication_module=decoder.decode_string(size=2 * SigningMeterBlockOffsets.SerialNumberCommunicationModuleLength),
            software_version_meter=decoder.decode_string(size=2 * SigningMeterBlockOffsets.SoftwareVersionMeterLength),
            software_version_communication_module=decoder.decode_string(size=2 * SigningMeterBlockOffsets.SoftwareVersionCommunicationModuleLength),
            meter_address_1=decoder.decode_string(size=2 * SigningMeterBlockOffsets.MeterAddress1Length),
            meter_address_2=decoder.decode_string(size=2 * SigningMeterBlockOffsets.MeterAddress2Length),
            reference_cumulative_register=decoder.decode_32bit_uint(),
            scale_factor_reference_cumulative_register=decoder.decode_16bit_int(),
            power_down_counter=decoder.decode_32bit_uint(),
            response_counter=decoder.decode_32bit_uint(),
            current_time=decode_timestamp(decoder),
            time_set=decode_time_set_info(decoder),
            di_state=decoder.decode_16bit_uint(),
            do_state=decoder.decode_16bit_uint(),
            last_di_modification=decode_timestamp(decoder),
            last_do_modification=decode_timestamp(decoder),
            metadata_1=decoder.decode_string(size=2 * SigningMeterBlockOffsets.Metadata1Length),
            metadata_2=decoder.decode_string(size=2 * SigningMeterBlockOffsets.Metadata2Length),
            metadata_3=decoder.decode_string(size=2 * SigningMeterBlockOffsets.Metadata3Length),
            ecdsa_curve_name=decoder.decode_string(size=2 * SigningMeterBlockOffsets.EcdsaCurveNameLength),
            ecdsa_public_key=decode_binary_string(decoder, size=2 * SigningMeterBlockOffsets.EcdsaPublicKeyLength),
            )
    elif model_id == SigningMeterModels.SignedState and length == SigningMeterModelPayloadLengths.SignedState:
        result = SignedStateData(
            type=decoder.decode_16bit_uint(),
            status=decoder.decode_16bit_uint(),
            active_energy_exported_total=decoder.decode_32bit_uint(),
            active_energy_exported_total_scale_factor=decoder.decode_16bit_int(),
            active_power_total=decoder.decode_32bit_int(),
            active_power_total_scale_factor=decoder.decode_16bit_int(),
            server_id=decoder.decode_string(size=2 * SignedStateBlockOffsets.ServerIdLength),
            response_counter=decoder.decode_32bit_uint(),
            timestamp=decode_timestamp(decoder),
            time_set=decode_time_set_info(decoder),
            di_state=decoder.decode_16bit_uint(),
            do_state=decoder.decode_16bit_uint(),
            last_di_modification=decode_timestamp(decoder),
            last_do_modification=decode_timestamp(decoder),
            metadata_1=decoder.decode_string(size=2 * SignedStateBlockOffsets.Metadata1Length),
            metadata_2=decoder.decode_string(size=2 * SignedStateBlockOffsets.Metadata2Length),
            metadata_3=decoder.decode_string(size=2 * SignedStateBlockOffsets.Metadata3Length),
            signature=decode_binary_string(decoder, size=2 * SignedStateBlockOffsets.SignatureLength),
            )
    else:
        result = decoder.decode_binary_string(size=2 * length)

    return result


def decode_timestamp(decoder):
    return Timestamp(
        operating_seconds=decoder.decode_32bit_uint(),
        epoch_time_utc_seconds=decoder.decode_32bit_uint(),
        local_timezone_offset_minutes=decoder.decode_16bit_int())


def decode_time_set_info(decoder):
    return TimeSetInfo(
        counter=decoder.decode_32bit_uint(),
        operating_seconds=decoder.decode_32bit_uint())


def update_md_from_scaled_int32(md, value, scaler, unit):
    data = pack('>lbB', value, scaler, unit)
    # TODO: Clean up logging MD data.
    hexdump(data)
    md.update(data)


def update_md_from_scaled_uint32(md, value, scaler, unit):
    data = pack('>LbB', value, scaler, unit)
    # TODO: Clean up logging MD data.
    hexdump(data)
    md.update(data)


def update_md_from_string(md, string):
    length = pack('>L', len(string))
    # TODO: Clean up logging MD data.
    hexdump(length)
    hexdump(string)
    md.update(length)
    md.update(string)


def digest_for_snapshot_data(md, data):
    payload = data.payload
    digest = md()

    update_md_from_scaled_uint32(digest, payload.type, 0, DlmsUnits.UNITLESS)
    update_md_from_scaled_uint32(digest, payload.active_energy_exported_total,
        payload.active_energy_exported_total_scale_factor, DlmsUnits.WATT_HOURS)
    update_md_from_scaled_int32(digest, payload.active_power_total,
        payload.active_power_total_scale_factor, DlmsUnits.WATTS)
    update_md_from_string(digest, payload.server_id)
    update_md_from_scaled_uint32(digest, payload.response_counter, 0, DlmsUnits.UNITLESS)
    update_md_from_scaled_uint32(digest, payload.timestamp.operating_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_uint32(digest, payload.timestamp.epoch_time_utc_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_int32(digest, payload.timestamp.local_timezone_offset_minutes, 0, DlmsUnits.MINUTES)
    update_md_from_scaled_uint32(digest, payload.time_set.counter, 0, DlmsUnits.UNITLESS)
    update_md_from_scaled_uint32(digest, payload.time_set.operating_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_uint32(digest, payload.di_state, 0, DlmsUnits.UNITLESS)
    update_md_from_scaled_uint32(digest, payload.do_state, 0, DlmsUnits.UNITLESS)
    update_md_from_scaled_uint32(digest, payload.last_di_modification.operating_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_uint32(digest, payload.last_di_modification.epoch_time_utc_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_int32(digest, payload.last_di_modification.local_timezone_offset_minutes, 0, DlmsUnits.MINUTES)
    update_md_from_scaled_uint32(digest, payload.last_do_modification.operating_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_uint32(digest, payload.last_do_modification.epoch_time_utc_seconds, 0, DlmsUnits.SECONDS)
    update_md_from_scaled_int32(digest, payload.last_do_modification.local_timezone_offset_minutes, 0, DlmsUnits.MINUTES)
    update_md_from_string(digest, payload.metadata_1)
    update_md_from_string(digest, payload.metadata_2)
    update_md_from_string(digest, payload.metadata_3)

    return digest.digest()


def get_block(client, offset):
    # Read and decode block header.
    decoder = client.get_device_block(offset, SunspecOffsets.HeaderLength)
    model_id = decoder.decode_16bit_uint()
    length = decoder.decode_16bit_uint()

    # Read and decode block payload.
    decoder = client.get_device_block(offset + SunspecOffsets.HeaderLength, length)
    payload = decode_block_payload(decoder, model_id, length)

    return SunspecModelData(model_id, length, payload)


def get_value(client, value):
    # TODO: What about assinging 'get_device_block' a more appropriate name? It
    # just returns register data.
    decoder = client.get_device_block(value.offset, value.length)
    return value.parse_registers(decoder)


def into_chunks(array, length):
    for i in range(0, len(array), length):
        yield array[i:i + length]


def is_namedtuple(value):
    # Quirks for identifying namedtuples.
    return isinstance(value, tuple) and type(value) != tuple


def is_snapshot_block_info(info):
    return info != None and info.is_snapshot


def parse_args():
    # TODO: Streamline casing in parameter descriptions.

    block_short_name_help = 'block short name (see output of \'list-blocks\')'
    snapshot_short_name_help = 'snapshot ' + block_short_name_help

    # Attempt to retrieve communication paramter defaults from environment
    # variables. This will allow short command lines for repeated invocations.
    device = os.getenv('BSMTOOL_DEVICE')
    baud = auto_int(os.getenv('BSMTOOL_BAUD', 19200))
    unit = auto_int(os.getenv('BSMTOOL_UNIT', 42))
    timeout = auto_int(os.getenv('BSMTOOL_TIMEOUT', 10))
    chunk = auto_int(os.getenv('BSMTOOL_CHUNK', 125))

    parser = ArgumentParser(description='BSM Modbus Tool',
        epilog='You may specify communication parameters also by environment variables. Use BSMTOOL_DEVICE, BSMTOOL_BAUD, BSMTOOL_UNIT, BSMTOOL_TIMEOUT, and BSMTOOL_CHUNK.')
    # Default parser for communication parameters.
    parser.add_argument('--device', metavar='DEVICE', help='serial device', required=(device is None), default=device)
    parser.add_argument('--baud', metavar='BAUD', type=int, help='serial baud rate', default=baud)
    parser.add_argument('--timeout', metavar='SECONDS', type=float, help='request timeout', default=timeout)
    parser.add_argument('--relax', dest='relax', action='store_true', help='use a relaxed timing for receiving Modbus data (default on Windows)')
    parser.add_argument('--no-relax', dest='relax', action='store_false', help='use strict timing for receiving Modbus data (default on other platforms)')
    parser.add_argument('--unit', metavar='UNIT', type=int, help='Modbus RTU unit number', required=(unit is None), default=unit)
    parser.add_argument('--chunk-size', metavar='REGISTERS', type=int, help='Maximum amount of registers to read at once', default=chunk)
    parser.set_defaults(relax=relax_default_for_platform())

    subparsers = parser.add_subparsers(metavar='COMMAND', help='sub commands')

    # List block information.
    list_blocks_parser = subparsers.add_parser('list-blocks', help='list SunSpec blocks')
    list_blocks_parser.set_defaults(func=list_blocks_command)

    # Read and interpret SunSpec block.
    get_block_parser = subparsers.add_parser('get-block', help='read and interpret SunSpec block')
    get_block_parser.set_defaults(func=get_block_command)
    get_block_parser.add_argument('names', metavar='NAME', nargs='+',  help=block_short_name_help)

    # Get some values.
    #
    # TODO: This subcommand is heavy work in progress.
    get_parser = subparsers.add_parser('get', help='get individual values')
    get_parser.set_defaults(func=get_values_command)
    get_parser.add_argument('--device-address', action='store_true', help='Modbus device address')
    get_parser.add_argument('--baud-rate', action='store_true', help='Modbus baud rate')
    get_parser.add_argument('--epoch-time', action='store_true', help='Epoch time UTC [seconds]')
    get_parser.add_argument('--tz-offset', action='store_true', help='Local timezone UTC offset [minutes]')
    get_parser.add_argument('--time-set-counter', action='store_true', help='Time set counter')
    get_parser.add_argument('--time-set-at', action='store_true', help='Time last set at [operating seconds]')
    get_parser.add_argument('--digital-input', action='store_true', help='Digital input state')
    get_parser.add_argument('--digital-output', action='store_true', help='Digital output state')
    get_parser.add_argument('--meta-1', action='store_true', help='Metadata string 1')
    get_parser.add_argument('--meta-2', action='store_true', help='Metadata string 2')
    get_parser.add_argument('--meta-3', action='store_true', help='Metadata string 3')
    get_parser.add_argument('--scs-status', action='store_true', help='Signed current state state status')
    get_parser.add_argument('--stons-status', action='store_true', help='Signed turn-on state status')
    get_parser.add_argument('--stoffs-status', action='store_true', help='Signed turn-off state status')

    # Set writeable values.
    set_parser = subparsers.add_parser('set', help='Set values')
    set_parser.set_defaults(func=set_values_command)
    set_parser.add_argument('--device-address', metavar='ADDRESS', type=auto_int, help='Modbus device address (Signing Meter Block)')
    set_parser.add_argument('--baud-rate', metavar='BAUD', type=auto_int, help='Modbus baud rate')
    set_parser.add_argument('--epoch-time', metavar='SECONDS', type=auto_int, help='Epoch time UTC [seconds]')
    set_parser.add_argument('--tz-offset', metavar='MINUTES', type=auto_int, help='Local timezone UTC offset [minutes]')
    set_parser.add_argument('--digital-output', metavar='VALUE', type=auto_int, help='Digital output state')
    set_parser.add_argument('--meta-1', help='Metadata string 1')
    set_parser.add_argument('--meta-2', help='Metadata string 2')
    set_parser.add_argument('--meta-3', help='Metadata string 3')
    set_parser.add_argument('--scs-status', metavar='STATUS', type=auto_int, help='Signed current state state status')
    set_parser.add_argument('--stons-status', metavar='STATUS',  type=auto_int, help='Signed turn-on state status')
    set_parser.add_argument('--stoffs-status', metavar='STATUS', type=auto_int, help='Signed turn-off state status')
    set_parser.add_argument('--write-lead', metavar='REGS', type=auto_int, help='Length of lead to add to each write chunk (for testing purposes, it will likely mess up multi-chunk writes)', default=0)

    # Request generating a snapshot (for a given snapshot name).
    create_snapshot_parser = subparsers.add_parser('create-snapshot', help='Create snapshot but don\'t fetch data')
    create_snapshot_parser.set_defaults(func=create_snapshot_command)
    create_snapshot_parser.add_argument('name', help=snapshot_short_name_help)

    # Request snapshot, wait for completion and get data.
    get_snapshot_parser = subparsers.add_parser('get-snapshot', help='Create snapshot and get data')
    get_snapshot_parser.set_defaults(func=get_snapshot_command)
    get_snapshot_parser.add_argument('name', help=snapshot_short_name_help)

    # Verify snapshot signature.
    verify_snapshot_parser = subparsers.add_parser('verify-snapshot', help='Verifies signature of snapshot (but does not create it)')
    verify_snapshot_parser.set_defaults(func=verify_snapshot_command)
    verify_snapshot_parser.add_argument('name', help=snapshot_short_name_help)

    # Hex-dump_command registers.
    dump_parser = subparsers.add_parser('dump', help='Dump registers')
    dump_parser.set_defaults(func=dump_command)
    dump_parser.add_argument('offset', metavar='OFFSET', type=auto_int, help='Modbus block offset (words)')
    dump_parser.add_argument('length', metavar='LENGTH', type=auto_int, help='Block length (words)')

    # Print version information.
    version_parser = subparsers.add_parser('version', help='Print version')
    version_parser.set_defaults(func=version_command)

    return parser.parse_args()


def print_model_data(data, indent=MODEL_DATA_INDENT):
    for name, value in data._asdict().items():
        if is_namedtuple(value):
            print('{}{}:'.format(indent, name))
            print_model_data(value, indent + MODEL_DATA_INDENT)
        else:
            print('{}{}: {}'.format(indent, name, value))


def readable_values_for_args(args):
    return list(filter(lambda v: v.get_arg(args) is True, ALL_VALUES))


def register_hexdump(registers, offset=0):
    chunk_length = 8
    chunks = list(into_chunks(registers, chunk_length))

    start = offset

    for i in range(0, len(chunks)):
        chunk = chunks[i]

        # Hex data of registers.
        hex_chunk = ' '.join(map(lambda x: '{:04x}'.format(x), chunk))

        # Printable characters from big-endian register data.
        payload_chunk = b''.join(pack('>H', x) for x in chunk)
        printable = ''.join(map(lambda x: chr(x) if x >= 32 and x < 127 else '.', payload_chunk))

        print('{:8}: {:40} {}'.format(start, hex_chunk, printable))
        start += len(chunk)


def relax_default_for_platform():
    return True if sys.platform == 'win32' else False


def write_jobs_for_args(args):
    jobs = []

    # State of work-in-progress for current job.
    start = None
    offset = None
    builder = None

    for writeable in WRITEABLE_VALUES:
        if writeable.get_arg(args) is not None:
            # Data ahead! Let's add it to the current job-in-progress.

            # If the current writeable value does not fit into the current job's
            # chunk, finish it and prepare for the next.
            if start != None and writeable.offset + writeable.length - start > args.chunk_size:
                jobs.append(WriteJob(start, builder.to_registers()))
                start = None
                offset = None
                builder = None

            # Start new job.
            if start == None:
                builder = SunspecBuilder()
                if args.write_lead > 0:
                    start = writeable.offset - args.write_lead
                    offset = writeable.offset
                    builder.add_string('', 2 * args.write_lead)
                else:
                    start = writeable.offset
                    offset = start

            # Pad space between the last writeable value and this one.
            if offset < writeable.offset:
                padding_regs = writeable.offset - offset
                builder.add_string('', 2 * padding_regs)
                offset += padding_regs

            # Finally add the current data.
            writeable.generate_registers(builder, args)
            offset += writeable.length
        else:
           # We've encountered a writeable value with no data given. We can not
           # write over this value. Finis current job and prepare for next.
           if start != None:
               jobs.append(WriteJob(start, builder.to_registers()))
               start = None
               offset = None
               builder = None

    # Finish current job if there is work-in-progress.
    if start != None:
        jobs.append(WriteJob(start, builder.to_registers()))

    return jobs




#------------------------------------------------------------
# Program command implementations
#------------------------------------------------------------
def list_blocks_command(args):
    line_format = '{:<8} {:<24} {:<8} {:<8} {:<16}'
    print(line_format.format('Short', 'Name', 'Offset', 'Length', 'SunSpec Model'))
    for block in BLOCK_INFOS:
        print(line_format.format(block.short_name, block.name, block.offset, block.length, block.model))


def get_block_command(args):
    client = create_sunspec_sync_client(args)

    for name in args.names:
        info = block_info_for_short_name(name.lower())
        if not info:
            print('Unknown block \'{}\'.'.format(name), file=sys.stderr)
            sys.exit(1)
        data = get_block(client, info.offset)
        print_model_data(data)

    client.client.close()


def create_snapshot(client, block_info):
    result = False

    if block_info != None and block_info.is_snapshot and block_info.offset != None:
        result = client.write_registers(info.offset + SignedStateBlockOffsets.Status, SignedStateBlockStatus.UPDATING)

    return result


def dump_command(args):
    client = create_sunspec_sync_client(args)

    registers = client.read_holding_registers(args.offset, args.length)
    register_hexdump(registers, args.offset)

    client.client.close()


def get_values_command(args):
    values = readable_values_for_args(args)
    client = create_sunspec_sync_client(args)

    for value in values:
        data = get_value(client, value)
        print('{}'.format(data))

    client.client.close()



def set_values_command(args):
    jobs = write_jobs_for_args(args)
    client = create_sunspec_sync_client(args)

    for job in jobs:
        check_write_result(client.write_registers(job.offset, job.registers))

    client.client.close()


def create_snapshot_command(args):
    client = create_sunspec_sync_client(args)
    info = block_info_for_short_name(args.name.lower())

    if not is_snapshot_block_info(info):
        print('\'{}\' is not a valid snapshot name.'.format(args.name))
        sys.exit(1)
    else:
        client.write_registers(info.offset + SignedStateBlockOffsets.Status, SignedStateBlockStatus.UPDATING)

    client.client.close()


def get_snapshot_command(args):
    client = create_sunspec_sync_client(args)
    info = block_info_for_short_name(args.name.lower())
    result = False

    if not is_snapshot_block_info(info):
        print('\'{}\' is not a valid snapshot name.'.format(args.name))
        sys.exit(1)
    else:
        status_offset = info.offset + SignedStateBlockOffsets.Status

        # Request snapshot update by writing to the snapshot's status register.
        client.write_registers(status_offset, SignedStateBlockStatus.UPDATING)

        # Pull snapshot status until it is no longer updating.
        status = SignedStateBlockStatus.UPDATING
        while status == SignedStateBlockStatus.UPDATING:
            status = client.read_holding_registers(status_offset, 1)[0]

        # Updating is done. Get and display snapshot data in case of success.
        if status == SignedStateBlockStatus.VALID:
            data = get_block(client, info.offset)
            print('Updating \'{}\' succeeded: {}'.format(info.short_name, status))
            print('Snapshot data:')
            print_model_data(data)
            result = True
        else:
            print('Updating \'{}\' failed: {}'.format(info.short_name, status))
            result = False

    client.client.close()
    if not result:
        sys.exit(1)


def verify_snapshot_command(args):
    client = create_sunspec_sync_client(args)
    info = block_info_for_short_name(args.name.lower())
    result = False

    signing_meter_data = get_block(client, SigningMeterOffsets.SigningMeterBlock)

    if not is_snapshot_block_info(info):
        print('\'{}\' is not a valid snapshot name.'.format(args.name))
        sys.exit(1)
    else:
        snapshot_data = get_block(client, info.offset)

        curve_name = signing_meter_data.payload.ecdsa_curve_name
        public_key = signing_meter_data.payload.ecdsa_public_key
        signature = snapshot_data.payload.signature

        print('Curve: {}'.format(signing_meter_data.payload.ecdsa_curve_name))
        print('Public key: {}'.format(binascii.hexlify(signing_meter_data.payload.ecdsa_public_key)))
        print('Snapshot data:')
        print_model_data(snapshot_data)
        print('Signature: {}'.format(binascii.hexlify(snapshot_data.payload.signature)))

        assert curve_name == b'secp256r1'
        curve = SECP256r1
        md = sha256

        print('Computing SHA-256 digest for snapshot data:')
        digest = digest_for_snapshot_data(md, snapshot_data)
        print('Snapshot data SHA-256 digest: {}'.format(binascii.hexlify(digest)))

        if len(public_key) == 0:
            print('Failed. Device has no public key.')
            result = False
        elif len(signature) == 0:
            print('Failed. Snapshot contains no signature.')
            result = False
        else:
            if verify_signed_digest(curve, md, public_key, signature, digest):
                print('Success.')
                result = True
            else:
                print('Failed.')
                result = False

    client.client.close()
    if not result:
        sys.exit(1)


def version_command(args):
    print(version.version)


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
