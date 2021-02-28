# Electric Vehicle Charging

The BSM-WS36A facilitates setting up electric vehicle charging applications in
three ways:

1. Taking and signing snapshots of data relevant for billing
2. Its ability to directly control an external contactor for controlling energy
   delivery and its controlled operation for recording snapshot data with the
   contactor turned off
3. Direct output of
   [OCMF](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format) data
   allowing end-user validation of billing data with commonly used and
   available software without the need for separate signing

The following sections demonstrate how to make use of them.


## Typical Setup

Core components of an electric vehicle charging application are the meter
itself and a contactor with appropriate auxiliary contacts for providing
feedback. [Hardware Setup](prerequisites.md#hardware-setup) shows the
single-phase setup we in the example below:

![Demo and Development Setup](img/bsm-demo-box-schematic-20210204.png)

For charging electric cars, a three-phase installation is more common though.

If epoch time information is important for billing, an external controller is
required for providing it to the meter on a regular basis as described in
[Setting and Updating Time](time.md).


## Charging Scenario

### Overview

This example shows aspects of a typical charging scenario as sketched below:

![EV Charging](img/overview-charging.png)

The backend in this example generates OCMF-XML envelopes for billing data. But
every data format which implicitly or explicitly supports passing the actual
signed data could be generated from the snapshot data.


### Updating Time Information

The time information is assumed to be up to date. It could be set and updated
as described in [Setting and Updating Time](time.md). This needs to be done on
a regular basis.

shown below:
```
$ bsmtool set bsm/epoch=1609491600 bsm/tzo=60
```
```
--> 2a 10 9d44 0003 06 5feee490003c d4b0
<-- 2a 10 9d44 0003 e9aa
```


### Setting Identification Data

The BSM-WS36A provides three string [metadata points](snapshots.md#metadata)
_Meta1_, _Meta2_ and _Meta3_ which get recorded and signed when creating a
snapshot.

These three data points could be used according to the application's needs when
generating billing data from the regular snapshots. When using the meter's OCMF
representation, only _Meta1_ will be included as customer identification data
_ID_.

This example sets and uses the following demo data

- Customer identification data _chargeIT up 12*4, id: 12345678abcdef_ set as _Meta1_
- Some more demo data _demo data 2_ set as _Meta2_
- _Meta3_ left in its initial empty state

where _12345678abcdef_ is meant to be the identification from an RFID
identification tag. This data could be set with the BSM Tool:
```
$ bsmtool set 'bsm/meta1=chargeIT up 12*4, id: 12345678abcdef' 'bsm/meta2=demo data 2'
```
```
--> 2a 10 9d57 0078 f0 63686172676549542075702031322a342c2069643a203132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000064656d6f206461746120320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 a4eb
<-- 2a 10 9d57 0078 584c
```


### Start of Charging

Creating a _Signed Turn-On Snapshot_ starts the charging process by recording
the baseline data and turning on the contactor. [Snapshot
Creation](snapshots.md#snapshot-creation) gives the details about this
procedure.


#### Creating the _Signed Turn-On Snapshot_

Create and read the _Signed Turn-On Snapshot_ as follows:
```
$ bsmtool get-snapshot stons
Updating 'stons' succeeded
Snapshot data:
bsm_snapshot:
    fixed:
        Typ: 1
        St: 0
        RCR: None
        TotWhImp: 14430 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 2064
        OS: 352851 s
        Epoch: 1609491622 s
        TZO: 60 min
        EpochSetCnt: 224
        EpochSetOS: 352832 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 70
    repeating blocks blob:
        Sig: 304402201bfb63da4a6ea54d5dec4579cb029d435b9391e85587905d740d711867650860022008f16665b60dedeccb0bb061c49b8bb68e24754c600269f6a74bd020e72caf2e
```
```
--> 2a 10 9f4a 0001 02 0002 ac03
<-- 2a 10 9f4a 0001 0810
--> 2a 03 9f49 0064 bdf8
<-- 2a 03 c8 00010000000000000000385e000000000001303031425a523135323032303030303700000810000562535feee4a6003c000000e0000562400001000063686172676549542075702031322a342c2069643a2031323334353637386162636465660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 a572
--> 2a 03 9fad 007d 3c05
<-- 2a 03 fa 64656d6f206461746120320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300046304402201bfb63da4a6ea54d5dec4579cb029d435b9391e85587905d740d711867650860022008f16665 4985
--> 2a 03 a02a 001b 0012
<-- 2a 03 36 b60dedeccb0bb061c49b8bb68e24754c600269f6a74bd020e72caf2e0000000000000000000000000000000000000000000000000000 daa2
```

#### Key Start Snapshot Data Points

Let's have a quick look at its key data points:

- Type and status
    - This is a [_Signed Turn-On
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L6) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L78)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L10) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L115)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L169) which will show
      the energy consumption at the end has been reset to zero
    - [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L177) gives the
      total energy consumption tracked by this meter and could be used for
      computing the energy consumption of the actual charging process as the
      delta between start and end
    - It was taken with no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) = 0 Wh) as it
      should be the case with the contactor turned off
- Time and counters
    - Let's remember the response counter
      [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L198) 2,064 for later
    - It has valid time information in _Epoch_ and _TZO_
- Metadata points _Meta1_ and _Meta2_ contain the previously set metadata


#### Start Snapshot Register Dump

The register dump (protocol addresses) of the start snapshot looks as follows:
```
$ bsmtool dump 40775 254
   40775: fd85 00fc 0001 0000 0000 0000 0000 385e  ..............8^
   40783: 0000 0000 0001 3030 3142 5a52 3135 3230  ......001BZR1520
   40791: 3230 3030 3037 0000 0810 0005 6253 5fee  200007......bS_.
   40799: e4a6 003c 0000 00e0 0005 6240 0001 0000  ...<......b@....
   40807: 6368 6172 6765 4954 2075 7020 3132 2a34  chargeIT up 12*4
   40815: 2c20 6964 3a20 3132 3334 3536 3738 6162  , id: 12345678ab
   40823: 6364 6566 0000 0000 0000 0000 0000 0000  cdef............
   40831: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40839: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40847: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40855: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40863: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40871: 0000 0000 0000 0000 0000 0000 6465 6d6f  ............demo
   40879: 2064 6174 6120 3200 0000 0000 0000 0000   data 2.........
   40887: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40895: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40903: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40911: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40919: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40927: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40935: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40943: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40951: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40959: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40967: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40975: 0000 0000 0000 0000 0030 0046 3044 0220  .........0.F0D. 
   40983: 1bfb 63da 4a6e a54d 5dec 4579 cb02 9d43  ..c.Jn.M].Ey...C
   40991: 5b93 91e8 5587 905d 740d 7118 6765 0860  [...U..]t.q.ge.`
   40999: 0220 08f1 6665 b60d edec cb0b b061 c49b  . ..fe.......a..
   41007: 8bb6 8e24 754c 6002 69f6 a74b d020 e72c  ...$uL`.i..K. .,
   41015: af2e 0000 0000 0000 0000 0000 0000 0000  ................
   41023: 0000 0000 0000 0000 0000 0000            ............
```


#### Start OCMF Representation

The snapshot is valid and so its OCMF representation could be read from _OCMF
Signed Turn-On Snapshot_ with the BSM Tool:
```
$ bsmtool get ostons
bsm_ocmf:
    Typ: 1
    St: 0
    O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1520200007","GV":"1.7:97B4:505A, d939f6f","PG":"T2064","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1520200007","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2021-01-01T10:00:22,000+0100 S","TX":"B","RV":0,"RI":"1-0:1.8.0*198","RU":"Wh","XV":14430,"XI":"1-0:1.8.0*255","XU":"Wh","RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3044022017d905bd931ef4512d17fcc33730c58a54c9ccccd52a59dcbb4d8bdec72564cb02203e453a01a5e3dc7b9ea5cdb46f86a77a8941279ca9135b733161f3187041d430"}
```
```
--> 2a 03 a2bb 0002 918d
<-- 2a 03 04 00010000 30f1
--> 2a 03 a2bd 007d 306c
<-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353230323030303037222c224756223a22312e373a393742343a353035412c2064393339663666222c225047223a225432303634222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353230323030303037222c224953223a747275652c224954223a22554e444546494e4544222c224944223a22636861726765 e226
--> 2a 03 a33a 007d 81b9
<-- 2a 03 fa 49542075702031322a342c2069643a203132333435363738616263646566222c225244223a5b7b22544d223a22323032312d30312d30315431303a30303a32322c3030302b303130302053222c225458223a2242222c225256223a302c225249223a22312d303a312e382e302a313938222c225255223a225768222c225856223a31343433302c225849223a22312d303a312e382e302a323535222c225855223a225768222c225254223a224143222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a223330343430323230313764393035626439 3f39
--> 2a 03 a3b7 0078 d191
<-- 2a 03 f0 333165663435313264313766636333333733306335386135346339636363636435326135396463626234643862646563373235363463623032323033653435336130316135653364633762396561356364623436663836613737613839343132373963613931333562373333313631663331383730343164343330227d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 93b9
```


#### Key Start OCMF Values

[Pretty-printed](ocmf.md#ocmf-json-payload), the _OCMF Signed Turn-On
Snapshot_'s payload looks like:
```json
{
  "FV": "1.0",
  "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
  "GS": "001BZR1520200007",
  "GV": "1.7:97B4:505A, d939f6f",
  "PG": "T2064",
  "MV": "BAUER Electronic",
  "MM": "BSM-WS36A-H01-1311-0000",
  "MS": "001BZR1520200007",
  "IS": true,
  "IT": "UNDEFINED",
  "ID": "chargeIT up 12*4, id: 12345678abcdef",
  "RD": [
    {
      "TM": "2021-01-01T10:00:22,000+0100 S",
      "TX": "B",
      "RV": 0,
      "RI": "1-0:1.8.0*198",
      "RU": "Wh",
      "XV": 14430,
      "XI": "1-0:1.8.0*255",
      "XU": "Wh",
      "RT": "AC",
      "EF": "",
      "ST": "G"
    }
  ]
}
```

Let's have a quick look at its key data points too:

- Type and status
    - Its type is indicated by the transaction _TX_ = _B_ (for beginning)
    - Its status _ST_ indicates that it is _good_ = _G_
- Power and energy
    - The reference cumulative register is used as the primary reading value
      _RV_
    - The total energy consumption is given as the additional value _XV_
    - The OCMF data does not contain the active power
- Time and counters
    - It provides the response counter as the snapshot in _PG_ (for pagination)
      prefixed with _T_ for a reading in a transactional context
    - Epoch time information is given in ISO 8601 format instead of epoch
      seconds and timezone offset
- _Meta1_ is used as identification data _ID_ and the identification type
  always _IT_ always returns _UNDEFINED_


#### Start OCMF Register Dump

The register dump of the start snapshot's OCMF representation looks as follows:
```
$ bsmtool dump 41657 374
   41657: fd87 0174 0001 0000 4f43 4d46 7c7b 2246  ...t....OCMF|{"F
   41665: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   41673: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic
   41681: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   41689: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   41697: 3031 425a 5231 3532 3032 3030 3030 3722  01BZR1520200007"
   41705: 2c22 4756 223a 2231 2e37 3a39 3742 343a  ,"GV":"1.7:97B4:
   41713: 3530 3541 2c20 6439 3339 6636 6622 2c22  505A, d939f6f","
   41721: 5047 223a 2254 3230 3634 222c 224d 5622  PG":"T2064","MV"
   41729: 3a22 4241 5545 5220 456c 6563 7472 6f6e  :"BAUER Electron
   41737: 6963 222c 224d 4d22 3a22 4253 4d2d 5753  ic","MM":"BSM-WS
   41745: 3336 412d 4830 312d 3133 3131 2d30 3030  36A-H01-1311-000
   41753: 3022 2c22 4d53 223a 2230 3031 425a 5231  0","MS":"001BZR1
   41761: 3532 3032 3030 3030 3722 2c22 4953 223a  520200007","IS":
   41769: 7472 7565 2c22 4954 223a 2255 4e44 4546  true,"IT":"UNDEF
   41777: 494e 4544 222c 2249 4422 3a22 6368 6172  INED","ID":"char
   41785: 6765 4954 2075 7020 3132 2a34 2c20 6964  geIT up 12*4, id
   41793: 3a20 3132 3334 3536 3738 6162 6364 6566  : 12345678abcdef
   41801: 222c 2252 4422 3a5b 7b22 544d 223a 2232  ","RD":[{"TM":"2
   41809: 3032 312d 3031 2d30 3154 3130 3a30 303a  021-01-01T10:00:
   41817: 3232 2c30 3030 2b30 3130 3020 5322 2c22  22,000+0100 S","
   41825: 5458 223a 2242 222c 2252 5622 3a30 2c22  TX":"B","RV":0,"
   41833: 5249 223a 2231 2d30 3a31 2e38 2e30 2a31  RI":"1-0:1.8.0*1
   41841: 3938 222c 2252 5522 3a22 5768 222c 2258  98","RU":"Wh","X
   41849: 5622 3a31 3434 3330 2c22 5849 223a 2231  V":14430,"XI":"1
   41857: 2d30 3a31 2e38 2e30 2a32 3535 222c 2258  -0:1.8.0*255","X
   41865: 5522 3a22 5768 222c 2252 5422 3a22 4143  U":"Wh","RT":"AC
   41873: 222c 2245 4622 3a22 222c 2253 5422 3a22  ","EF":"","ST":"
   41881: 4722 7d5d 7d7c 7b22 5341 223a 2245 4344  G"}]}|{"SA":"ECD
   41889: 5341 2d73 6563 7032 3536 7231 2d53 4841  SA-secp256r1-SHA
   41897: 3235 3622 2c22 5344 223a 2233 3034 3430  256","SD":"30440
   41905: 3232 3031 3764 3930 3562 6439 3331 6566  22017d905bd931ef
   41913: 3435 3132 6431 3766 6363 3333 3733 3063  4512d17fcc33730c
   41921: 3538 6135 3463 3963 6363 6364 3532 6135  58a54c9ccccd52a5
   41929: 3964 6362 6234 6438 6264 6563 3732 3536  9dcbb4d8bdec7256
   41937: 3463 6230 3232 3033 6534 3533 6130 3161  4cb02203e453a01a
   41945: 3565 3364 6337 6239 6561 3563 6462 3436  5e3dc7b9ea5cdb46
   41953: 6638 3661 3737 6138 3934 3132 3739 6361  f86a77a8941279ca
   41961: 3931 3335 6237 3333 3136 3166 3331 3837  9135b733161f3187
   41969: 3034 3164 3433 3022 7d00 0000 0000 0000  041d430"}.......
   41977: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41985: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41993: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42001: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42009: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42017: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42025: 0000 0000 0000 0000 0000 0000            ............
```


### Intermediate Values

Intermediate values for the current charging process might be required for
example for displaying status information. There are two ways to get them:

- Just reading out the desired data points from the [AC
  Meter](modbus-interface.md#model-instances) and [_Signing
  Meter_](modbus-interface.md#model-instances) model instances

- Creating [_Signed Current Snapshot_](modbus-interface.md#model-instances)s

Both of them provide data suitable for status updates. The latter associates
energy consumption with a timestamp but increases the response counter so that
this one will reflect the number of intermediate snapshots taken at the end of
the charging process.


### End of Charging

Creating a _Signed Turn-Off Snapshot_ ends the charging process by turning of
the contactor and recoding the snapshot data. Again, [Snapshot Creation]() gives
the details about this procedure.


#### Creating the Signed Turn-Off Snapshot

Creating and reading the _Signed Turn-Off Snapshot_ works in analog to
[creating the _Signed Turn-On Snapshot_](#creating-the-signed-turn-on-snapshot)
and as follows:
```
$ bsmtool get-snapshot stoffs
Updating 'stoffs' succeeded
Snapshot data:
bsm_snapshot:
    fixed:
        Typ: 2
        St: 0
        RCR: 150 Wh
        TotWhImp: 14590 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 2065
        OS: 353162 s
        Epoch: 1609491933 s
        TZO: 60 min
        EpochSetCnt: 224
        EpochSetOS: 352832 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 70
    repeating blocks blob:
        Sig: 304402204fb0de8e38e9e23ebe52e2b15397fe1313cd4753b88b0920b58edad6127448a80220408a02dc0f65545637201f912c7e0107669149f60722e8365ba0b1f5f25936bb
```
```
--> 2a 10 a048 0001 02 0002 62e2
<-- 2a 10 a048 0001 a5c4
--> 2a 03 a047 0064 d02f
<-- 2a 03 c8 0002000000000096000038fe000000000001303031425a5231353230323030303037000008110005638a5feee5dd003c000000e0000562400001000063686172676549542075702031322a342c2069643a2031323334353637386162636465660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 a6e7
--> 2a 03 a0ab 007d d010
<-- 2a 03 fa 64656d6f206461746120320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300046304402204fb0de8e38e9e23ebe52e2b15397fe1313cd4753b88b0920b58edad6127448a80220408a02dc 9791
--> 2a 03 a128 001b a02e
<-- 2a 03 36 0f65545637201f912c7e0107669149f60722e8365ba0b1f5f25936bb0000000000000000000000000000000000000000000000000000 cbe0
```

#### Key End Snapshot Data Points

Let's look one more time at the snapshot's key data points and compare them to
the _Signed Turn-On Snapshot_ taken at the start of charging:

- Type and status
    - This is a [_Signed Turn-Off
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L7) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L78)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L10) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L115)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L169) started at zero
      and now shows the energy delivered during this charging process: 150 Wh
    - The total energy delivered,
      [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L177), increased
      from 14,430 Wh to 14,590 Wh which gives a consumption of 160 Wh. This is
      one least significant digit more than the reading from _RCR_ due to their
      [internal state](snapshots.md#energy-and-power) for continuously tracking
      energy consumption.
    - Again, there is no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) = 0 Wh) since
      power delivery got cut before recording the snapshot data
- Metadata is still the same as in _Signed Turn-On Snapshot_


#### End Snapshot Register Dump

The register dump of the end snapshot looks as follows
```
$ bsmtool dump 41029 254
   41029: fd85 00fc 0002 0000 0000 0096 0000 38fe  ..............8.
   41037: 0000 0000 0001 3030 3142 5a52 3135 3230  ......001BZR1520
   41045: 3230 3030 3037 0000 0811 0005 638a 5fee  200007......c._.
   41053: e5dd 003c 0000 00e0 0005 6240 0001 0000  ...<......b@....
   41061: 6368 6172 6765 4954 2075 7020 3132 2a34  chargeIT up 12*4
   41069: 2c20 6964 3a20 3132 3334 3536 3738 6162  , id: 12345678ab
   41077: 6364 6566 0000 0000 0000 0000 0000 0000  cdef............
   41085: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41093: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41101: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41109: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41117: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41125: 0000 0000 0000 0000 0000 0000 6465 6d6f  ............demo
   41133: 2064 6174 6120 3200 0000 0000 0000 0000   data 2.........
   41141: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41149: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41157: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41165: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41173: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41181: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41189: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41197: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41205: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41213: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41221: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41229: 0000 0000 0000 0000 0030 0046 3044 0220  .........0.F0D.
   41237: 4fb0 de8e 38e9 e23e be52 e2b1 5397 fe13  O...8..>.R..S...
   41245: 13cd 4753 b88b 0920 b58e dad6 1274 48a8  ..GS... .....tH.
   41253: 0220 408a 02dc 0f65 5456 3720 1f91 2c7e  . @....eTV7 ..,~
   41261: 0107 6691 49f6 0722 e836 5ba0 b1f5 f259  ..f.I..".6[....Y
   41269: 36bb 0000 0000 0000 0000 0000 0000 0000  6...............
   41277: 0000 0000 0000 0000 0000 0000            ............
```


#### OCMF End Representation

After successfully creating the _Signed Turn-Off Snapshot_, its OCMF
representation can be read from _OCMF Signed Turn-Off Snapshot_:
```
$ bsmtool get ostoffs
bsm_ocmf:
    Typ: 2
    St: 0
    O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1520200007","GV":"1.7:97B4:505A, d939f6f","PG":"T2065","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1520200007","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2021-01-01T10:05:33,000+0100 S","TX":"E","RV":150,"RI":"1-0:1.8.0*198","RU":"Wh","XV":14590,"XI":"1-0:1.8.0*255","XU":"Wh","RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"304502206557e44b012431b80b603390d6ed5381b5c774e823b8dd99c078d25b5c04a20d022100ca14532a0185ba0feb0a9f60949d33bc682bc786e8bbd8df174cab2668e4160f"}
```
```
--> 2a 03 a431 0002 b0ef
<-- 2a 03 04 00020000 c0f1
--> 2a 03 a433 007d 50cf
<-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353230323030303037222c224756223a22312e373a393742343a353035412c2064393339663666222c225047223a225432303635222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353230323030303037222c224953223a747275652c224954223a22554e444546494e4544222c224944223a22636861726765 2fb6
--> 2a 03 a4b0 007d a127
<-- 2a 03 fa 49542075702031322a342c2069643a203132333435363738616263646566222c225244223a5b7b22544d223a22323032312d30312d30315431303a30353a33332c3030302b303130302053222c225458223a2245222c225256223a3135302c225249223a22312d303a312e382e302a313938222c225255223a225768222c225856223a31343539302c225849223a22312d303a312e382e302a323535222c225855223a225768222c225254223a224143222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a22333034353032323036353537653434 db82
--> 2a 03 a52d 0078 f136
<-- 2a 03 f0 62303132343331623830623630333339306436656435333831623563373734653832336238646439396330373864323562356330346132306430323231303063613134353332613031383562613066656230613966363039343964333362633638326263373836653862626438646631373463616232363638653431363066227d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 95a1
```


#### Key End OCMF Values

[Pretty-printed](ocmf.md#ocmf-json-payload), the _OCMF Signed Turn-Off
Snapshot_ looks as follows:
```json
{
  "FV": "1.0",
  "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
  "GS": "001BZR1520200007",
  "GV": "1.7:97B4:505A, d939f6f",
  "PG": "T2065",
  "MV": "BAUER Electronic",
  "MM": "BSM-WS36A-H01-1311-0000",
  "MS": "001BZR1520200007",
  "IS": true,
  "IT": "UNDEFINED",
  "ID": "chargeIT up 12*4, id: 12345678abcdef",
  "RD": [
    {
      "TM": "2021-01-01T10:05:33,000+0100 S",
      "TX": "E",
      "RV": 150,
      "RI": "1-0:1.8.0*198",
      "RU": "Wh",
      "XV": 14590,
      "XI": "1-0:1.8.0*255",
      "XU": "Wh",
      "RT": "AC",
      "EF": "",
      "ST": "G"
    }
  ]
}
```

Let's have a quick look at its key data points:

- Type and status
    - Its type is indicated by the transaction _TX_ = _E_ (for end)
    - Its status _ST_ = _G_ stands for good
- Power and energy
    - The primary reading value _RV_ now shows the energy consumption from the
      refernce cumulative register: 150 Wh
    - The total energy consumption is given by _XV_
    - The OCMF data does not contain the active power
- Time and counters
    - The response counter _PG_ (prefixed with _T_) gives the value 2,065 and
      is the successor of the start response counter
    - Epoch time information is given in ISO 8601 format
- The identification data _ID_ taken from _Meta1_ has the same value as in the
  start OCMF data


#### End OCMF Register Dump

The register dump of the end snapshot's OCMF representation looks as follows:
```
$ bsmtool dump 42031 374
   42031: fd87 0174 0002 0000 4f43 4d46 7c7b 2246  ...t....OCMF|{"F
   42039: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   42047: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic
   42055: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   42063: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   42071: 3031 425a 5231 3532 3032 3030 3030 3722  01BZR1520200007"
   42079: 2c22 4756 223a 2231 2e37 3a39 3742 343a  ,"GV":"1.7:97B4:
   42087: 3530 3541 2c20 6439 3339 6636 6622 2c22  505A, d939f6f","
   42095: 5047 223a 2254 3230 3635 222c 224d 5622  PG":"T2065","MV"
   42103: 3a22 4241 5545 5220 456c 6563 7472 6f6e  :"BAUER Electron
   42111: 6963 222c 224d 4d22 3a22 4253 4d2d 5753  ic","MM":"BSM-WS
   42119: 3336 412d 4830 312d 3133 3131 2d30 3030  36A-H01-1311-000
   42127: 3022 2c22 4d53 223a 2230 3031 425a 5231  0","MS":"001BZR1
   42135: 3532 3032 3030 3030 3722 2c22 4953 223a  520200007","IS":
   42143: 7472 7565 2c22 4954 223a 2255 4e44 4546  true,"IT":"UNDEF
   42151: 494e 4544 222c 2249 4422 3a22 6368 6172  INED","ID":"char
   42159: 6765 4954 2075 7020 3132 2a34 2c20 6964  geIT up 12*4, id
   42167: 3a20 3132 3334 3536 3738 6162 6364 6566  : 12345678abcdef
   42175: 222c 2252 4422 3a5b 7b22 544d 223a 2232  ","RD":[{"TM":"2
   42183: 3032 312d 3031 2d30 3154 3130 3a30 353a  021-01-01T10:05:
   42191: 3333 2c30 3030 2b30 3130 3020 5322 2c22  33,000+0100 S","
   42199: 5458 223a 2245 222c 2252 5622 3a31 3530  TX":"E","RV":150
   42207: 2c22 5249 223a 2231 2d30 3a31 2e38 2e30  ,"RI":"1-0:1.8.0
   42215: 2a31 3938 222c 2252 5522 3a22 5768 222c  *198","RU":"Wh",
   42223: 2258 5622 3a31 3435 3930 2c22 5849 223a  "XV":14590,"XI":
   42231: 2231 2d30 3a31 2e38 2e30 2a32 3535 222c  "1-0:1.8.0*255",
   42239: 2258 5522 3a22 5768 222c 2252 5422 3a22  "XU":"Wh","RT":"
   42247: 4143 222c 2245 4622 3a22 222c 2253 5422  AC","EF":"","ST"
   42255: 3a22 4722 7d5d 7d7c 7b22 5341 223a 2245  :"G"}]}|{"SA":"E
   42263: 4344 5341 2d73 6563 7032 3536 7231 2d53  CDSA-secp256r1-S
   42271: 4841 3235 3622 2c22 5344 223a 2233 3034  HA256","SD":"304
   42279: 3530 3232 3036 3535 3765 3434 6230 3132  502206557e44b012
   42287: 3433 3162 3830 6236 3033 3339 3064 3665  431b80b603390d6e
   42295: 6435 3338 3162 3563 3737 3465 3832 3362  d5381b5c774e823b
   42303: 3864 6439 3963 3037 3864 3235 6235 6330  8dd99c078d25b5c0
   42311: 3461 3230 6430 3232 3130 3063 6131 3435  4a20d022100ca145
   42319: 3332 6130 3138 3562 6130 6665 6230 6139  32a0185ba0feb0a9
   42327: 6636 3039 3439 6433 3362 6336 3832 6263  f60949d33bc682bc
   42335: 3738 3665 3862 6264 3864 6631 3734 6361  786e8bbd8df174ca
   42343: 6232 3636 3865 3431 3630 6622 7d00 0000  b2668e4160f"}...
   42351: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42359: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42367: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42375: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42383: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42391: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42399: 0000 0000 0000 0000 0000 0000            ............
```


### Billing Data and Verification

Having _Signed Turn-On Snapshot_ and _Signed Turn-Off Snapshot_ successfully
created and read, billing data could be generated. Depending on the application
it might be either derived from the snapshot data or its OCMF representation.
In the latter case this data is typically wrapped in an OCMF XML envelope as
described in [OCMF XML](ocmf.md#ocmf-xml).

[Snapshot Verification](snapshots.md#snapshot-verification) describes how to
verify snapshot data and [OCMF XML](ocmf.md#ocmf-xml) the generation and
verification of OCMF XML envelopes.

For this example, the OCMF XML envelope could be generated from the OCMF
representation of start and end snapshot created above with:
```xml
$ bsmtool ocmf-xml
<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<values>
  <value transactionId="1" context="Transaction.Begin">
    <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1520200007","GV":"1.7:97B4:505A, d939f6f","PG":"T2064","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1520200007","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2021-01-01T10:00:22,000+0100 S","TX":"B","RV":0,"RI":"1-0:1.8.0*198","RU":"Wh","XV":14430,"XI":"1-0:1.8.0*255","XU":"Wh","RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3044022017d905bd931ef4512d17fcc33730c58a54c9ccccd52a59dcbb4d8bdec72564cb02203e453a01a5e3dc7b9ea5cdb46f86a77a8941279ca9135b733161f3187041d430"}</signedData>
    <publicKey encoding="plain">3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254</publicKey>
  </value>
  <value transactionId="1" context="Transaction.End">
    <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1520200007","GV":"1.7:97B4:505A, d939f6f","PG":"T2065","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1520200007","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2021-01-01T10:05:33,000+0100 S","TX":"E","RV":150,"RI":"1-0:1.8.0*198","RU":"Wh","XV":14590,"XI":"1-0:1.8.0*255","XU":"Wh","RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"304502206557e44b012431b80b603390d6ed5381b5c774e823b8dd99c078d25b5c04a20d022100ca14532a0185ba0feb0a9f60949d33bc682bc786e8bbd8df174cab2668e4160f"}</signedData>
    <publicKey encoding="plain">3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254</publicKey>
  </value>
</values>
```

This data (saved as [`ev-charging-ocmf.xml`](data/ev-charging-ocmf.xml)) can be
successfully verified with [S.A.F.E. e.V.
Transparenzsoftware](https://www.safe-ev.de/de/transparenzsoftware.php) by
loading it into the application and cliking on _Transaktion überprüfen_:

![S.A.F.E. e.V. Transparenzsoftware Main Window](img/ev-charging-verification-overview.png)
![S.A.F.E. e.V. Transparenzsoftware Verification Details](img/ev-charging-verification-detail.png)
