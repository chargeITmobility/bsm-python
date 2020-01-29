# YOUR_PRODUCT_NAME_HERE Modbus Tool

# Overview

This tool facilitates Modbus communication with YOUR_PRODUCT_NAME_HERE from the
command line. It also demonstrates several interesting aspects like:

* Reading data from registers
* Setting parameters
* Creating snapshots
* Verifying a snapshot signature

So it might come in handy for testing communication and integrating the meter
in your environment.


# Prerequisites

* Python 3
    * We have tested it with 3.7 and 3.8
    * We recommend version 3.8


# Installation

* From a pre-built distribution package
```
$ pip3 install --user bauer_bsm-YOUR_VERSION_HERE-py3-none-any.whl
```

* For development directly from this repository
```
$ pip3 install --user --editable .
```

* Omit the argument `--user` for installing this package globally/for
  all users on your system.


# Getting help

To display the built-in help for the tool and general arguments use:
```
$ bsmtool --help
```
To get help for an individual subcommand, give `--help` after the subcommand.
For example for help on creating and fetching snapshots use:
```
$ bsmtool get-snapshot --help
```
