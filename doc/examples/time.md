# Setting and Updating Time

The BSM-WS36A tracks time with its internal clock as [epoch
time](https://en.wikipedia.org/wiki/Unix_time). Time information needs to
provided externally and updated at a certain interval to maintain valid epoch
time on the device. The device starts up with an invalid epoch time and after
setting time information, it needs to be updated every 24 to 48 hours.

> **Warning:** Updating the time at intervals smaller than 24 h reduces the
> lifetime of the device.

There are two data points for getting, setting, and updating this time
information:

- _Epoch_ representing the seconds since 1970-01-01
- _TZO_ the current time zone offset to
  [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) in minutes

Both data points are located in the single [instance](modbus-interface.md) of
the [_BSM_ model](../../bauer_bsm/bsm/models/smdx_64900.xml):

| Model                                            | Data Point | Type   | Unit | Start Address |
| ------------------------------------------------ | ---------- | ------ | ---- | ------------: |
| [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) | Epoch      | uint32 | s    | 40261         |
| [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) | TZO        | int16  | min  | 40263         |

Initially setting epoch time information, both data points needs to be written.
Later updates may only set either _Epoch_ or _TZO_.


## Daylight Saving Time

The BSM-WS36A does not support daylight saving time rules. Epoch time
information needs to be updated externally at the beginning and end of daylight
saving time observation.


## Terminology

### Setting Time

Setting the time refers to initially setting the time from an invalid state or
providing time information which differs more than the accepted cone of drift
since the last update or setting of epoch time (see user manual for more
details).

Setting time gets registered at two data points:

| Model                                            | Data Point  | Type   | Unit | Start Address |
| ------------------------------------------------ | ----------- | ------ | ---- | ------------: |
| [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) | EpochSetCnt | uint32 |      | 40264         |
| [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) | EpochSetOS  | uint32 | s    | 40266         |

where _EpochSetCnt_ counts the number of times epoch time has been set and
_EpochSetOS_ provides when this happened in operating seconds of the device.


### Updating Time

Updating time refers to providing time information within the accepted cone of
drift since the last updating or setting of time.

Updating time does not get registered.


## Initially Setting Time

After powering up the device, epoch time information needs to be set by
providing both, epoch time _Epoch_ and the timezone offset _TZO_. For setting
the device's time to 2021-01-01 10:00:00 UTC+01:00, the following values need
to be written to the device:

- _Epoch_ = 1609491600 s = 0x5feee490 s
- _TZO_ = 60 min = 0x3c min

To set them with the BSM Tool, invoke it as follows:
```
$ bsmtool set bsm/epoch=1609491600 bsm/tzo=60
```

This will result in the Modbus write request starting at the protocol address
40260 = 0x9d44 (data model address 40261) and an acknowledge from the device:
```
--> 2a 10 9d44 0003 06 5feee490003c d4b0
<-- 2a 10 9d44 0003 e9aa
```
This gets recorded at the epoch time set counter _EpochSetCnt_ and modification
timestamp _EpochSetOS_.


## Updating Time

For updating epoch time information, only the epoch seconds need to be provided
while it is still possible to write epoch seconds and the same timezone offset.

After [initially setting time](#initially-setting-time), it could be updated 24
hours later to

- 2021-01-02 10:00:00 UTC+01:00
- _Epoch_ = 1609578000 s = 0x5ff03610 s

by keeping the already set timezone offset and just writing the epoch seconds
wit the BSM Tool:
```
$ bsmtool set bsm/epoch=1609578000
```
```
--> 2a 10 9d44 0002 04 5ff03610 8855
<-- 2a 10 9d44 0002 286a
```
This update is assumed to be within the accepted cone of drift and therefor
does not get registered at _EpochSetCnt_ and _EpochSetOS_.


## Starting to Observe Daylight Saving Time

To start observing daylight saving time with 2021-03-28 03:00:00 UTC+02:00 you
could keep the actual epoch seconds on the device and just set the new timezone
offset at this point in time:

- _Epoch_ remains 1616893200 = 0x605fd510
- _TZO_ needs to be updated to 120 min = 0x78

This could be done with the BSM Tool as follows:
```
$ bsmtool set bsm/tzo=120
```
```
--> 2a 10 9d46 0001 02 0078 0eec
<-- 2a 10 9d46 0001 c9ab
```
Changing the timezone offset is considered setting the time and gets registered
at _EpochSetCnt_ and _EpochSetOS_.
