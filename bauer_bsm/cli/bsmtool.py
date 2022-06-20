#!/usr/bin/env python3


# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from . import util as cliutil
from ..bsm import config
from ..bsm.client import BsmClientDevice, SunSpecBsmClientDevice
from ..crypto import util as cryptoutil
from ..exporter import chargy, ocmf, registers
from ..sunspec.core import suns
from ..util import package_version
from argparse import ArgumentParser, FileType

import csv
import os
import re
import sys


# Slicers for modbus messages in pySunSpec's tracing output. They are meant for
# messages represented as contigous hex strings and will return an array of
# logically grouped data (device address, function code, ...).
_TRACE_RTU_SLICERS = \
    {
        ('->', '03'): lambda s: [s[0:2], s[2:4], s[4:8], s[8:-4], s[-4:]],
        ('->', '10'): lambda s: [s[0:2], s[2:4], s[4:8], s[8:12], s[12:14], s[14:-4], s[-4:]],

        ('<--', '03'): lambda s: [s[0:2], s[2:4], s[4:6], s[6:-4], s[-4:]],
        ('<--', '10'): lambda s: [s[0:2], s[2:4], s[4:8], s[8:-4], s[-4:]],
    }


def create_argument_parser():
    # TODO: How to get the main binary name? '%(prog)s' returns the subcommand
    # name for subcommands.
    path_epilog = '''
        A path may be just a model instance alias as shown by \'bsmtool
        models\' or an istance alias and a data point name separated by /.
        Casing is ignored. The following paths all refer to the data point
        \'Md\' (model name) from the common model instance: \'common/Md\',
        \'common/md\', \'cb/md\'. The whole common model instance could be
        read with the path \'common\' or \'cb\'.
        '''
    snapshot_alias_help = 'snapshot model instance alias (see output of \'models\')'

    # Attempt to retrieve communication paramter defaults from environment
    # variables. This will allow short command lines for repeated invocations.
    device = os.getenv('BSMTOOL_DEVICE')
    baud = cliutil.auto_int(os.getenv('BSMTOOL_BAUD', 19200))
    unit = cliutil.auto_int(os.getenv('BSMTOOL_UNIT', 42))
    timeout = float(os.getenv('BSMTOOL_TIMEOUT', 13))
    chunk = cliutil.auto_int(os.getenv('BSMTOOL_CHUNK', 125))

    parser = ArgumentParser(description='BSM Modbus Tool',
        epilog='You may specify communication parameters also by environment variables. Use BSMTOOL_DEVICE, BSMTOOL_BAUD, BSMTOOL_UNIT, BSMTOOL_TIMEOUT, and BSMTOOL_CHUNK.')
    # Default parser for communication parameters.
    parser.add_argument('--device', metavar='DEVICE', help='serial device', required=(device is None), default=device)
    parser.add_argument('--baud', metavar='BAUD', type=cliutil.auto_int, help='serial baud rate', default=baud)
    parser.add_argument('--timeout', metavar='SECONDS', type=float, help='request timeout', default=timeout)
    parser.add_argument('--unit', metavar='UNIT', type=cliutil.auto_int, help='Modbus RTU unit number', required=(unit is None), default=unit)
    parser.add_argument('--chunk-size', metavar='REGISTERS', type=cliutil.auto_int, help='maximum amount of registers to read at once', default=chunk)
    parser.add_argument('--trace', action='store_true', help='trace Modbus communication (reads/writes)')
    parser.add_argument('--verbose', action='store_true', help='give verbose output')
    parser.add_argument('--dtr', metavar='VALUE', type=cliutil.auto_bool, help='set serial device DTR line to VALUE (which may be used for controlling test equipment)', default=None)
    parser.add_argument('--rts', metavar='VALUE', type=cliutil.auto_bool, help='set serial device RTS line to VALUE (which may be used for controlling test equipment)', default=None)
    parser.add_argument('--public-key-format', choices=cryptoutil.PUBLIC_KEY_RENDERER.keys(), help='output format of ECDSA public key (see RFC 5480 for DER and SEC1 section 2.3.3 for details about formats)', default=cryptoutil.PUBLIC_KEY_DEFAULT_FORMAT)

    subparsers = parser.add_subparsers(metavar='COMMAND', help='sub commands')

    # List model instances.
    models_parser = subparsers.add_parser('models', help='list SunSpec model instances')
    models_parser.set_defaults(func=list_model_instances_command)

    # Export register layout.
    export_parser = subparsers.add_parser('export', help='export register layout')
    export_parser.set_defaults(func=export_command)
    export_parser.add_argument('file', metavar='FILE', type=FileType('w'), help='output file name')

    # Get model instance or single data point values.
    get_parser = subparsers.add_parser('get', help='get individual values')
    get_parser.set_defaults(func=get_command)
    get_parser.add_argument('paths', metavar='PATH', nargs='+', help='get data from models or data points for the given path(s).')
    get_parser.epilog = path_epilog

    # Set data point values.
    set_parser = subparsers.add_parser('set', help='set values')
    set_parser.set_defaults(func=set_command)
    set_parser.add_argument('path_value_pairs', metavar='PATH_VALUE', nargs='+', help='set data point values for the given path and value pairs (in the form PATH=VALUE).')
    set_parser.epilog = path_epilog

    # Request generating a snapshot (for a given snapshot name).
    create_snapshot_parser = subparsers.add_parser('create-snapshot', help='create snapshot but don\'t fetch data')
    create_snapshot_parser.set_defaults(func=create_snapshot_command)
    create_snapshot_parser.add_argument('name', help=snapshot_alias_help)

    # Request snapshot, wait for completion and get data.
    get_snapshot_parser = subparsers.add_parser('get-snapshot', help='create snapshot and fetch data')
    get_snapshot_parser.set_defaults(func=get_snapshot_command)
    get_snapshot_parser.add_argument('name', help=snapshot_alias_help)

    # Verify snapshot signature.
    verify_snapshot_parser = subparsers.add_parser('verify-snapshot', help='verify snapshot signature (but do not create it)')
    verify_snapshot_parser.set_defaults(func=verify_snapshot_command)
    verify_snapshot_parser.add_argument('name', help=snapshot_alias_help)

    # Verify a signature for given message digest and public key.
    verify_signature_parser = subparsers.add_parser('verify-signature', help='verify arbitrary signature for a given public key and digest')
    verify_signature_parser.set_defaults(func=verify_signature_command)
    verify_signature_parser.add_argument('public_key', metavar='PUBLIC_KEY', type=cliutil.hex_data_or_file, help='public key as hex data or a file name to read binary data from. The data is expected to be catenated x and y coordinates x || y.')
    verify_signature_parser.add_argument('message_digest', metavar='MD', type=cliutil.hex_data_or_file, help='message digest as hex data or a file name to read binary data from.')
    verify_signature_parser.add_argument('signature', metavar='SIGNATURE', type=cliutil.hex_data_or_file, help='signature as hex data or a file name to read binary from. The data is expected to be catenated r and s values r || s.')

    # Generate data for Chargy from already existing snapshots.
    chargy_parser = subparsers.add_parser('chargy', help='generate billing data sample for Chargy from already existing snapshots (stons and stoffs)')
    chargy_parser.set_defaults(func=chargy_command)
    chargy_parser.add_argument('--station-serial-number', metavar='SERIAL_NUMBER', help='charging station\'s serial number', default='2020-24-T-042')
    chargy_parser.add_argument('--station-compliance-info', metavar='INFO', help='compliance info information for the charging station', default='See https://www.chargeit-mobility.com/wp-content/uploads/chargeIT-Baumusterpr%C3%BCfbescheinigung-Lades%C3%A4ule-Online.pdf for type examination certificate')
    chargy_parser.add_argument('start', metavar='START', nargs='?', help=snapshot_alias_help, default='stons')
    chargy_parser.add_argument('end', metavar='END', nargs='?', help=snapshot_alias_help, default='stoffs')

    # Generate OCMF XML from already existings snapshots.
    ocmf_xml_parser = subparsers.add_parser('ocmf-xml', help='generate OCMF XML from already existing snapshots (stons and stoffs)',
        epilog='Use matching matching start and end snapshots like \'stons\' and \'stoffs\' for typical OCMF XML output.')
    ocmf_xml_parser.add_argument('start', metavar='START', nargs='?', help=snapshot_alias_help, default='ostons')
    ocmf_xml_parser.add_argument('end', metavar='END', nargs='?', help=snapshot_alias_help, default='ostoffs')
    ocmf_xml_parser.set_defaults(func=ocmf_xml_command)

    # Hex-dump registers.
    dump_parser = subparsers.add_parser('dump', help='dump registers')
    dump_parser.set_defaults(func=dump_command)
    dump_parser.add_argument('offset', metavar='OFFSET', type=cliutil.auto_int, help='Modbus register offset (words, starting at 0)')
    dump_parser.add_argument('length', metavar='LENGTH', type=cliutil.auto_int, help='block length (words)')

    # Print version information.
    version_parser = subparsers.add_parser('version', help='print version')
    version_parser.set_defaults(func=version_command)

    return parser


def create_client_backend(clazz, args):
    trace = None
    if args.trace:
        trace = trace_modbus_rtu

    client = clazz(slave_id=args.unit, name=args.device,
        baudrate=args.baud, timeout=args.timeout, max_count=args.chunk_size,
        trace=trace)

    # Set the two modem control lines DTR and RTS. This might be useful for
    # controlling test equipment via this lines.
    serial = None
    if isinstance(client, BsmClientDevice):
        serial = client.modbus_device.client.serial
    elif isinstance(client, SunSpecBsmClientDevice):
        serial = client.device.modbus_device.client.serial
    else:
        raise ValueError('Unsupported client class {}'.format(type(client).__name__))

    if args.dtr is not None:
        serial.dtr = args.dtr

    if args.rts is not None:
        serial.rts = args.rts

    return client



def create_client(args):
    return create_client_backend(BsmClientDevice, args)


def create_sunspec_client(args):
    return create_client_backend(SunSpecBsmClientDevice, args)


def into_chunks(array, length):
    for i in range(0, len(array), length):
        yield array[i:i + length]


def md_trace_print(string):
    for line in string.splitlines():
        print(line)


def register_hexdump_bytes(data, offset=0):
    chunk_regs = 8
    chunk_length = 2 * chunk_regs

    start = offset
    lines = []

    for chunk in into_chunks(data, chunk_length):
        # Hex data of registers.
        hex_chunk = ' '.join(map(lambda x: '{:02x}{:02x}'.format(x[0], x[1]), zip(chunk[::2], chunk[1::2])))
        # Printable characters from data.
        printable = ''.join(map(lambda x: chr(x) if x >= 32 and x < 127 else '.', chunk))

        lines.append('{:8}: {:40} {}'.format(start, hex_chunk, printable))
        start += chunk_regs

    return '\n'.join(lines)


def trace_modbus_rtu(string):
    # Attempt to logically group known Modbus frame formats in the trace output
    # from pySunSpec.
    #
    # The Modbus message is expected at the end of a trace output line. Capture
    # "direction indicator", address, and function code.
    match = re.search('(<--|->)([0-9a-fA-F]{2})([0-9a-fA-F]{2})[0-9a-fA-F]+$', string)
    if match:
        # Look up message slicer by "direction indicator" and function code.
        slicer = _TRACE_RTU_SLICERS.get((match.group(1), match.group(3)), None)
        if slicer:
            (data_start, _) = match.span(2)
            prefix = string[:data_start]
            data = string[data_start:]
            # Separate the message slices by spaces.
            sliced = ' '.join(slicer(data))
            string = prefix + sliced

    # TODO: What about creating a feature request for "pretty tracing"? In the
    # sense that the trace function gets device, addres, payload data passed
    # separately for formatting?
    print(string)




#
# Program commands.
#

def list_model_instances_command(args):
    line_format = '{:<8} {:<8} {:<8} {:<40} {:<16} {}'
    client = create_client(args)

    print(line_format.format('Address', 'ID', 'Payload', 'Label', 'Name', 'Aliases'))

    for index, model in enumerate(client.models_list):
        name = cliutil.model_name(model)
        rendered_aliases = ''

        aliases = client.aliases_list[index]
        if aliases:
            rendered_aliases = ', '.join(aliases)

        print(line_format.format(model.addr - 2, model.id, model.len,
            client.model_instance_label(model), name, rendered_aliases))

    client.close()


def dump_command(args):
    client = create_client(args)

    data = client.read(args.offset, args.length)
    print(register_hexdump_bytes(data, args.offset))

    client.close()


def export_command(args):
    """
    Exports the complete Modbus register layout from model data into CSV.
    """
    client = create_client(args)
    writer = csv.writer(args.file)

    registers.write_register_overview_csv(client, writer)

    client.close()


def get_command(args):
    client = create_client(args)

    for path in args.paths:
        (model_name, point_id) = cliutil.model_name_and_point_id_for_path(path)

        # TODO: Reuse models already read for this command.
        model = client.lookup_model(model_name)
        if not model:
            print('Unknown model \'{}\'.'.format(model_name), file=sys.stderr)
            sys.exit(1)

        model.read_points()

        if point_id:
            device = model.device
            prefix = '{}/'.format(model.model_type.name)

            # Attempt to interpret point_id as either a regular data point ID
            # or the ID of a BLOB.
            #
            # TODO: Add support for printing non-BLOB data from repeating
            # blocks if required.
            point = client.lookup_point_in_model(model, point_id)
            if point:
                cliutil.print_point_data(point, prefix=prefix)
            elif device.has_repeating_blocks_blob_layout(model) and device.repeating_blocks_blob_id(model).lower() == point_id.lower():
                cliutil.print_blob_data(model, prefix=prefix, pk_format=args.public_key_format)
            else:
                print('Unknown data point \'{}\' in model \'{}\'.'.format(point_id, model_name),
                    file=sys.stderr)
                sys.exit(1)
        else:
            cliutil.print_model_data(model, verbose=args.verbose,
                pk_format=args.public_key_format)

    client.close()


def set_command(args):
    client = create_client(args)
    models_to_write = set()

    for path_value in args.path_value_pairs:
        (path, value) = tuple(path_value.split('=', 1))
        (model_name, point_id) = cliutil.model_name_and_point_id_for_path(path)
        (model, point) = client.lookup_model_and_point(model_name, point_id)

        if not model or not point:
            print('Unknown data point \'{}\''.format(path), file=sys.stderr)
            sys.exit(1)

        if point.point_type.access != suns.SUNS_ACCESS_RW:
            print('Could not write to read-only data point \'{}/{}\'.'.format(
                model.model_type.name, point.point_type.id), file=sys.stderr)
            sys.exit(1)

        point.value = point.point_type.to_value(value)
        models_to_write.add(model)

    # pySunSpec combines updating neighbour values into a single write. This
    # keeps the BSM mechanism for having these values initially set both
    # working with this backend.
    for model in models_to_write:
        model.write_points()

    client.close()


def create_snapshot_command(args):
    client = create_client(args)
    alias = args.name.lower()

    # Test whether the supplied name is a valid alias.
    model = client.snapshot_aliases.get(alias)
    if not model:
        print('\'{}\' is not a valid snapshot name.'.format(args.name),
            file=sys.stderr)
        sys.exit(1)
    else:
        client.create_snapshot(alias)

    client.close()


def get_snapshot_command(args):
    client = create_client(args)
    alias = args.name.lower()
    result = False

    # Test whether the supplied name is a valid alias.
    model = client.snapshot_aliases.get(alias)
    if not model:
        print('\'{}\' is not a valid snapshot name.'.format(args.name),
            file=sys.stderr)
        sys.exit(1)
    else:
        snapshot = client.get_snapshot(alias)
        if snapshot is not None:
            print('Updating \'{}\' succeeded'.format(args.name))
            print('Snapshot data:')
            cliutil.print_model_data(model, verbose=args.verbose)
            result = True
        else:
            # Snapshot model has been updated by get_snapshot.
            status = model.points[config.SNAPSHOT_STATUS_DATA_POINT_ID]
            print('Updating \'{}\' failed: {}'.format(args.name, status.value),
                file=sys.stderr)
            result = False

    client.close()
    if not result:
        sys.exit(1)


def chargy_command(args):
    client = create_sunspec_client(args)
    result = False

    output = chargy.generate_chargy_json(client, args.start, args.end,
        station_serial_number=args.station_serial_number,
        station_compliance_info=args.station_compliance_info)

    if output is not None:
        sys.stdout.buffer.write(output)
        result = True
    else:
        print('Generating Chargy JSON data failed due to invalid snapshot(s).',
            file=sys.stderr)

    client.close()
    if not result:
        sys.exit(1)


def ocmf_xml_command(args):
    client = create_sunspec_client(args)
    result = False

    xml = ocmf.generate_ocmf_xml(client, begin_alias=args.start, end_alias=args.end)

    if xml is not None:
        sys.stdout.buffer.write(xml)
        result = True
    else:
        print('Genrating OCMF XML failed due to invalid snapshot(s).',
            file=sys.stderr)

    client.close()
    if not result:
        sys.exit(1)


def verify_signature_command(args):
    # The following example will be verified successfully:
    #
    #     public key:     3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254
    #     message digest: cab351d004e66292963ca855717cc7ba55cc84b11a655d0d1db4c705d05796e7
    #     signature:      30450220633af3e89b89747ed105f7b7df02b814ad289dc8d20aed6815c184e4344a0109022100d1e0019af352cadc5aef90687903c54c0e41074a3ede65d8798769ab44959329
    #

    if cryptoutil.verify_signed_digest(args.public_key, config.BSM_MESSAGE_DIGEST, args.signature, args.message_digest):
        if args.verbose:
            print('Success.')
    else:
        print('Failed.', file=sys.stderr)
        sys.exit(1)


def verify_snapshot_command(args):
    client = create_client(args)
    alias = args.name.lower()
    result = False

    snapshot = client.snapshot_aliases.get(args.name.lower())

    if not snapshot:
        print('\'{}\' is not a valid snapshot name.'.format(args.name),
            file=sys.stderr)
        sys.exit(1)
    else:
        result = client.verify_snapshot(alias, trace=md_trace_print)

    client.close()
    if not result:
        sys.exit(1)


def version_command(args):
    print(package_version())




#
# Command line interface entry points.
#

def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
