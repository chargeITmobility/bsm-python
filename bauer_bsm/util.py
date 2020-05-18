# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from importlib import import_module


def package_version():
    version = None

    # Attempt to provide version information on best-effort from the release
    # information.
    try:
        module = import_module('.version', __package__)
        version = module.version
    except ModuleNotFoundError:
        version = 'unreleased'

    return version
