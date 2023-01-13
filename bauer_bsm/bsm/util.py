# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


def array_chunks(array, length):
    for i in range(0, len(array), length):
        yield array[i:i + length]


def dict_get_case_insensitive(d, search_key):
    matches = [k for k in d.keys() if k.lower() == search_key.lower()]
    matches_len = len(matches)

    if matches_len == 0:
        return d.get(search_key)
    elif matches_len == 1:
        return d.get(matches[0])
    else:
        raise ValueError('Ambigous key \'{}\'.'.format(search_key))


def register_hex_string(data, reg_separator=' '):
    return reg_separator.join(map(lambda x: '{:02x}{:02x}'.format(x[0], x[1]), zip(data[::2], data[1::2])))


def register_hexdump_bytes(data, offset=0):
    chunk_regs = 8
    chunk_length = 2 * chunk_regs

    start = offset
    lines = []

    for chunk in array_chunks(data, chunk_length):
        # Hex data of registers.
        hex_chunk = register_hex_string(chunk, reg_separator=' ')
        # Printable characters from data.
        printable = ''.join(map(lambda x: chr(x) if x >= 32 and x < 127 else '.', chunk))

        lines.append('{:8}: {:40} {}'.format(start, hex_chunk, printable))
        start += chunk_regs

    return '\n'.join(lines)
