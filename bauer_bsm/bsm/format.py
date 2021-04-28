# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


def format_point(point):
    return '{}: {}'.format(point.point_type.id, format_point_value(point))


def format_point_value(point):
    unit = ''

    if point.value is not None and point.point_type.units:
        unit = ' {}'.format(point.point_type.units)

    return '{}{}'.format(point.value, unit)
