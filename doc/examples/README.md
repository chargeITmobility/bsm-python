# Bauer BSM-WS36A-H01-1311-0000 Examples

## Overview

These are examples demonstrating how to use the BSM-WS36A-H01-1311-0000 (short
BSM-WS36A) and the tools provided by its Python support.

[Notation](notation.md) describes the notation used here. The examples assume a
certain hard- and software setup presented in the
[prerequisites](prerequisites.md).

> **Note:** This is a pre-release and some things might change for the final
> product.


## Modbus Interface

This set of examples demontrates how to interact with the device's [Modbus
interface](modbus-interface.md). Most use cases could be easily explored using
the [BSM Tool](bsmtool.md).


## Examples

The examples assume that you have configured the RS-485 (nowadays officially
named EIA-485) device for communicating with the BSM-WS36A via the [environment
variable](bsmtool.md#environment-variables) `BSMTOOL_DEVICE`.  If not otherwise
stated, [default communication
parameters](modbus-interface.md#default-communication-parameters) are used,
thus not requiring to explicitly specify them when invoking the BSM Tool.

Let's dive into the actual examples:

- [Changing Communication Parameters](communication-parameters.md)
    - [Changing the Device Address](communication-parameters.md#changing-the-device-address)
    - [Changing the Baud Rate](communication-parameters.md#changing-the-baud-rate)
    - [Changing Device Address and Baud Rate at the Same Time](communication-parameters.md#changing-device-address-and-baud-rate-at-the-same-time)
- [Setting and Updating Time](time.md)
    - [Daylight Saving Time](time.md#daylight-saving-time)
    - [Terminology](time.md#terminology)
    - [Initially Setting Time](time.md#initially-setting-time)
    - [Updating Time](time.md#updating-time)
    - [Starting to Observe Daylight Saving Time](time.md#starting-to-observe-daylight-saving-time)
- [Signed Snapshots](snapshots.md)
    - [Snapshot Creation](snapshots.md#snapshot-creation)
    - [Snapshot Data](snapshots.md#snapshot-data)
    - [Public Key](snapshots.md#public-key)
    - [Snapshot Verification](snapshots.md#snapshot-verification)
- [Open Charge Metering Format (OCMF)](ocmf.md)
    - [Snapshots and Their Associated OCMF Representation](ocmf.md#snapshots-and-their-associated-ocmf-representation)
    - [Getting the OCMF Representation](ocmf.md#getting-the-ocmf-representation)
    - [Snapshot Data in OCMF](ocmf.md#snapshot-data-in-ocmf)
    - [Example](ocmf.md#example)
    - [Comparing Snapshot and OCMF Payload](ocmf.md#comparing-snapshot-and-ocmf-payload)
    - [OCMF XML](ocmf.md#ocmf-xml)
- [Electric Vehicle Charging](ev-charging.md)
    - [Typical Setup](ev-charging.md#typical-setup)
    - [Charging Scenario](ev-charging.md#charging-scenario)


## Use the Source, Luke

You could also consult and debug the source code in this repository. The BSM
Python client could be found in
[`bauer_bsm/bsm/client.py`](../../bauer_bsm/bsm/client.py). Following
[pySunSpec](https://github.com/sunspec/pysunspec), there are two interfaces:

- [`BsmClientDevice`](../../bauer_bsm/bsm/client.py#L103) meant for general use
  which follows the interface from pySunSpec's `ClientDevice`
- [`SunSpecBsmClientDevice`](../../bauer_bsm/bsm/client.py#L421) which provides
  models and their data points directly as object attributes/properties as
  pySunSpec's `SunSpecClientDevice` and might come in handy for scripting

To see them in action, you could have a look at the BSM Tool's sources in
[`bauer_bsm/cli/bsmtool.py`](../../bauer_bsm/cli/bsmtool.py).
