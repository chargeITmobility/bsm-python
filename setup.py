#!/usr/bin/env python3


from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as requirements:
        result = [line for line in requirements.readlines() if line and not line.startswith('--')]
    return result


setup(
    name='bauer_bsm',
    install_requires=requirements(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bsmtool=bauer_bsm.cli.mbtool:main',
            'bsmverify=bauer_bsm.cli.sign_verify:main',
        ],
    },

    # TODO: Add package description and metadata.
)
