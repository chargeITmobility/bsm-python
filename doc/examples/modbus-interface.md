# BSM-WS36A Modbus Interface

## Default Communication Parameters

The BSM-WS36A provides a Modbus RTU interface via RS-485 with the default
communication parameters:

- 8 data bits, 1 stop bit, even parity (8E1)
- 19,200 Baud
- Device address 42

The device supports the following baud rates 1200, 2400, 4800, 9600, 19200,
38400, 57600, 115200, 230400, 460800, and 921600 and device addresses from 1 to
247. Section [Changing Communication Parameters](communication-parameters.md)
shows how to change them.


## Data Access

Data on the device could be read via the Modbus function _Read Holding
Registers_ (function code 3) and written via _Preset Multiple Registers_
(function code 10).

Writing to read-only data points/registers is ignored. This allows to set
multiple non-adjacent data points in one transaction/write request which might
come in handy when for example [changing communication
parameters](communication-parameters.md).


## Data Models

The BSM-WS36A provides an interface geared to the [SunSpec
Alliance](https://sunspec.org)'s information models. See the following
specifications for more details:

- [_SunSpec Modbus Technology Overview_](https://sunspec.org/sunspec-modbus-technology-overview/)
- [_SunSpec Information Model Specification_](https://sunspec.org/sunspec-information-model-specification/)
- [_SunSpec Information Model Reference_](https://sunspec.org/sunspec-information-model-reference/)

XML definitions of the models used by the BSM-WS36A could be found here:

- [SunSpec Alliance](https://github.com/sunspec/models/tree/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx)
- [Custom BSM Models](../../bauer_bsm/bsm/models)


## Register Addresses

_“The good thing about standards is that there are so many to choose from.”_ (Andrew S. Tanenbaum)

Modbus uses two different types of addressing schemes: Data addresses starting at
one and protocol addresses (on the wire) starting from zero. So for example, the
data address 40,001 will be encoded as 40,000 == 0x9c40 within an Modbus RTU
frame on the wire. See [_Modicon Modbus Protocol Reference
Guide_](https://modbus.org/docs/PI_MBUS_300.pdf) chapter 2, section _Data
Addresses in Modbus Messages_.


## Model Instances

The BSM-WS36A provides the following model instances:

| Start Address | Model ID | Payload Registers | Label                              | Model Name                                                                                                       | Instance Aliases                           |
| ------------: | -------: | ----------------: | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| 40003         | 1        | 66                | Common                             | [common](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml)    | common, cb                                 |
| 40071         | 10       | 4                 | Serial Interface Header            | [model\_10](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00010.xml) | serial\_interface\_header, sih             |
| 40077         | 17       | 12                | Serial Interface                   | [model\_17](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00017.xml) | serial\_interface, si                      |
| 40091         | 203      | 105               | AC Meter (Three Phase)             | [ac\_meter](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00203.xml) | ac\_meter, tpm                             |
| 40198         | 64900    | 300               | Signing Meter                      | [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml)                                                                 | bs\_meter, bsm, sm                         |
| 40500         | 64902    | 20                | Communication Module Firmware Hash | [bsm\_blob](../../bauer_bsm/bsm/models/smdx_64902.xml)                                                           | cm\_firmware\_hash, cfwh                   |
| 40522         | 64901    | 252               | Signed Current Snapshot            | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml)                                                       | signed\_current\_snapshot, scs             |
| 40776         | 64901    | 252               | Signed Turn-On Snapshot            | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml)                                                       | signed\_turn\_on\_snapshot, stons          |
| 41030         | 64901    | 252               | Signed Turn-Off Snapshot           | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml)                                                       | signed\_turn\_off\_snapshot, stoffs        |
| 41284         | 64903    | 372               | OCMF Signed Current Snapshot       | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml)                                                           | ocmf\_signed\_current\_snapshot, oscs      |
| 41658         | 64903    | 372               | OCMF Signed Turn-On Snapshot       | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml)                                                           | ocmf\_signed\_turn\_on\_snapshot, ostons   |
| 42032         | 64903    | 372               | OCMF Signed Turn-Off Snapshot      | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml)                                                           | ocmf\_signed\_turn\_off\_snapshot, ostoffs |

Each model starts with a two register header followed by the given number of
payload registers. The individual data point start addresses can be computed as

> _Data Point Start Address_ = _Model Start Address_ + 2 + _Data Point Offset_

where the model start address is taken from the table above and the data point
offset from the linked model definitions. They are also provided in the user
manual.

For example, the address of the device address
[_DA_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml#L10)
data point with offset 64 from the [common
model](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml)
starting at 40003 computes as:

> 40069 = 40003 + 2 + 64

The BSM-WS36A instantiates models multiple times for the different snapshots or
OCMF data. Instance aliases are provided by the Python support and the BSM Tool
for accessing all model instances by a name. For example, the _Signed Turn-On
Snapshot_ could read with the BSM Tool as follows:
```
$ bsmtool --device=$BSMTOOL_DEVICE stons
```

The BSM Tool allows to print the actual model instances and the table above has
been generated from this data. Note that the output from the BSM Tool gives
protocol addresses and not data addresses.
```
$ bsmtool models
Address  ID       Payload  Label                                    Name             Aliases
40002    1        66       Common                                   common           common, cb
40070    10       4        Serial Interface Header                  model_10         serial_interface_header, sih
40076    17       12       Serial Interface                         model_17         serial_interface, si
40090    203      105      AC Meter                                 ac_meter         ac_meter, tpm
40197    64900    300      Signing Meter                            bsm              bs_meter, bsm, sm
40499    64902    20       Communication Module Firmware Hash       bsm_blob         cm_firmware_hash, cfwh
40521    64901    252      Signed Current Snapshot                  bsm_snapshot     signed_current_snapshot, scs
40775    64901    252      Signed Turn-On Snapshot                  bsm_snapshot     signed_turn_on_snapshot, stons
41029    64901    252      Signed Turn-Off Snapshot                 bsm_snapshot     signed_turn_off_snapshot, stoffs
41283    64903    372      OCMF Signed Current Snapshot             bsm_ocmf         ocmf_signed_current_snapshot, oscs
41657    64903    372      OCMF Signed Turn-On Snapshot             bsm_ocmf         ocmf_signed_turn_on_snapshot, ostons
42031    64903    372      OCMF Signed Turn-Off Snapshot            bsm_ocmf         ocmf_signed_turn_off_snapshot, ostoffs
```

## Data Representation

### Standard Representation

The [_SunSpec Information Model
Specification_](https://sunspec.org/sunspec-information-model-specification/)
describes the interpretation of standard data types.


### Binary Data

The BSM-WS36A provides several data as Binary Large Objects (BLOBs) - for
example, its [public key](../../bauer_bsm/bsm/models/smdx_64900.xml#L31) and
[snapshot signatures](../../bauer_bsm/bsm/models/smdx_64901.xml#L65).

SunSpec does not define a data representation for BLOBs and so a proprietary
[bsm\_blob](../../bauer_bsm/bsm/models/smdx_64902.xml) or a similar arrangement
of data points at the end of other models like at the ones above. For example:
representation is used. Either by the specialized BLOB model

- [_NB_](../../bauer_bsm/bsm/models/smdx_64902.xml#L41) giving the number of
  Modbus registers _B_ forming the BLOB data area

- [_BB_](../../bauer_bsm/bsm/models/smdx_64902.xml#L49) the actual number of
  bytes

- [_B_](bauer_bsm/bsm/models/smdx_64902.xml#L53) a repeating block with a
  single register of this name forming the BLOB data area

See [Signed Snapshots](snapshots.md) for an example.
