# Changing Communication Parameters

The baud rate and device address can be configured either through the service
button (see BSM-WS36A user manual) or via the Modbus interface itself by
writing to the following data points:

| Model                                                                                                            | Data Point | Type   | Unit | Start Address |
| ---------------------------------------------------------------------------------------------------------------- | ---------- | ------ | ---- | ------------: |
| [common](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml)    | DA         | uint16 |      | 40069         |
| [model\_17](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00017.xml) | Rte        | uint32 | bps  | 40083         |

Changes will take effect after a write gets confirmed by the device. You could
change both parameters at once, by setting both data points in a single write
request.


## Changing the Device Address

The device address could be changed from the default one to 1 using the BSM
Tool as follows:
```
$ bsmtool set cb/da=1
```
```
--> 2a 10 9c84 0001 02 0001 cf2c
<-- 2a 10 9c84 0001 69ab
```

Switching back to the default address requires explicitly specifying the
current device address:
```
$ bsmtool --unit=1 set cb/da=42
```
```
--> 01 10 9c84 0001 02 002a 65c2
<-- 01 10 9c84 0001 6fb0
```


## Changing the Baud Rate

The baud rate can be changed similar to the device address using the BSM Tool
from the default value to 115,200 bps:
```
$ bsmtool set si/rte=115200
```
```
--> 2a 10 9c92 0002 04 0001c200 0c58
<-- 2a 10 9c92 0002 c86e
```

Switching back to the default baud rate requires explicitly specifying the
current one:
```
$ bsmtool --baud=115200 set si/rte=19200
```
```
--> 2a 10 9c92 0002 04 00004b00 3a08
<-- 2a 10 9c92 0002 c86e
```


## Changing Device Address and Baud Rate at the Same Time

Setting data points from different model instances at the same time is
currently not supported by the BSM Tool. But this could be achieved with the
[PyModbus](https://github.com/riptideio/pymodbus/) console. For example, to
switch to the device address 1 and 115,200 bps from the [default
values](modbus-interface.md#default-communication-parameters) with the BSM Tool, invoke it as
follows:
- Start PyModbus Console
    ```
    $ pymodbus.console serial --port=$BSMTOOL_DEVICE --baudrate=19200 --parity=E --timeout=15
    ```
- Set _DA_ to 1 and _Rte_ to 115,200 in a single write (note that PyModbus uses
  protocol addresses)
    ```
    > client.write_registers unit=42 address=40068 values=1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,49664
    {
        "address": 40068,
        "count": 16
    }
    ```

This will result in the following Modbus write request and acknowledge from the device:
```
--> 2a 10 9c84 0010 20 000100000000000000000000000000000000000000000000000000000001c200 c411
<-- 2a 10 9c84 0010 a9a7
```
From now on the device could be reached with the new communication parameters.
