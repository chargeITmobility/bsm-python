# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


def dict_get_case_insensitive(d, search_key):
    matches = [k for k in d.keys() if k.lower() == search_key.lower()]
    matches_len = len(matches)

    if matches_len == 0:
        return d.get(search_key)
    elif matches_len == 1:
        return d.get(matches[0])
    else:
        raise ValueError('Ambigous key \'{}\'.'.format(search_key))
