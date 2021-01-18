# Bauer BSM-WS36A-H01-1311-0000 Examples

## Overview

These are examples demonstrating how to use the BSM-WS36A-H01-1311-0000 (short
BSM-WS36A) and the tools provided by its Python support.

[Notation](notation.md) describes the notation used here. The examples assume a
certain hard- and software setup presented in the
[prerequisites](prerequisites.md).


## Modbus Interface

This set of examples demontrates how to interact with the device's [Modbus
interface](modbus-interface.md). Most use cases could be easily explored using
the [BSM Tool](bsmtool.md).


## Examples

The examples assume that you have configured the RVS-485 device for
communicating with the BSM-WS36A via the [environment
variable](bsmtool.md#environment-variables) `BSMTOOL_DEVICE`.  If not otherwise
stated, [default communication
parameters](modbus-interface.md#default-communication-parameters) are used,
thus not requiring to explicitly specify them when invoking the BSM Tool.

Let's dive into the actual examples:

- [Changing Communication Parameters](communication-parameters.md)
- [Setting and Updating Time](time.md)
- [Signed Snapshots](snapshots.md)
- [Open Charge Metering Format (OCMF)](ocmf.md)
- [Electric Vehicle Charging](ev-charging.md)


## Use the Source, Luke

You could also consult and debug the source code in this repository. The BSM
Python client could be found in
[`bauer_bsm/bsm/client.py`](../../bauer_bsm/bsm/client.py). Following
[pySunSpec](https://github.com/sunspec/pysunspec), there are two interfaces:

- [`BsmClientDevice`](../../bauer_bsm/bsm/client.py#L103) meant for general use
  which follows the interface from pySunSpec's `ClientDevice`
- [`SunSpecBsmClientDevice`](../../bauer_bsm/bsm/client.py#L468) which provides
  models and their data points directly as object attributes/properties as
  pySunSpec's `SunSpecClientDevice` and might come in handy for scripting

To see them in action, you could have a look at the BSM Tool's sources in
[`bauer_bsm/cli/bsmtool.py`](../../bauer_bsm/cli/bsmtool.py).
