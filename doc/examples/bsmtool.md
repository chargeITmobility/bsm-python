# The BSM Tool

The BSM Tool facilitates testing and developing with the BSM-WS36A. It supports
common tasks like reading out and setting data and more complex scenarios like
verifying digital signatures.

This tool is open source, and allows you to inspect what is going on under the
hood in detail. It also allows to print a trace of the Modbus communication
using the option `--trace`.


## Installation

The [prerequisites](prerequisites.md) show the installation of the Python
runtime environment and the tool itself.


## Usage

The BSM Tool displays general usage information when invoking it with the
option `--help`:
```
$ bsmtool --help
usage: bsmtool [-h] --device DEVICE [--baud BAUD] [--timeout SECONDS] [--unit UNIT]
               [--chunk-size REGISTERS] [--trace] [--verbose]
               [--public-key-format {der,raw,sec1-compressed,sec1-uncompressed}]
               COMMAND ...

BSM Modbus Tool

positional arguments:
  COMMAND               sub commands
    models              list SunSpec model instances
    export              export register layout
    get                 get individual values
    set                 set values
    create-snapshot     create snapshot but don't fetch data
    get-snapshot        create snapshot and fetch data
    verify-snapshot     verify snapshot signature (but do not create it)
    verify-signature    verify arbitrary signature for a given public key and digest
    ocmf-xml            generate OCMF XML from already existing snapshots (stons and stoffs)
    dump                dump registers
    version             print version

optional arguments:
  -h, --help            show this help message and exit
  --device DEVICE       serial device
  --baud BAUD           serial baud rate
  --timeout SECONDS     request timeout
  --unit UNIT           Modbus RTU unit number
  --chunk-size REGISTERS
                        maximum amount of registers to read at once
  --trace               trace Modbus communication (reads/writes)
  --verbose             give verbose output
  --public-key-format {der,raw,sec1-compressed,sec1-uncompressed}
                        output format of ECDSA public key (see RFC 5480 for DER and SEC1 section
                        2.3.3 for details about formats)

You may specify communication parameters also by environment variables. Use BSMTOOL_DEVICE,
BSMTOOL_BAUD, BSMTOOL_UNIT, BSMTOOL_TIMEOUT, and BSMTOOL_CHUNK.
```
This also gives an overview over the available commands. To get more
information about a command, invoke the command with the option `--help`:
```
$ bsmtool get-snapshot --help
usage: bsmtool get-snapshot [-h] name

positional arguments:
  name        snapshot model instance alias (see output of 'models')

optional arguments:
  -h, --help  show this help message and exit
```


## Environment Variables

The BSM Tool allows to configure defaults for several parameters by means of
environment variables. [`bsmtool --help`](#usage) lists the supported
variables.

The examples assume having `BSMTOOL_DEVICE` set to specify the serial device
for communicating with the BSM-WS36A. For example, you could set this variable
to use `COM1` on Windows with
```
> set BSMTOOL_DEVICE=COM1
```
and `/dev/ttyUSB0`  on Linux and macOS with:
```
$ export BSMTOOL_DEVICE=/dev/ttyUSB0
```
Your actual device name may vary.
