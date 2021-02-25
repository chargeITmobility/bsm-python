# Signed Snapshots

The BSM-WS36A allows taking snapshots of a predefined set of data points.
Successfully created snapshots will be ECDSA signed with the device's
individual key so the data can later be verified with the device's public key.

Snapshots are represented by instances of the model
[bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) and there are three snapshot
instances available. The first one:

- [_Signed Current Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L81)
  for a snapshot of the device's actual data

And two instances for switching an external contactor on or off via the meter's
digital I/Os:

- [_Signed Turn-On Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L92)
  for turning the contactor on after taking the snapshot data
- [_Signed Turn-Off Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L103)
  for turning the contactor off and taking the snapshot data afterwards

These two instances could be used for exactly measuring the energy consumption
between a turn-on and turn-off snapshot. In both cases the current energy
consumption gets recorded with the contactor turned off. This allows to exactly
determine the energy consumption between them, for example for electric vehicle
charging applications.


## Snapshot Creation

A snapshot gets created by the writing to its status data point
[_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L115) and polling this data
point afterwards its value indicates either a successful update or a failure.

The procedure looks as follows:

1. Write [_UPDATING_](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) (2) to
   [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L115)
2. Read the value of _St_ with a timeout of 15 seconds
3. If _St_ returns _UPDATING_ (2), continue with step 2
4. If _St_ returns _VALID_ (0), the snapshot data is ready to be read
5. If _St_ returns any other value, handle the error and reattempt to create
   the snapshot

Creating a snapshot with the BSM Tool differs from that procedure due to its
current limitation of reading a complete model instance at once. It will
therefor poll the whole snapshot instance like as follows:
```
$ bsmtool get-snapshot scs
Updating 'scs' succeeded
Snapshot data:
bsm_snapshot:
    fixed:
        Typ: 0
        St: 0
        RCR: 20 Wh
        TotWhImp: 36600 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 1513
        OS: 1038979 s
        Epoch: 1609491606 s
        TZO: 60 min
        EpochSetCnt: 221
        EpochSetOS: 881136 s
        DI: 1
        DO: 0
        Meta1: demo data 1
        Meta2: None
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 3045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e
```
In this case the snapshot gets created successfully and ready upon the first
poll:
```
--> 2a 10 9e4c 0001 02 0002 bca5
<-- 2a 10 9e4c 0001 e9ed
--> 2a 03 9e4b 0064 1dc4
<-- 2a 03 c8 000000000000001400008ef8000000000001303031425a5231353230323030303037000005e9000fda835feee496003c000000dd000d71f00001000064656d6f20646174612031000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 ada3
--> 2a 03 9eaf 007d 9c39
<-- 2a 03 fa 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000473045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d 3dba
--> 2a 03 9f2c 001b ec07
<-- 2a 03 36 8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e00000000000000000000000000000000000000000000000000 aa60
```

Just polling _St_ and not the entire model instance could for example be done
with the PyModbus Console:
```
$ pymodbus.console serial --port=$BSMTOOL_DEVICE --baudrate=19200 --parity=E --timeout=15
> client.write_registers unit=42 address=40524 values=2
{
    "address": 40524,
    "count": 1
}

> client.read_holding_registers unit=42 address=40524 count=1
{
    "registers": [ 0 ]
}
```
```
--> 2a 10 9e4c 0001 02 0002 bca5
<-- 2a 10 9e4c 0001 e9ed
--> 2a 03 9e4c 0001 6c2e
<-- 2a 03 02 0000 9c42
```


## Snapshot Data

### Overview

Snapshot data is represented by instances of the model
[bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) containing two data
points describing the snapshot:

- [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L78) as a read-only data
  point indicating the snapshot instance

- [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L115) returning the
  snapshot status when read and triggering the creation of a new snapshot by
  writing the value [_UPDATING_
  (2)](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) to this data point

Most data points represent the state of the corresponding data points (with
equal ID) from other model instances when the snapshot was taken. See
[bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) for details.


For example, the actual _Signed Current Snapshot_ [created
above](#snapshot-creation) could be read with the BSM Tool as follows:
```
$ bsmtool get scs
bsm_snapshot:
    fixed:
        Typ: 0
        St: 0
        RCR: 20 Wh
        TotWhImp: 36600 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 1513
        OS: 1038979 s
        Epoch: 1609491606 s
        TZO: 60 min
        EpochSetCnt: 221
        EpochSetOS: 881136 s
        DI: 1
        DO: 0
        Meta1: demo data 1
        Meta2: None
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 3045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e
```
```
--> 2a 03 9e4b 0064 1dc4
<-- 2a 03 c8 000000000000001400008ef8000000000001303031425a5231353230323030303037000005e9000fda835feee496003c000000dd000d71f00001000064656d6f20646174612031000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 ada3
--> 2a 03 9eaf 007d 9c39
<-- 2a 03 fa 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000473045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d 3dba
--> 2a 03 9f2c 001b ec07
<-- 2a 03 36 8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e00000000000000000000000000000000000000000000000000 aa60
```


### Modbus Register Dump

The contents of the Modbus registers of the snapshot example above in
[Overview](#overview) could also be shown as a register dump by the BSM Tool.
Please note, that the addresses used in the model instance overview and
register dumps are Modbus protocol addresses.

The BSM Tool provides an overview of the model instances with `bsmtool models`:
```
$ bsmtool models
Address  ID       Payload  Label                                    Name             Aliases
[...]
40521    64901    252      Signed Current Snapshot                  bsm_snapshot     signed_current_snapshot, scs
[...]
```

And current data of the _Signed Current Snapshot_ could be dumped by invoking
the following command with a total length of _payload length_ + 2:
```
$ bsmtool dump 40521 254
   40521: fd85 00fc 0000 0000 0000 0014 0000 8ef8  ................
   40529: 0000 0000 0001 3030 3142 5a52 3135 3230  ......001BZR1520
   40537: 3230 3030 3037 0000 05df 000f 2860 5f80  200007......(`_.
   40545: 829c 003c 0000 00dd 000d 71f0 0001 0000  ...<......q.....
   40553: 6465 6d6f 2064 6174 6120 3100 0000 0000  demo data 1.....
   40561: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40569: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40577: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40585: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40593: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40601: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40609: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40617: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40625: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40633: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40641: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40649: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40657: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40665: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40673: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40681: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40689: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40697: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40705: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40713: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40721: 0000 0000 0000 0000 0030 0047 3045 0220  .........0.G0E.
   40729: 6485 473a 37a8 9fb2 20a5 be53 396d 7474  d.G:7... ..S9mtt
   40737: 243a a68f bfb2 0089 7483 f628 0b17 d5a2  $:......t..(....
   40745: 0221 008d 19b0 f1f0 4504 4987 e418 4c86  .!......E.I...L.
   40753: 379e 5353 cc33 9a01 2df8 16b3 a172 4429  7.SS.3..-....rD)
   40761: 0176 8700 0000 0000 0000 0000 0000 0000  .v..............
   40769: 0000 0000 0000 0000 0000 0000            ............
```


### Energy and Power

A snapshot records three data points related to power and energy:

- The reference cumulative register
  [_RCR_](bauer_bsm/bsm/models/smdx_64901.xml#L176) which counts the energy
  consumption since it got reset during the creation of the last _Signed
  Turn-On Snapshot_
- [_TotWhImp_](bauer_bsm/bsm/models/smdx_64901.xml#L184) counting the overall
  energy consumption measured by the BSM-WS36A
- And the actual real power consumption
  [_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L192)

Please note that both counters maintain hidden internal digits to track the
energy consumption below the least significant digit presented in display and
on the Modbus interface. Resetting _RCR_ zeroes the hidden digits too and so a
difference between _TotWhImp_ readings is up to one least significant digit
ahead of _RCR_. Use _RCR_ for billing if you want to bill exactly the amount of
energy shown on the meter display.


### Time and Counter Information

For identifying the point in time of its creation, snapshots record timestamps
and some counters. Epoch time information in:

- [_Epoch_](../../bauer_bsm/bsm/models/smdx_64901.xml#L25) - [epoch
  time](https://en.wikipedia.org/wiki/Unix_time)
- [_TZO_](../../bauer_bsm/bsm/models/smdx_64901.xml#L26) - the current time
  zone offset to
  [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)

Please ensure to have epoch time information [set and updated](time.md) on a
regular basis at the [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) model to
get valid epoch time information in your snapshot data.

In addition to the epoch time, the BSM-WS36A also records the following data
points which might come in handy for validating a snapshots by their timestamps
and counter sequences:

- [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L23) a response counter
  which increments with each signed snapshot
- [_OS_](../../bauer_bsm/bsm/models/smdx_64901.xml#L24) the meter's operating
  seconds counter
- [_EpochSetCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L27) a counter
  which gets incremented every time the epoch time is set (in contrast to
  [updating](time.md#terminology))
- [_EpochSetOS_](../../bauer_bsm/bsm/models/smdx_64901.xml#L28) the operating
  seconds timestamp of the point in time snapshot data got recorded


### Metadata

The BSM-WS36A supports custom data to be included and signed along with the
other snapshot data. Therefor a snapshot records the three metadata string data
points

- [_Meta1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L31)
- [_Meta2_](../../bauer_bsm/bsm/models/smdx_64901.xml#L32)
- [_Meta3_](../../bauer_bsm/bsm/models/smdx_64901.xml#L33)

from the [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml) model. The character
encoding could be chosen by the application. In case of doubt, we recommend
using [UTF-8](https://en.wikipedia.org/wiki/UTF-8) to avoid ambiguity.

Unused space in the register area of a string data point needs to be
null-padded and a string data point needs to be written completely even if the
actual data is shorter.

Setting _Meta1_ to _demo data 1_ as shown in [Overview](#overview) can be done
with the BSM Tool as follows:
```
$ bsmtool set bsm/meta1="demo data 1"
```
```
--> 2a 10 9d57 0046 8c 64656d6f20646174612031000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 8a62
<-- 2a 10 9d57 0046 d99c
```
Please note that the BSM Tool currently uses the fixed character encoding
[ISO-8859-1/Latin 1](https://en.wikipedia.org/wiki/ISO/IEC_8859-1).


### Signature

The last data points of
[bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) are the signature
[BLOB](modbus-interface.md#binary-data) represented by:

- [_NSig_](../../bauer_bsm/bsm/models/smdx_64901.xml#L39) the number of Modbus
  registers forming the signature data area
- [_BSig_](../../bauer_bsm/bsm/models/smdx_64901.xml#L407) the number of bytes
  actually used by the signature
- [_Sig_](../../bauer_bsm/bsm/models/smdx_64901.xml#L411) the actual signature
  data

Snapshots are signed using ECDSA and the signature is encoded as
`Ecdsa-Sig-Value` from [RFC
4492](https://tools.ietf.org/html/rfc4492#section-5.4) in ASN.1 DER. In
essence, the signature components _r_ and _s_ with a prefix.

For example, _r_ and _s_ of the example from [Snapshot Data](#snapshot-data)
could be parsed from the signature using OpenSSL:
```
$ echo 3045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e | xxd -r -p | openssl asn1parse -inform der -i -dump
    0:d=0  hl=2 l=  69 cons: SEQUENCE
    2:d=1  hl=2 l=  33 prim:  INTEGER           :B83C4B4194F5FD536C036D6F9FA002FFE89A560A97FF8B72DD77057C2D77B86D
   37:d=1  hl=2 l=  32 prim:  INTEGER           :7FCB1D8B23AE8FC4CC80075F66D3EC4553D3E30AEE5D234D6C1333D143C3B78E
```


## Public Key

Similar to a snapshot signature, the [_Signing Meter_ model
instance](../../bauer_bsm/bsm/models/smdx_64900.xml#L31) provides the public
key [BLOB](modbus-interface.md#binary-data) through the data points
[_NPK_](../../bauer_bsm/bsm/models/smdx_64900.xml#L208),
[_BPK_](../../bauer_bsm/bsm/models/smdx_64900.xml#L216), and
[_PK_](../../bauer_bsm/bsm/models/smdx_64900.xml#L220).

The public key data is encoded according to [RFC
5480](https://tools.ietf.org/html/rfc5480#section-2). In essence, this is an
algorithm specifier identifying the actual curve and the public key point
encoded according to [SEC 1, section 2.3.4
_Octet-String-to-Elliptic-Curve-Point
Conversion_](https://www.secg.org/sec1-v2.pdf) which is the prefix 0x04
catenated with the curve point coordinates _X_ and _Y_.

For example, reading the BSM model instance for getting the public key with the BSM Tool:
```
$ bsmtool get bsm
bsm:
    fixed:
[...]
        NPK: 48
        BPK: 91
    repeating blocks blob:
        PK (der): 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254
```
```
--> 2a 03 9d07 0050 dd80
<-- 2a 03 a0 30303030303030303230323030303037000000000000000030303062353730303030363063623035312e373a393742343a3530354100000063393338663331000000000000000000303031425a5231353230323030303037303430303432000000000000000000000000001400000000037a000005db000d7e6a5f7ed8a6003c000000dd000d71f000010000ffffffffffffffff8000ffffffffffffffff8000 54a1
--> 2a 03 9d57 0078 dd8f
<-- 2a 03 f0 64656d6f2064617461203100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 bad4
--> 2a 03 9dcf 0064 5da9
<-- 2a 03 c8 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030005b3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c72540000000000 3c73
```

Or just reading the three BLOB data points demonstrated with the PyModbus
Console (mind PyModbus is using protocol addresses):
```
$ pymodbus.console serial --port=$BSMTOOL_DEVICE --baudrate=19200 --parity=E --timeout=15
> client.read_holding_registers unit=42 address=40449 count=50
{
    "registers": [48, 91, 12377, 12307, 1543, 10886, 18638, 15618, 262, 2090, 34376, 52797, 769, 1795, 16896, 1099, 64770, 49624, 21106, 52970, 39287, 56102, 55084, 50177, 55781, 24623, 44782, 32455, 46774, 12188, 3278, 13485, 36148, 23898, 49384, 63069, 60255, 61627, 16427, 7047, 37483, 53687, 64557, 48186, 38772, 59623, 3186, 21504, 0, 0]
}
```
The data gets read with a single Modbus transaction in this case:
```
--> 2a 03 9e01 0032 bc2c
<-- 2a 03 64 0030005b3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9ccce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e7c72540000000000 70fa
```

The public key data could be parsed with OpenSSL as well:
```
$ echo 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254 | xxd -r -p | openssl asn1parse -inform der -i -dump
    0:d=0  hl=2 l=  89 cons: SEQUENCE
    2:d=1  hl=2 l=  19 cons:  SEQUENCE
    4:d=2  hl=2 l=   7 prim:   OBJECT            :id-ecPublicKey
   13:d=2  hl=2 l=   8 prim:   OBJECT            :prime256v1
   23:d=1  hl=2 l=  66 prim:  BIT STRING
      0000 - 00 04 4b fd 02 c1 d8 52-72 ce ea 99 77 db 26 d7   ..K....Rr...w.&.
      0010 - 2c c4 01 d9 e5 60 2f ae-ee 7e c7 b6 b6 2f 9c 0c   ,....`/..~.../..
      0020 - ce 34 ad 8d 34 5d 5a c0-e8 f6 5d eb 5f f0 bb 40   .4..4]Z...]._..@
      0030 - 2b 1b 87 92 6b d1 b7 fc-2d bc 3a 97 74 e8 e7 0c   +...k...-.:.t...
      0040 - 72 54                                             rT
```
This gives the curve identifier _prime256v1_ which is an [alternative
name](https://tools.ietf.org/html/rfc4492#appendix-A) for _secp256r1_ and the
public key as a bit string which again decodes to:

- Prefix 0x0004 indicating an uncompressed ECDSA curve point
- X: 0x4bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34
- Y: 0xad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254


## Snapshot Verification

A snapshot signature is generated in two steps:

- Compute the SHA-256 hash over an abstract representation of the snapshot data
- Sign this hash using ECDSA

To verify a signature, the following steps are required:

- Re-compute the SHA-256 hash over this abstract representation of the snapshot
  data read from the device
- Verify the ECDSA signature for this hash using the device's public key


### Verifying a Snapshot with the BSM Tool

The BSM Python support provides the functionality to verify snapshot data which
in turn is used by the BSM tool to provide this functionality. The command
`verify-snapshot` could be used to verify shapshot data. It performs the steps
from above and prints intermediate results to facilitate following this
procedure.

Verifying the the _Signed Current Snapshot_ created in [Snapshot
Creation](#snapshot-creation) looks as follows:
```
$ bsmtool verify-snapshot scs
Verifying 64901 ...
Curve: secp256r1
Public key: 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254
Signature: 3045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e
Computing SHA-256 digest for snapshot data:
Typ:
    value: 0
    data:  0000000000ff
RCR:
    value: 20 Wh
    data:  00000014001e
TotWhImp:
    value: 36600 Wh
    data:  00008ef8001e
W:
    value: 0.0 W
    data:  00000000011b
MA1:
    value: 001BZR1520200007
    data:  00000010303031425a5231353230323030303037
RCnt:
    value: 1513
    data:  000005e900ff
OS:
    value: 1038979 s
    data:  000fda830007
Epoch:
    value: 1609491606 s
    data:  5feee4960007
TZO:
    value: 60 min
    data:  0000003c0006
EpochSetCnt:
    value: 221
    data:  000000dd00ff
EpochSetOS:
    value: 881136 s
    data:  000d71f00007
DI:
    value: 1
    data:  0000000100ff
DO:
    value: 0
    data:  0000000000ff
Meta1:
    value: demo data 1
    data:  0000000b64656d6f20646174612031
Meta2:
    value: None
    data:  00000000
Meta3:
    value: None
    data:  00000000
Evt:
    value: 0
    data:  0000000000ff
Snapshot data SHA-256 digest: 07c35dbf15939c4c3d79c61a5cffc5006d88e4e86a3ad40739b6afaf5a6f2ffb
Success.
```

This is done in code by BSM Tool's
[`verify_snapshot_command`](../../bauer_bsm/cli/bsmtool.py#L523) which uses
[`verify_snapshot`](../../bauer_bsm/bsm/client.py#L406) from the BSM Python
support. The following sections cover some aspects of this procedure more in
detail.

### Abstract Data Representation

The BSM-WS36A uses an abstract data representation for having a generic
representation of numerical values and to include the unit which is implicitly
given by the model definition of
[bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml). This abstract data
representation is fed into the hash function to generate the hash value to be
signed later

See our Python implementation
[`update_md_from_point`](../../bauer_bsm/bsm/md.py#L90) for more details.


#### Numerical Values

Numerical values are represented by

- A 32 bit representation of the numerical value _v_
- A signed 8 bit scale factor exponent  _s_
- The unsigned 8 bit representation _u_ of the DLMS code for its unit (see
  [_EXCERPT FROM Companion Specification for Energy Metering COSEM Interface
  Classes and OBIS Object Identification
  System_](https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf), _Table 4 –
  Enumerated values for physical units_ and
  [`bauer_bsm/bsm/dlms.py`](../../bauer_bsm/bsm/dlms.py) in this repository)

giving `vvvvvvvv ss uu` where each letter represents a hexadecimal digit of the
respective element. For example, 36.6 kWh will be represented as follows:

- In its base unit Wh: 36.6 kWh = 36600 Wh = 0x8ef8 Wh
- This would require a scale factor of 1 = 10^0, thus the scale factor exponent
  0
- The DLMS unit code for Wh 30 = 0x1e
- Which results in `00008ef8 00 1e`

See [`data_for_scaled_int32`](../../bauer_bsm/bsm/md.py#L113) and
[`data_for_scaled_uint32`](../../bauer_bsm/bsm/md.py#L117).


#### String Values

String values are represented by:

- Its length as an unsigned 32 bit value
- Catenated with its actual data bytes

For example the string `ABC` will be represented as `00000003 414243`. See
[`data_for_string`](../../bauer_bsm/bsm/md.py#L121).


### Signature Verification

BSM Tools `verify-snapshot` command verifies the signature of the specified
snapshot.  additionally provides `verify-signature` for indepently verifying
the signature for a given hash and public key. The latter is implemented at
[`verify_signature_command`](../../bauer_bsm/cli/bsmtool.py#L519) and both of
them are backed by [`verify_signed_digest`](../../bauer_bsm/crypto/util.py#L72).

Verifying the signature for the snapshot data hash shown in in [Verifying a
Snapshot with the BSM Tool](#verifying-a-snapshot-with-the-bsm-tool) could be
done by:
```
$ bsmtool --verbose verify-signature 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254 07c35dbf15939c4c3d79c61a5cffc5006d88e4e86a3ad40739b6afaf5a6f2ffb 3045022100b83c4b4194f5fd536c036d6f9fa002ffe89a560a97ff8b72dd77057c2d77b86d02207fcb1d8b23ae8fc4cc80075f66d3ec4553d3e30aee5d234d6c1333d143c3b78e
Success.
```
