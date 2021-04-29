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

where _12345678abcdef_ is meant to be the identification from a RFID
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

This example uses the snapshot pair  _Signed Turn-On Snapshot_ and _Signed
Turn-Off Snapshot_ which switches an external contactor. Use the pair _Signed
Start Snapshot_ and _Signed End Snapshot_ in analog in case the meter does not
control an external contactor. See [Signed Snapshots](snapshots.md) for more
details.


#### Creating the _Signed Turn-On Snapshot_

Create and read the _Signed Turn-On Snapshot_ as follows:
```
$ bsmtool get-snapshot stons
bsm_snapshot:
    fixed:
        Typ: 1
        St: 0
        RCR: None
        TotWhImp: 88200 Wh
        W: 0.0 W
        MA1: 001BZR1521070003
        RCnt: 22107
        OS: 1829766 s
        Epoch: 1602145359 s
        TZO: 120 min
        EpochSetCnt: 12174
        EpochSetOS: 1829734 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 304502201a40c702753d715cc37e5aabbf706ed409e1aa01f8f19996b192a3276adecd72022100a4818e85690f00946c56569b92453ad9bf118fa3ae2a636629cdb8b89123f041
```
```
--> 2a 10 9f4a 0001 02 0002 ac03
<-- 2a 10 9f4a 0001 0810
--> 2a 03 9f49 0064 bdf8
<-- 2a 03 c8 000100000000000000015888000000000001303031425a52313532313037303030330000565b001beb865f7ecc4f007800002f8e001beb660001000063686172676549542075702031322a342c2069643a2031323334353637386162636465660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 3d9d
--> 2a 03 9fad 007d 3c05
<-- 2a 03 fa 64656d6f206461746120320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300047304502201a40c702753d715cc37e5aabbf706ed409e1aa01f8f19996b192a3276adecd72022100a4818e 2eb6
--> 2a 03 a02a 001b 0012
<-- 2a 03 36 85690f00946c56569b92453ad9bf118fa3ae2a636629cdb8b89123f04100000000000000000000000000000000000000000000000000 1ba4
```

#### Key Start Snapshot Data Points

Let's have a quick look at its key data points:

- Type and status
    - This is a [_Signed Turn-On
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L6) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L80)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L131)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) which will show
      the energy consumption at the end has been reset to zero
    - [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L193) gives the
      total energy consumption tracked by this meter and could be used for
      computing the energy consumption of the actual charging process as the
      delta between start and end
    - It was taken with no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L201) = 0 Wh) as it
      should be the case with the contactor turned off
- Time and counters
    - Let's remember the response counter
      [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L214) 22,107 for later
    - It has valid time information in _Epoch_ and _TZO_
- Metadata points _Meta1_ and _Meta2_ contain the previously set metadata


#### Start Snapshot Register Dump

The register dump (protocol addresses) of the start snapshot looks as follows:
```
$ bsmtool dump 40775 254
   40775: fd85 00fc 0001 0000 0000 0000 0001 5888  ..............X.
   40783: 0000 0000 0001 3030 3142 5a52 3135 3231  ......001BZR1521
   40791: 3037 3030 3033 0000 565b 001b eb86 5f7e  070003..V[...._~
   40799: cc4f 0078 0000 2f8e 001b eb66 0001 0000  .O.x../....f....
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
   40975: 0000 0000 0000 0000 0030 0047 3045 0220  .........0.G0E.
   40983: 1a40 c702 753d 715c c37e 5aab bf70 6ed4  .@..u=q\.~Z..pn.
   40991: 09e1 aa01 f8f1 9996 b192 a327 6ade cd72  ...........'j..r
   40999: 0221 00a4 818e 8569 0f00 946c 5656 9b92  .!.....i...lVV..
   41007: 453a d9bf 118f a3ae 2a63 6629 cdb8 b891  E:......*cf)....
   41015: 23f0 4100 0000 0000 0000 0000 0000 0000  #.A.............
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
$ bsmtool get ostons/o | cut -d \| -f 2 | jq .
{
  "FV": "1.0",
  "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
  "GS": "001BZR1521070003",
  "GV": "1.8:33C4:DB63, 08d1aa3",
  "PG": "T22107",
  "MV": "BAUER Electronic",
  "MM": "BSM-WS36A-H01-1311-0000",
  "MS": "001BZR1521070003",
  "IS": true,
  "IT": "UNDEFINED",
  "ID": "chargeIT up 12*4, id: 12345678abcdef",
  "RD": [
    {
      "TM": "2020-10-08T10:22:39,000+0200 S",
      "TX": "B",
      "RV": 0,
      "RI": "1-0:1.8.0*198",
      "RU": "Wh",
      "XV": 88200,
      "XI": "1-0:1.8.0*255",
      "XU": "Wh",
      "XT": 1,
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
$ bsmtool dump 42291 500
   42291: fd87 01f2 0001 0000 4f43 4d46 7c7b 2246  ........OCMF|{"F
   42299: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   42307: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic
   42315: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   42323: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   42331: 3031 425a 5231 3532 3130 3730 3030 3322  01BZR1521070003"
   42339: 2c22 4756 223a 2231 2e38 3a33 3343 343a  ,"GV":"1.8:33C4:
   42347: 4442 3633 2c20 3038 6431 6161 3322 2c22  DB63, 08d1aa3","
   42355: 5047 223a 2254 3232 3130 3722 2c22 4d56  PG":"T22107","MV
   42363: 223a 2242 4155 4552 2045 6c65 6374 726f  ":"BAUER Electro
   42371: 6e69 6322 2c22 4d4d 223a 2242 534d 2d57  nic","MM":"BSM-W
   42379: 5333 3641 2d48 3031 2d31 3331 312d 3030  S36A-H01-1311-00
   42387: 3030 222c 224d 5322 3a22 3030 3142 5a52  00","MS":"001BZR
   42395: 3135 3231 3037 3030 3033 222c 2249 5322  1521070003","IS"
   42403: 3a74 7275 652c 2249 5422 3a22 554e 4445  :true,"IT":"UNDE
   42411: 4649 4e45 4422 2c22 4944 223a 2263 6861  FINED","ID":"cha
   42419: 7267 6549 5420 7570 2031 322a 342c 2069  rgeIT up 12*4, i
   42427: 643a 2031 3233 3435 3637 3861 6263 6465  d: 12345678abcde
   42435: 6622 2c22 5244 223a 5b7b 2254 4d22 3a22  f","RD":[{"TM":"
   42443: 3230 3230 2d31 302d 3038 5431 303a 3232  2020-10-08T10:22
   42451: 3a33 392c 3030 302b 3032 3030 2053 222c  :39,000+0200 S",
   42459: 2254 5822 3a22 4222 2c22 5256 223a 302c  "TX":"B","RV":0,
   42467: 2252 4922 3a22 312d 303a 312e 382e 302a  "RI":"1-0:1.8.0*
   42475: 3139 3822 2c22 5255 223a 2257 6822 2c22  198","RU":"Wh","
   42483: 5856 223a 3838 3230 302c 2258 4922 3a22  XV":88200,"XI":"
   42491: 312d 303a 312e 382e 302a 3235 3522 2c22  1-0:1.8.0*255","
   42499: 5855 223a 2257 6822 2c22 5854 223a 312c  XU":"Wh","XT":1,
   42507: 2252 5422 3a22 4143 222c 2245 4622 3a22  "RT":"AC","EF":"
   42515: 222c 2253 5422 3a22 4722 7d5d 7d7c 7b22  ","ST":"G"}]}|{"
   42523: 5341 223a 2245 4344 5341 2d73 6563 7032  SA":"ECDSA-secp2
   42531: 3536 7231 2d53 4841 3235 3622 2c22 5344  56r1-SHA256","SD
   42539: 223a 2233 3034 3530 3232 3030 3563 6533  ":"3045022005ce3
   42547: 6638 6163 6132 3930 3530 6364 3963 6134  f8aca29050cd9ca4
   42555: 3466 6164 6462 3337 6461 6433 3739 3464  4faddb37dad3794d
   42563: 3963 3464 6365 3730 3162 6436 3361 6134  9c4dce701bd63aa4
   42571: 6463 3239 6632 3636 3333 3430 3232 3130  dc29f26633402210
   42579: 3064 3163 3233 3166 3837 3065 3766 3831  0d1c231f870e7f81
   42587: 3565 3033 3762 6336 6666 3861 6363 6336  5e037bc6ff8accc6
   42595: 3966 3966 6366 3738 3364 3266 6239 6539  9f9fcf783d2fb9e9
   42603: 3063 3838 6664 3163 3962 6432 3066 6434  0c88fd1c9bd20fd4
   42611: 6222 7d00 0000 0000 0000 0000 0000 0000  b"}.............
   42619: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42627: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42635: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42643: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42651: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42659: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42667: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42675: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42683: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42691: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42699: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42707: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42715: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42723: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42731: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42739: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42747: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42755: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42763: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42771: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42779: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42787: 0000 0000 0000 0000                      ........
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
the contactor and recoding the snapshot data. Again, [Snapshot Creation](snapshots.md#snapshot-creation) gives
the details about this procedure.


#### Creating the Signed Turn-Off Snapshot

Creating and reading the _Signed Turn-Off Snapshot_ works in analog to
[creating the _Signed Turn-On Snapshot_](#creating-the-signed-turn-on-snapshot)
and as follows:
```
$ bsmtool get-snapshot stoffs
bsm_snapshot:
    fixed:
        Typ: 2
        St: 0
        RCR: 150 Wh
        TotWhImp: 88350 Wh
        W: 0.0 W
        MA1: 001BZR1521070003
        RCnt: 22108
        OS: 1830064 s
        Epoch: 1602145657 s
        TZO: 120 min
        EpochSetCnt: 12174
        EpochSetOS: 1829734 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 3045022100d7070dc074c9188ec1b957cb7a6b3a37d0c416b3c9f9eb49c01087c4a95e16e9022025aaee48fa55f93ed507d7565458fdfa118b1aa73632055401a9e324e1f28a20
```
```
--> 2a 10 a048 0001 02 0002 62e2
<-- 2a 10 a048 0001 a5c4
--> 2a 03 a047 0064 d02f
<-- 2a 03 c8 00020000000000960001591e000000000001303031425a52313532313037303030330000565c001becb05f7ecd79007800002f8e001beb660001000063686172676549542075702031322a342c2069643a2031323334353637386162636465660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 1dd7
--> 2a 03 a0ab 007d d010
<-- 2a 03 fa 64656d6f2064617461203200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000473045022100d7070dc074c9188ec1b957cb7a6b3a37d0c416b3c9f9eb49c01087c4a95e16e9022025aaee df95
--> 2a 03 a128 001b a02e
<-- 2a 03 36 48fa55f93ed507d7565458fdfa118b1aa73632055401a9e324e1f28a2000000000000000000000000000000000000000000000000000 c57e
```


#### Key End Snapshot Data Points

Let's look one more time at the snapshot's key data points and compare them to
the _Signed Turn-On Snapshot_ taken at the start of charging:

- Type and status
    - This is a [_Signed Turn-Off
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L7) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L80)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L131)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) started at zero
      and now shows the energy delivered during this charging process: 150 Wh
    - The total energy delivered,
      [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L193), increased
      from 88,200 Wh to 88,350 Wh which gives a consumption of 150 Wh. Due to
      the [internal state of _TotWhImp_](snapshots.md#energy-and-power) this
      difference can be one least significant digit larger than the value for
      _RCR_ (shown in the display).
    - Again, there is no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L201) = 0 Wh) since
      power delivery got cut before recording the snapshot data
- Time and counters
    - The response counter
      [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L214) is 22,108 - one
    - It has valid time information in _Epoch_ and _TZO_
    - [_EpochSetCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L241) (with a
      value of 12,174) and
      [_EpochSetOS_](../../bauer_bsm/bsm/models/smdx_64901.xml#L246) (with a
      value of 1,829,734) are the same as in the start snapshot. So they are
      using the same time base originating from this same setting of time.
- Metadata is still the same as in _Signed Turn-On Snapshot_


#### End Snapshot Register Dump

The register dump of the end snapshot looks as follows
```
$ bsmtool dump 41029 254
   41029: fd85 00fc 0002 0000 0000 0096 0001 591e  ..............Y.
   41037: 0000 0000 0001 3030 3142 5a52 3135 3231  ......001BZR1521
   41045: 3037 3030 3033 0000 565c 001b ecb0 5f7e  070003..V\...._~
   41053: cd79 0078 0000 2f8e 001b eb66 0001 0000  .y.x../....f....
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
   41229: 0000 0000 0000 0000 0030 0047 3045 0221  .........0.G0E.!
   41237: 00d7 070d c074 c918 8ec1 b957 cb7a 6b3a  .....t.....W.zk:
   41245: 37d0 c416 b3c9 f9eb 49c0 1087 c4a9 5e16  7.......I.....^.
   41253: e902 2025 aaee 48fa 55f9 3ed5 07d7 5654  .. %..H.U.>...VT
   41261: 58fd fa11 8b1a a736 3205 5401 a9e3 24e1  X......62.T...$.
   41269: f28a 2000 0000 0000 0000 0000 0000 0000  .. .............
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
    O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070003","GV":"1.8:33C4:DB63, 08d1aa3","PG":"T22108","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070003","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2020-10-08T10:27:37,000+0200 S","TX":"E","RV":150,"RI":"1-0:1.8.0*198","RU":"Wh","XV":88350,"XI":"1-0:1.8.0*255","XU":"Wh","XT":2,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3046022100fa544eb800c940b30a87d2c075a0797e5089092b77a47f76433e63cb06c8832d022100e0e3c8370e19b8ef4caf295e3f676b43b12e092507ee81edc8cc7b9b2c9569bb"}
```
```
--> 2a 03 a729 0002 30ac
<-- 2a 03 04 00020000 c0f1
--> 2a 03 a72b 007d d08c
<-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353231303730303033222c224756223a22312e383a333343343a444236332c2030386431616133222c225047223a22543232313038222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353231303730303033222c224953223a747275652c224954223a22554e444546494e4544222c224944223a226368617267 4687
--> 2a 03 a7a8 007d 2164
<-- 2a 03 fa 6549542075702031322a342c2069643a203132333435363738616263646566222c225244223a5b7b22544d223a22323032302d31302d30385431303a32373a33372c3030302b303230302053222c225458223a2245222c225256223a3135302c225249223a22312d303a312e382e302a313938222c225255223a225768222c225856223a38383335302c225849223a22312d303a312e382e302a323535222c225855223a225768222c225854223a322c225254223a224143222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a2233303436303232 9961
--> 2a 03 a825 007d b25b
<-- 2a 03 fa 3130306661353434656238303063393430623330613837643263303735613037393765353038393039326237376134376637363433336536336362303663383833326430323231303065306533633833373065313962386566346361663239356533663637366234336231326530393235303765653831656463386363376239623263393536396262227d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 e2cf
--> 2a 03 a8a2 0079 03b1
<-- 2a 03 f2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 443c
```


#### Key End OCMF Values

[Pretty-printed](ocmf.md#ocmf-json-payload), the _OCMF Signed Turn-Off
Snapshot_ looks as follows:
```json
$ bsmtool get ostons/o | cut -d \| -f 2 | jq .
{
  "FV": "1.0",
  "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
  "GS": "001BZR1521070003",
  "GV": "1.8:33C4:DB63, 08d1aa3",
  "PG": "T22108",
  "MV": "BAUER Electronic",
  "MM": "BSM-WS36A-H01-1311-0000",
  "MS": "001BZR1521070003",
  "IS": true,
  "IT": "UNDEFINED",
  "ID": "chargeIT up 12*4, id: 12345678abcdef",
  "RD": [
    {
      "TM": "2020-10-08T10:27:37,000+0200 S",
      "TX": "E",
      "RV": 150,
      "RI": "1-0:1.8.0*198",
      "RU": "Wh",
      "XV": 88350,
      "XI": "1-0:1.8.0*255",
      "XU": "Wh",
      "XT": 2,
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
    - The response counter _PG_ (prefixed with _T_) gives the value 22,108 and
      is the successor of the start response counter
    - Epoch time information is given in ISO 8601 format
- The identification data _ID_ taken from _Meta1_ has the same value as in the
  start OCMF data


#### End OCMF Register Dump

The register dump of the end snapshot's OCMF representation looks as follows:
```
$ bsmtool dump 42791 500
   42791: fd87 01f2 0002 0000 4f43 4d46 7c7b 2246  ........OCMF|{"F
   42799: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   42807: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic 
   42815: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   42823: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   42831: 3031 425a 5231 3532 3130 3730 3030 3322  01BZR1521070003"
   42839: 2c22 4756 223a 2231 2e38 3a33 3343 343a  ,"GV":"1.8:33C4:
   42847: 4442 3633 2c20 3038 6431 6161 3322 2c22  DB63, 08d1aa3","
   42855: 5047 223a 2254 3232 3130 3822 2c22 4d56  PG":"T22108","MV
   42863: 223a 2242 4155 4552 2045 6c65 6374 726f  ":"BAUER Electro
   42871: 6e69 6322 2c22 4d4d 223a 2242 534d 2d57  nic","MM":"BSM-W
   42879: 5333 3641 2d48 3031 2d31 3331 312d 3030  S36A-H01-1311-00
   42887: 3030 222c 224d 5322 3a22 3030 3142 5a52  00","MS":"001BZR
   42895: 3135 3231 3037 3030 3033 222c 2249 5322  1521070003","IS"
   42903: 3a74 7275 652c 2249 5422 3a22 554e 4445  :true,"IT":"UNDE
   42911: 4649 4e45 4422 2c22 4944 223a 2263 6861  FINED","ID":"cha
   42919: 7267 6549 5420 7570 2031 322a 342c 2069  rgeIT up 12*4, i
   42927: 643a 2031 3233 3435 3637 3861 6263 6465  d: 12345678abcde
   42935: 6622 2c22 5244 223a 5b7b 2254 4d22 3a22  f","RD":[{"TM":"
   42943: 3230 3230 2d31 302d 3038 5431 303a 3237  2020-10-08T10:27
   42951: 3a33 372c 3030 302b 3032 3030 2053 222c  :37,000+0200 S",
   42959: 2254 5822 3a22 4522 2c22 5256 223a 3135  "TX":"E","RV":15
   42967: 302c 2252 4922 3a22 312d 303a 312e 382e  0,"RI":"1-0:1.8.
   42975: 302a 3139 3822 2c22 5255 223a 2257 6822  0*198","RU":"Wh"
   42983: 2c22 5856 223a 3838 3335 302c 2258 4922  ,"XV":88350,"XI"
   42991: 3a22 312d 303a 312e 382e 302a 3235 3522  :"1-0:1.8.0*255"
   42999: 2c22 5855 223a 2257 6822 2c22 5854 223a  ,"XU":"Wh","XT":
   43007: 322c 2252 5422 3a22 4143 222c 2245 4622  2,"RT":"AC","EF"
   43015: 3a22 222c 2253 5422 3a22 4722 7d5d 7d7c  :"","ST":"G"}]}|
   43023: 7b22 5341 223a 2245 4344 5341 2d73 6563  {"SA":"ECDSA-sec
   43031: 7032 3536 7231 2d53 4841 3235 3622 2c22  p256r1-SHA256","
   43039: 5344 223a 2233 3034 3630 3232 3130 3066  SD":"3046022100f
   43047: 6135 3434 6562 3830 3063 3934 3062 3330  a544eb800c940b30
   43055: 6138 3764 3263 3037 3561 3037 3937 6535  a87d2c075a0797e5
   43063: 3038 3930 3932 6237 3761 3437 6637 3634  089092b77a47f764
   43071: 3333 6536 3363 6230 3663 3838 3332 6430  33e63cb06c8832d0
   43079: 3232 3130 3065 3065 3363 3833 3730 6531  22100e0e3c8370e1
   43087: 3962 3865 6634 6361 6632 3935 6533 6636  9b8ef4caf295e3f6
   43095: 3736 6234 3362 3132 6530 3932 3530 3765  76b43b12e092507e
   43103: 6538 3165 6463 3863 6337 6239 6232 6339  e81edc8cc7b9b2c9
   43111: 3536 3962 6222 7d00 0000 0000 0000 0000  569bb"}.........
   43119: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43127: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43135: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43143: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43151: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43159: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43167: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43175: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43183: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43191: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43199: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43207: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43215: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43223: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43231: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43239: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43247: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43255: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43263: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43271: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43279: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43287: 0000 0000 0000 0000                      ........
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
$ bsmtool ocmf-xml ostons ostoffs
<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<values>
  <value transactionId="1" context="Transaction.Begin">
    <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070003","GV":"1.8:33C4:DB63, 08d1aa3","PG":"T22107","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070003","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2020-10-08T10:22:39,000+0200 S","TX":"B","RV":0,"RI":"1-0:1.8.0*198","RU":"Wh","XV":88200,"XI":"1-0:1.8.0*255","XU":"Wh","XT":1,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3045022005ce3f8aca29050cd9ca44faddb37dad3794d9c4dce701bd63aa4dc29f266334022100d1c231f870e7f815e037bc6ff8accc69f9fcf783d2fb9e90c88fd1c9bd20fd4b"}</signedData>
    <publicKey encoding="plain">3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254</publicKey>
  </value>
  <value transactionId="1" context="Transaction.End">
    <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070003","GV":"1.8:33C4:DB63, 08d1aa3","PG":"T22108","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070003","IS":true,"IT":"UNDEFINED","ID":"chargeIT up 12*4, id: 12345678abcdef","RD":[{"TM":"2020-10-08T10:27:37,000+0200 S","TX":"E","RV":150,"RI":"1-0:1.8.0*198","RU":"Wh","XV":88350,"XI":"1-0:1.8.0*255","XU":"Wh","XT":2,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3046022100fa544eb800c940b30a87d2c075a0797e5089092b77a47f76433e63cb06c8832d022100e0e3c8370e19b8ef4caf295e3f676b43b12e092507ee81edc8cc7b9b2c9569bb"}</signedData>
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
