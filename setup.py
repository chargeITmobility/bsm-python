#!/usr/bin/env python3


from setuptools import setup, find_packages


setup(
    name='bauer_bsm',
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'ecdsa',
        'hexdump',
        'pymodbus',
        'six',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bsmtool=bauer_bsm.cli.bsmtool:main',
            'bsmverify=bauer_bsm.cli.sign_verify:main',
        ],
    },

    use_scm_version={
        'write_to': 'bauer_bsm/cli/version.py',
    },

    # TODO: Add package description and metadata.
)
