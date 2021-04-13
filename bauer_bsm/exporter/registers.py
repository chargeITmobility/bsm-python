# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..sunspec.core import suns
import re




_HEADER_BLOCK_TYPE = 'header'
_SYMBOL_POINT_TYPES = [
        suns.SUNS_TYPE_BITFIELD16,
        suns.SUNS_TYPE_BITFIELD32,
        suns.SUNS_TYPE_ENUM16,
        suns.SUNS_TYPE_ENUM32,
    ]




def _cleanup_model_string(string, none=None):
    if string is None:
        return none

    string = re.sub(r'\s+', ' ', string)
    string = string.strip()

    return string


def _write_model_header_rows(writer, model_type, base_addr):
    writer.writerow([
            _HEADER_BLOCK_TYPE,
            None,
            base_addr - 2,
            0,
            1,
            'ID',
            'Model ID',
            model_type.id,
            suns.SUNS_TYPE_UINT16,
            None,
            None,
            suns.SUNS_ACCESS_R,
            suns.SUNS_MANDATORY_TRUE,
            None,
            None,
        ])
    writer.writerow([
            _HEADER_BLOCK_TYPE,
            None,
            base_addr - 1,
            1,
            1,
            'L',
            'Model Payload Length',
            model_type.len,
            suns.SUNS_TYPE_UINT16,
            None,
            None,
            suns.SUNS_ACCESS_R,
            suns.SUNS_MANDATORY_TRUE,
            None,
            None,
        ])


def _write_point_type_row(writer, block_type, point_type, base_addr, base_offset):
    writer.writerow([
            block_type.type,
            None,
            base_addr + point_type.offset,
            base_offset + point_type.offset,
            point_type.len,
            point_type.id,
            point_type.label,
            point_type.value_default,
            point_type.type,
            point_type.units,
            point_type.sf,
            point_type.access,
            point_type.mandatory,
            _cleanup_model_string(point_type.description),
            _cleanup_model_string(point_type.notes),
        ])


def _write_symbol_rows(writer, point_type):
    # TODO: There are duplicate entries for certain symbols like they show up
    # in the SunSpec model documentation. Does this originate from the symbol
    # definition in the model and the separate strings? What about cleaning
    # this up?
    for symbol in point_type.symbols:
        writer.writerow([
                point_type.type,
                point_type.id,
                None,
                None,
                None,
                symbol.id,
                symbol.label,
                symbol.value,
                None,
                None,
                None,
                None,
                None,
                _cleanup_model_string(symbol.description),
                _cleanup_model_string(symbol.notes),
            ])


def write_register_overview_csv(client, writer):
    """
    Writes the complete Modbus register layout from model data as CSV using the
    supplied CSV writer.
    """
    writer.writerow(['Bauer BSM-WS36A-H01-1311-0000 Modbus Register Overview'])

    for model in client.models_list:
        fixed_block = model.model_type.fixed_block
        repeating_block = model.model_type.repeating_block
        model_type = model.model_type
        base_addr = model.addr
        symbol_points = []

        writer.writerow([])
        writer.writerow([])

        writer.writerow(['Model Instance: {}'.format(client.model_instance_label(model))])
        writer.writerow(['Model: {}'.format(_cleanup_model_string(model_type.label, none=''))])
        writer.writerow(['Description: {}'.format(_cleanup_model_string(model_type.description, none=''))])
        writer.writerow(['Notes: {}'.format(_cleanup_model_string(model_type.notes, none=''))])

        writer.writerow([])
        writer.writerow([
                'Field Type',
                'Applicable Point',
                'Address',
                'Address Offset',
                'Size',
                'Name',
                'Label',
                'Value',
                'Type',
                'Units',
                'Scale Factor',
                'Access',
                'Mandatory',
                'Description',
                'Notes',
            ])

        _write_model_header_rows(writer, model_type, base_addr)
        writer.writerow([])

        for point_type in fixed_block.points_list:
            _write_point_type_row(writer, fixed_block, point_type, base_addr, 2)
            if point_type.type in _SYMBOL_POINT_TYPES:
                symbol_points.append(point_type)

        if repeating_block is not None:
            fixed_block_length = int(fixed_block.len)
            base_addr = base_addr + fixed_block_length

            writer.writerow([])

            for point_type in repeating_block.points_list:
                _write_point_type_row(writer, repeating_block, point_type, base_addr, 0)
                if point_type.type in _SYMBOL_POINT_TYPES:
                    symbol_points.append(point_type)

        for symbol_point in symbol_points:
            writer.writerow([])
            _write_symbol_rows(writer, symbol_point)
