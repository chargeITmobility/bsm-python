from .constants import SunspecModel, SunspecOffsets, SunspecIdentifier, SunspecDefaultValue
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from six import iteritems


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
logging.basicConfig()


# --------------------------------------------------------------------------- # 
# Sunspec Client
# --------------------------------------------------------------------------- # 
class SunspecDecoder(BinaryPayloadDecoder):
    """ A decoder that deals correctly with the sunspec
    binary format.
    """

    def __init__(self, payload, byteorder, wordorder):
        """ Initialize a new instance of the SunspecDecoder

        .. note:: This is always set to big endian byte order
        as specified in the protocol.
        """
        byteorder = Endian.Big
        BinaryPayloadDecoder.__init__(self, payload, byteorder, wordorder)

    def decode_binary_string(self, size=1):
        return super().decode_string(size)

    def decode_string(self, size=1):
        """ Decodes a string from the buffer

        :param size: The size of the string to decode
        """
        string = super().decode_string(size)
        return string.split(SunspecDefaultValue.String)[0]

class SunspecBuilder(BinaryPayloadBuilder):
    def __init__(self, payload=None, byteorder=Endian.Big, wordorder=Endian.Big, repack=False):
        BinaryPayloadBuilder.__init__(self, payload, byteorder, wordorder, repack)

    def add_string(self, value, size=1):
        assert(size % 2 == 0)
        assert(len(value) <= size)

        # TODO: How to deal with non-ASCII characters? The PyModbus stack
        # operates on characters so we have to make assumptions about the
        # encoding.

        padding = '\x00' * (size - len(value))
        super().add_string(value + padding)

class SunspecClient(object):

    def __init__(self, client, unit=None, chunk_size=125):
        """ Initialize a new instance of the client

        :param client: The modbus client to use
        """
        self.client = client
        self.unit = unit
        self.chunk_size = chunk_size
        self.offset = SunspecOffsets.CommonBlock

    def initialize(self):
        """ Initialize the underlying client values

        :returns: True if successful, false otherwise
        """
        decoder  = self.get_device_block(self.offset, 2)
        if decoder.decode_32bit_uint() == SunspecIdentifier.Sunspec:
            return True
        self.offset = SunspecOffsets.AlternateCommonBlock
        decoder  = self.get_device_block(self.offset, 2)
        return decoder.decode_32bit_uint() == SunspecIdentifier.Sunspec

    def get_common_block(self):
        """ Read and return the sunspec common information
        block.

        :returns: A dictionary of the common block information
        """
        length  = SunspecOffsets.CommonBlockLength
        decoder = self.get_device_block(self.offset, length)
        return {
            'SunSpec_ID':       decoder.decode_32bit_uint(),
            'SunSpec_DID':      decoder.decode_16bit_uint(),
            'SunSpec_Length':   decoder.decode_16bit_uint(),
            'Manufacturer':     decoder.decode_string(size=32),
            'Model':            decoder.decode_string(size=32),
            'Options':          decoder.decode_string(size=16),
            'Version':          decoder.decode_string(size=16),
            'SerialNumber':     decoder.decode_string(size=32),
            'DeviceAddress':    decoder.decode_16bit_uint(),
            'Pad':              decoder.decode_16bit_uint(),
        }

    def get_device_block(self, offset, size):
        """ A helper method to retrieve the next device block

        .. note:: We will read 2 more registers so that we have
        the information for the next block.

        :param offset: The offset to start reading at
        :param size: The size of the offset to read
        :returns: An initialized decoder for that result
        """
        _logger.debug("reading device block[{}..{}]".format(offset, offset + size))

        registers = []
        remaining = size

        if size > 0:
            while remaining > 0:
                current_chunk = min(remaining, self.chunk_size)
                response = self.client.read_holding_registers(offset, current_chunk, unit=self.unit)

                registers += response.registers
                offset += current_chunk
                remaining -= current_chunk

        return SunspecDecoder.fromRegisters(registers)

    def get_all_device_blocks(self, raw_data=False):
        """ Retrieve all the available blocks in the supplied
        sunspec device.

        .. note:: Since we do not know how to decode the available
        blocks, this returns a list of dictionaries of the form:

            decoder: the-binary-decoder,
            model:   the-model-identifier (name)

        :returns: A list of the available blocks
        """
        blocks = []
        offset = self.offset + 2
        model  = SunspecModel.CommonBlock
        while model != SunspecModel.EndOfSunSpecMap:
            decoder = self.get_device_block(offset, 2)
            model   = decoder.decode_16bit_uint()
            start   = offset
            length  = decoder.decode_16bit_uint()

            offset += 2

            if raw_data:
                decoder = self.get_device_block(offset, length)

            offset += length

            blocks.append({
                'model' : model,
                'name'  : SunspecModel.lookup(model),
                'start' : start,
                'length': length,
            })
        return blocks

    def read_holding_registers(self, offset, length):
        _logger.debug('reading registers {}..{}'.format(offset, offset + length))

        registers = []
        remaining = length

        while remaining > 0:
            current_chunk = min(remaining, self.chunk_size)
            response = self.client.read_holding_registers(offset, current_chunk, unit=self.unit)

            registers += response.registers
            offset += current_chunk
            remaining -= current_chunk

        return registers

    def write_registers(self, offset, values):
        _logger.debug('write registers {} with {}'.format(offset, values))
        self.client.write_registers(offset, values, unit=self.unit)


