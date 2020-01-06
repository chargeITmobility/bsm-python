from six import iteritems
from enum import IntEnum


# --------------------------------------------------------------------------- # 
# Sunspec Common Constants
# --------------------------------------------------------------------------- # 
class SunspecDefaultValue(object):
    """ A collection of constants to indicate if
    a value is not implemented.
    """
    Signed16        = 0x8000
    Unsigned16      = 0xffff
    Accumulator16   = 0x0000
    Scale           = 0x8000
    Signed32        = 0x80000000
    Float32         = 0x7fc00000
    Unsigned32      = 0xffffffff
    Accumulator32   = 0x00000000
    Signed64        = 0x8000000000000000
    Unsigned64      = 0xffffffffffffffff
    Accumulator64   = 0x0000000000000000
    String          = b'\x00'


class SunspecStatus(object):
    """ Indicators of the current status of a
    sunspec device
    """
    Normal  = 0x00000000
    Error   = 0xfffffffe
    Unknown = 0xffffffff


class SunspecIdentifier(object):
    """ Assigned identifiers that are pre-assigned
    by the sunspec protocol.
    """
    Sunspec = 0x53756e53


class SunspecModel(object):
    """ Assigned device indentifiers that are pre-assigned
    by the sunspec protocol.
    """
    #---------------------------------------------
    # 0xx Common Models
    #---------------------------------------------
    CommonBlock                              = 1
    AggregatorBlock                          = 2
    InterfaceHeader                          = 10
    SerialInterface                          = 17

    #---------------------------------------------
    # 1xx Inverter Models
    #---------------------------------------------
    SinglePhaseIntegerInverter               = 101
    SplitPhaseIntegerInverter                = 102
    ThreePhaseIntegerInverter                = 103
    SinglePhaseFloatsInverter                = 103
    SplitPhaseFloatsInverter                 = 102
    ThreePhaseFloatsInverter                 = 103

    #---------------------------------------------
    # 2xx Meter Models
    #---------------------------------------------
    SinglePhaseMeter                         = 201
    SplitPhaseMeter                          = 201
    WyeConnectMeter                          = 201
    DeltaConnectMeter                        = 201
    ThreePhaseMeter                          = 203

    #---------------------------------------------
    # 3xx Environmental Models
    #---------------------------------------------
    BaseMeteorological                       = 301
    Irradiance                               = 302
    BackOfModuleTemperature                  = 303
    Inclinometer                             = 304
    Location                                 = 305
    ReferencePoint                           = 306
    BaseMeteorological                       = 307
    MiniMeteorological                       = 308

    #---------------------------------------------
    # 4xx String Combiner Models             
    #---------------------------------------------
    BasicStringCombiner                      = 401
    AdvancedStringCombiner                   = 402

    #---------------------------------------------
    # 5xx Panel Models
    #---------------------------------------------
    PanelFloat                               = 501
    PanelInteger                             = 502

    #---------------------------------------------
    # 641xx Outback Blocks
    #---------------------------------------------
    OutbackDeviceIdentifier                  = 64110
    OutbackChargeController                  = 64111
    OutbackFMSeriesChargeController          = 64112
    OutbackFXInverterRealTime                = 64113
    OutbackFXInverterConfiguration           = 64114
    OutbackSplitPhaseRadianInverter          = 64115
    OutbackRadianInverterConfiguration       = 64116
    OutbackSinglePhaseRadianInverterRealTime = 64117
    OutbackFLEXNetDCRealTime                 = 64118
    OutbackFLEXNetDCConfiguration            = 64119
    OutbackSystemControl                     = 64120

    #---------------------------------------------
    # 64xxx Vender Extension Block
    #---------------------------------------------
    VendorPrivateStart                       = 64900
    VendorPrivateEnd                         = 64910

    EndOfSunSpecMap                          = 65535

    @classmethod
    def lookup(klass, code):
        """ Given a device identifier, return the
        device model name for that identifier

        :param code: The device code to lookup
        :returns: The device model name, or None if none available
        """
        values = dict((v, k) for k, v in iteritems(klass.__dict__)
            if not callable(v))
        return values.get(code, None)


class SunspecOffsets(object):
    """ Well known offsets that are used throughout
    the sunspec protocol
    """
    HeaderLength            = 2
    CommonBlock             = 40000
    CommonBlockLength       = 70
    AlternateCommonBlock    = 50000


class SunspecModelPayloadLengths(IntEnum):
    """ Payload lengths of SunSpec Model blocks

    These are the actual payload lengths without header. Such lengths are given
    at other Enums from this file but they include block headers and for the
    common block the SunSpec ID as well. Let's have the pure payload lengths
    here.
    """
    CommonBlock                              = 66
    InterfaceHeader                          = 4
    SerialInterface                          = 12
    ThreePhaseMeter                          = 105
    EndOfSunSpecMapBlock                     = 0


# TODO: Complete block information.
class CommonBlockOffsets(IntEnum):
    """ Offsets and field lengths of SunSpec Common Block. """
    Manufacturer                             = 2
    ManufacturerLength                       = 16
    Model                                    = 18
    ModelLength                              = 16
    Options                                  = 34
    OptionsLength                            = 8
    Version                                  = 42
    VersionLength                            = 8
    SerialNumber                             = 50
    SerialNumberLength                       = 16
    DeviceAddress                            = 66
    DeviceAddressLength                      = 1
    Padding                                  = 67
    PaddingLength                            = 1


# TODO: Complete block information.
class SerialInterfaceOffsets(IntEnum):
    """ Selected offsets and field lengths of SunSpec SerialInterfaceBlock. """
    Name                                     = 2
    NameLength                               = 4
    BaudRate                                 = 6
    BaudRateLength                           = 2
