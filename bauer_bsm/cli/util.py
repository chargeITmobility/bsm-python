# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..bsm import config
from ..bsm import format as fmt
from ..crypto import util as cryptoutil

import argparse
import string
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


MODEL_DATA_INDENT = '    '
BSM_MODEL_ID = 64900


def auto_bool(x):
    if isinstance(x, bool) or x is None:
        return x

    lower = x.lower()
    if lower in ['true', 't', 'yes', 'y', '1']:
        return True
    elif lower in ['false', 'f', 'no', 'n', '0']:
        return False
    else:
        raise argparse.ArgumentTypeError('Could not interpret \'{}\' as bool'.format(x))


def auto_int(x):
    result = None

    if isinstance(x, int):
        # Pass-through integer values.
        result = x
    elif x is not None:
        # Parse everything else but 'None' with auto base detection.
        result = int(x, 0)

    return result


def hex_data_or_file(arg):
    hex_digits = set(string.hexdigits)
    if all(c in hex_digits for c in arg):
        return bytes.fromhex(arg)
    else:
        return open(arg, 'rb').read()


def model_name(model):
    if model.model_type is not None:
        return model.model_type.name
    else:
        return 'unknown model {}'.format(model.id)


def model_name_and_point_id_for_path(path):
    components = path.split('/')

    if len(components) < 1 or len(components) > 2:
        raise ValueError('Unsupported path \'{}\'.')

    model_name = components[0]
    point_id = None
    if len(components) == 2:
        point_id = components[1]

    return (model_name, point_id)


def print_blob_data(model, indent=MODEL_DATA_INDENT, prefix='', pk_format='sec1-uncompressed'):
    device = model.device
    rendered = render_blob_data(model, pk_format=pk_format)
    blob_id = device.repeating_blocks_blob_id(model)

    if model.model_type.id == BSM_MODEL_ID:
        print('{}{}{} ({}): {}'.format(indent, prefix, blob_id,
            pk_format.lower(), rendered))
    else:
        print('{}{}{}: {}'.format(indent, prefix, blob_id, rendered))


def print_block_data(block, indent=MODEL_DATA_INDENT):
    for point in block.points_list:
        print_point_data(point, prefix=indent)


def print_model_data(model, indent=MODEL_DATA_INDENT, verbose=False, pk_format=cryptoutil.PUBLIC_KEY_DEFAULT_FORMAT):
    first = model.blocks[0]
    repeating = model.blocks[1:]

    print('{}:'.format(model.model_type.name))

    # Print model header upon request.
    if verbose:
        print('{}ID: {}'.format(indent, model.model_type.id))
        print('{}L: {}'.format(indent, model.model_type.len))

    # Print simplified representation for models just containg a fixed block.
    if len(model.blocks) == 1:
        print_block_data(first, indent)
    else:
        device = model.device

        print('{}fixed:'.format(indent))
        print_block_data(first, 2 * indent)

        if device.has_repeating_blocks_blob_layout(model):
            print('{}repeating blocks blob:'.format(indent))
            print_blob_data(model, 2 * indent, pk_format=pk_format)
        else:
            print('{}repeating:'.format(indent))
            for index, block in enumerate(repeating):
                print('{}{}:'.format(2 * indent, index))
                print_block_data(block, 3 * indent)


def print_point_data(point, prefix=''):
    print('{}{}'.format(prefix, fmt.format_point(point)))


def render_blob_data(model, pk_format='der'):
    device = model.device
    data = device.repeating_blocks_blob(model)

    if model.model_type.id == BSM_MODEL_ID:
        if PY3:
            return cryptoutil.public_key_data_from_blob(data,
                config.BSM_MESSAGE_DIGEST, output_format=pk_format).hex()
        if PY2:
            return cryptoutil.public_key_data_from_blob(data,
                config.BSM_MESSAGE_DIGEST, output_format=pk_format).encode('hex')
    else:
        if PY3:
            return data.hex()
        if PY2:
            return data.encode('hex')
