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

* Several Python packages listed in `requirements.txt`. You may install them as follows:
```
$ pip3 install -r requirements.txt
```


# Getting help

To display the built-in help for the tool and general arguments use:
```
$ ./mbtool --help
```
To get help for an individual subcommand, give `--help` after the subcommand.
For example for help on creating and fetching snapshots use:
```
$ ./mbtool get-snapshot --help
```
