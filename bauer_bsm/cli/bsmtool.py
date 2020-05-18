# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


#!/usr/bin/env python3


from ..bsm import config
from ..bsm import format as fmt
from ..bsm.client import BsmClientDevice
from ..bsm.md import md_for_snapshot_data
from ..crypto import util as cutil
from ..sunspec.core import client as sclient
from ..sunspec.core import device as sdevice
from ..sunspec.core import suns
from ..util import package_version
from argparse import ArgumentParser

import os
import string
import sys


MODEL_DATA_INDENT = '    '


def auto_int(x):
    result = None

    if isinstance(x, int):
        # Pass-through integer values.
        result = x
    elif x != None:
        # Parse everything else but 'None' with auto base detection.
        result = int(x, 0)

    return result


def create_argument_parser():
    snapshot_alias_help = 'snapshot model instance alias (see output of \'models\')'

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
    parser.add_argument('--unit', metavar='UNIT', type=int, help='Modbus RTU unit number', required=(unit is None), default=unit)
    parser.add_argument('--chunk-size', metavar='REGISTERS', type=int, help='maximum amount of registers to read at once', default=chunk)
    parser.add_argument('--trace', action='store_true', help='trace Modbus communication (reads/writes)')
    parser.add_argument('--verbose', action='store_true', help='give verbose output')

    subparsers = parser.add_subparsers(metavar='COMMAND', help='sub commands')

    # List model instances.
    models_parser = subparsers.add_parser('models', help='list SunSpec model instances')
    models_parser.set_defaults(func=list_model_instances_command)

    # Get model instance or single data point values.
    get_parser = subparsers.add_parser('get', help='get individual values')
    get_parser.set_defaults(func=get_command)
    get_parser.add_argument('paths', metavar='PATH', nargs='+', help='get data from models or data points for the given path(s).')

    # Set data point values.
    set_parser = subparsers.add_parser('set', help='set values')
    set_parser.set_defaults(func=set_command)
    set_parser.add_argument('path_value_pairs', metavar='PATH_VALUE', nargs='+', help='set data point values for the given path and value pairs (in the form PATH=VALUE).')

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
    verify_signature_parser.add_argument('public_key', metavar='PUBLIC_KEY', type=hex_data_or_file, help='public key as hex data or a file name to read binary data from. The data is expected to be catenated x and y coordinates x || y.')
    verify_signature_parser.add_argument('message_digest', metavar='MD', type=hex_data_or_file, help='message digest as hex data or a file name to read binary data from.')
    verify_signature_parser.add_argument('signature', metavar='SIGNATURE', type=hex_data_or_file, help='signature as hex data or a file name to read binary from. The data is expected to be catenated r and s values r || s.')

    # Hex-dump_command registers.
    dump_parser = subparsers.add_parser('dump', help='dump registers')
    dump_parser.set_defaults(func=dump_command)
    dump_parser.add_argument('offset', metavar='OFFSET', type=auto_int, help='Modbus register offset (words, starting at 0)')
    dump_parser.add_argument('length', metavar='LENGTH', type=auto_int, help='block length (words)')

    # Print version information.
    version_parser = subparsers.add_parser('version', help='print version')
    version_parser.set_defaults(func=version_command)

    return parser


def create_client(args):
    trace=None
    if args.trace:
        trace=trace_modbus_rtu

    client = BsmClientDevice(slave_id=args.unit, name=args.device,
        baudrate=args.baud, timeout=args.timeout, max_count=args.chunk_size,
        trace=trace)
    return client


def dict_get_case_insensitive(d, search_key):
    matches = [k for k in d.keys() if k.lower() == search_key.lower()]
    matches_len = len(matches)

    if matches_len == 0:
        return d.get(search_key)
    elif matches_len == 1:
        return d.get(matches[0])
    else:
        raise ValueError('Ambigous key \'{}\'.'.format(search_key))


def hex_data_or_file(arg):
    hex_digits = set(string.hexdigits)
    if all(c in hex_digits for c in arg):
        return bytes.fromhex(arg)
    else:
        return open(arg, 'rb').read()


def into_chunks(array, length):
    for i in range(0, len(array), length):
        yield array[i:i + length]


def lookup_model(client, name):
    model = next(filter(lambda x: x.model_type.name.lower() == name.lower(),
        client.models_list), None)

    if not model:
        model = dict_get_case_insensitive(client.model_aliases, name)

    return model


def lookup_model_and_point(client, model_name, point_id):
    model = lookup_model(client, model_name)
    point = None

    if model:
        point = lookup_point_in_model(model, point_id)

    return (model, point)


def lookup_point_in_model(model, point_id):
    return next(filter(lambda x: x.point_type.id.lower() == point_id.lower(),
        model.points_list), None)


def lookup_snapshot(client, name):
    return dict_get_case_insensitive(client.snapshot_aliases, name)


def md_trace_print(string):
    for line in string.splitlines():
        print(line)


def model_name_and_point_id_for_path(path):
    components = path.split('/')

    if len(components) < 1 or len(components) > 2:
        raise ValueError('Unsupported path \'{}\'.')

    model_name = components[0]
    point_id = None
    if len(components) == 2:
        point_id = components[1]

    return (model_name, point_id)


def print_block_data(block, indent=MODEL_DATA_INDENT):
    for point in block.points_list:
        print_point_data(point, prefix=indent)


def print_model_data(model, indent=MODEL_DATA_INDENT):
    first = model.blocks[0]
    repeating = model.blocks[1:]

    print('{}:'.format(model.model_type.name))
    if len(model.blocks) == 1:
        print_block_data(first, indent)
    else:
        device = model.device

        print('{}fixed:'.format(indent))
        print_block_data(first, 2 * indent)

        if device.has_repeating_blocks_blob_layout(model):
            data = device.repeating_blocks_blob(model)
            blob_id = device.repeating_blocks_blob_id(model)
            print('{}repeating blocks blob:'.format(indent))
            print('{}{}: {}'.format(2 * indent, blob_id, data.hex()))
        else:
            print('{}repeating:'.format(indent))
            for index, block in enumerate(repeating):
                print('{}{}:'.format(2 * indent, index))
                print_block_data(block, 3 * indent)


def print_point_data(point, prefix=''):
    print('{}{}'.format(prefix, fmt.format_point(point)))


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
    # TODO: What about adding some spaces around the payload?
    #
    # TODO: What about creating a feature request for "pretty tracing"? In the
    # sense that the trace function gets device, addres, payload data passed
    # separately for formatting?
    print(string)




#
# Program commands.
#

def list_model_instances_command(args):
    line_format = '{:<8} {:<8} {:<8} {:<16} {}'
    client = create_client(args)

    print(line_format.format('Offset', 'ID', 'Payload', 'Name', 'Aliases'))

    for index, model in enumerate(client.models_list):
        name = ''
        rendered_aliases = ''

        if model.model_type != None:
            name = model.model_type.name

        aliases = client.aliases_list[index]
        if aliases:
            rendered_aliases = ', '.join(aliases)

        print(line_format.format(model.addr - 2, model.id, model.len, name,
            rendered_aliases))

    client.close()


def dump_command(args):
    client = create_client(args)

    data = client.read(args.offset, args.length)
    print(register_hexdump_bytes(data, args.offset))

    client.close()


def get_command(args):
    client = create_client(args)

    for path in args.paths:
        (model_name, point_id) = model_name_and_point_id_for_path(path)

        # TODO: Reuse models already read for this command.
        model = lookup_model(client, model_name)
        if not model:
            print('Unknown model \'{}\'.'.format(model_name), file=sys.stderr)
            sys.exit(1)

        model.read_points()

        if point_id:
            point = lookup_point_in_model(model, point_id)
            if not point:
                print('Unknown data point \'{}\' in model \'{}\'.'.format(point_id, model_name),
                    file=sys.stderr)
                sys.exit(1)

            prefix = '{}/'.format(model.model_type.name)
            print_point_data(point, prefix=prefix)
        else:
            print_model_data(model)

    client.close()



def set_command(args):
    client = create_client(args)
    models_to_write = set()

    for path_value in args.path_value_pairs:
        (path, value) = tuple(path_value.split('=', 1))
        (model_name, point_id) = model_name_and_point_id_for_path(path)
        (model, point) = lookup_model_and_point(client, model_name, point_id)

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
        if snapshot != None:
            print('Updating \'{}\' succeeded'.format(args.name))
            print('Snapshot data:')
            print_model_data(model)
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


def verify_signature_command(args):
    # The following example will be verified successfully:
    #
    #     public key:     6858b701931d153524d03b28f8b2758d33dd6f76282184ad825e31283e076e1f8c1747f16f9df5b5123594fe867b282a2fb5ab704d5230445cc820e3880b4db7
    #     signature:      5d3c7fbdc68c0484475b15051f51192230f37c3590de7060f31f7c07137089fa35fae5dd765f558680762acc65e35e71e5862370ad1da8cbe87a8e22cb6418eb
    #     message digest: 6bdab37edc9f9b29c125056eed1d7506b5f346743306eac2e3ae6789adda746d
    #

    if cutil.verify_signed_digest(config.BSM_CURVE, config.BSM_MESSAGE_DIGEST, args.public_key, args.signature, args.message_digest):
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
