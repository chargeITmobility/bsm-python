# Notation

## Command Line Interface

These examples make heavy use of a command line interface. Due to Python's
excellent portability this may be on the operating system of your choice:
`cmd.exe` on Windows or your favorite shell on Linux and macOS.

When a shell asks for user input, it presents a prompt whose appearance may
vary: from an angle bracket (`>`) at `cmd.exe` to a dollar (`$`) or percentage
sign (`%`) on Linux or macOS. The examples will use the dollar sign (`$`) to
indicate an input prompt and the example
```
$ bsmtool version
0.11.0
```
means enter `bsmtool version` at your shell prompt and the expected output will
be `0.11.0` here.

There are a few advanced examples command line invocations using [command
pipeline](https://en.wikipedia.org/wiki/Pipeline_(Unix)) (`|`). They work on
typical shells on Linux and macOS but your results on Windows may vary.


## Modbus

### Interaction with the Device

Most of the examples will use the BSM Tool to perform the interaction with the
BSM-WS36A and the actual Modbus frames sent over the wire.  Requests to the
meter are indicated by a right arrow `-->` and responses by a left arrow `<--`.

For example, reading the [common
block](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml),
which could be seen as the electronic nameplate of the device is done by invoking
```
$ bsmtool get cb
common:
    Mn: BAUER Electronic
    Md: BSM-WS36A-H01-1311-0000
    Opt: None
    Vr: 1.9:32CA:AFF4
    SN: 21070006
    DA: 42
```
which results in the following Modbus frames being sent to and from the device:
```
--> 2a 03 9c44 0042 ada5
<-- 2a 03 84 424155455220456c656374726f6e69630000000000000000000000000000000042534d2d57533336412d4830312d313331312d3030303000000000000000000000000000000000000000000000000000312e393a333243413a414646340000003231303730303036000000000000000000000000000000000000000000000000002a8000 890d
```

### Register Contents

For pointing out the actual data register dumps will be used. Such dumps could
be generated with the BSM Tool using protocol addresses:
```
$ bsmtool dump 40002 68
   40002: 0001 0042 4241 5545 5220 456c 6563 7472  ...BBAUER Electr
   40010: 6f6e 6963 0000 0000 0000 0000 0000 0000  onic............
   40018: 0000 0000 4253 4d2d 5753 3336 412d 4830  ....BSM-WS36A-H0
   40026: 312d 3133 3131 2d30 3030 3000 0000 0000  1-1311-0000.....
   40034: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40042: 0000 0000 312e 393a 3332 4341 3a41 4646  ....1.9:32CA:AFF
   40050: 3400 0000 3231 3037 3030 3036 0000 0000  4...21070006....
   40058: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40066: 0000 0000 002a 8000                      .....*..
```
An output line starts with the decimal protocol address of the first register
in this line. It is followed by a hexadecimal representation of the register
contents. At the end of the line, the data is interpreted as ASCII characters
where possible and dots also represent non-printable characters.

The example above includes two registers of header data starting at protocol
address 40002/data address 40003.
