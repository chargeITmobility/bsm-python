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
    * We have tested it with 3.7 and 3.9
    * See [Prerequisites](doc/examples/prerequisites.md#python-3) for details

* [pySunSpec](https://github.com/sunspec/pysunspec/)
    * As there is currently no package available at pypi.org, we integrated it
      as `bauer_bsm.sunspec`


## Installation

* You can install the latest release from GitHub:
  ```
  $ pip3 install https://github.com/chargeITmobility/bsm-python/releases/download/release-0.11.1/bauer_bsm-0.11.1-py3-none-any.whl
  ```

* For hands-on work of the code, clone this repository and perform a editable installation as follows:
  ```
  $ pip3 install --user --editable .
  ```


## Getting Help

### Built-In Tool Help

To display the built-in help for the tool and general arguments use:
```
$ bsmtool --help
```
To get help for an individual subcommand, give `--help` after the subcommand.
For example for help on creating and fetching snapshots use:
```
$ bsmtool get-snapshot --help
```


### Online Examples and Documentation

This repository contains a comprehensive set of examples on using the BSM-WS36A
and the BSM Tool in [`doc/examples`](doc/examples/README.md).

The directory [`doc/modbus`](doc/modbus) contains a Modbus model instance and
register overview.

Finally, you could have a look in the product manuals of the BSM-WS36A:
* [English _Product Manual_](doc/manuals/Product_manual_BSM_EN_210910.pdf)
* [German _Produkthandbuch_](doc/manuals/Produkthandbuch_BSM_DE_v1-01_210910.pdf)
