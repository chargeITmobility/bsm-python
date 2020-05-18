#!/usr/bin/env python3
#
# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from setuptools import setup, find_packages


# We have a dependency to pySunSpec which is not distributed via pypi.org.
# Dependency links for having a dependency to a Git repo are deprecated so
# we've assimilated it as a submodule as follows:
#
#     1. We include it as a Git submodule under 'external'.
#
#     2. We symlink to the actual 'sunspec' module from our top-level module.
#
#     3. We've incorporated the relevant settings from pySunSpec's setup.py
#        into ours.
#
# Suggestions for improvements are welcome.


setup(
    name='bauer_bsm',
    setup_requires=[
        'setuptools_scm',
    ],
    # pySunSpec requires Python 3 in version 3.5 or greater. As we do not test
    # on Python 2, we ignore the Python 2 support from pySunSpec.
    python_requires='>=3.5',
    install_requires=[
        'ecdsa',
        'pyserial',
    ],
    packages=find_packages(),
    # Include model data from pySunSpec and us.
    package_data={
        'bauer_bsm.bsm': ['models/*'],
        'bauer_bsm.sunspec': ['models/smdx/*'],
    },
    entry_points={
        'console_scripts': [
            'bsmtool=bauer_bsm.cli.bsmtool:main',
        ],
    },

    use_scm_version={
        'write_to': 'bauer_bsm/version.py',
    },

    # TODO: Add package description and metadata.
)
