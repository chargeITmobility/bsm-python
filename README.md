# Bauer BSM-WS36A-H01-1311-0000 Python Interface and Modbus Tool

## Overview

This package contains a Python 3 library and a command line tool for
interacting with a BSM-WS36A-H01-1311-0000. Both allow you to explore the
communication and common tasks like:

* Reading data from registers
* Setting parameters
* Creating snapshots
* Verifying a snapshot signature

So this package might come in handy for testing communication and integrating
the meter in your environment.

The command line tool gets installed as `bsmtool`.


## Prerequisites

* Python 3
    * We have tested it with 3.7 and 3.8
    * We recommend version 3.8

* [pySunSpec](https://github.com/sunspec/pysunspec/)
    * As there is currently no package available at pypi.org, we integrated it
      as `bauer_bsm.sunspec`


## Installation

* We are working on releasing an official package on pypi.org
* Until then
    * You can install it from GitHub
      ```
      $ pip3 install git+https://github.com/chargeITmobility/bsm-python
      ```
    * Or for hands on work from a clone of the repository above
      ```
      bsm-python$ pip3 install --user --editable .
      ```


## Getting help

To display the built-in help for the tool and general arguments use:
```
$ bsmtool --help
```
To get help for an individual subcommand, give `--help` after the subcommand.
For example for help on creating and fetching snapshots use:
```
$ bsmtool get-snapshot --help
```
